from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from telorax.application.dto.account import (
    AccountDetailDTO,
    AccountListDTO,
    AccountStatsDTO,
    AccountSummaryDTO,
    ImportSessionDTO,
    ImportSessionResultDTO,
    UpdateAccountDTO,
)
from telorax.application.validators.account_validator import validate_update_account
from telorax.core.enums import AccountState
from telorax.core.exceptions import AccountImportError, AccountNotFoundError, InvalidSessionError
from telorax.domain.entities import Account
from telorax.infrastructure.database.repositories.unit_of_work import SQLAlchemyUnitOfWork
from telorax.infrastructure.security.session_cipher import SessionCipher
from telorax.infrastructure.telegram.session_importer import SessionImporter, SessionImportOptions

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

    from telorax.core.config.settings import Settings


class AccountService:
    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        settings: Settings,
    ) -> None:
        self._session_factory = session_factory
        self._settings = settings
        self._cipher = SessionCipher(
            settings.master_key.get_secret_value() if settings.master_key else None,
        )
        self._importer = SessionImporter(settings)

    async def get_account(self, account_id: int) -> AccountDetailDTO | None:
        async with SQLAlchemyUnitOfWork(self._session_factory) as unit_of_work:
            account = await unit_of_work.accounts.get_by_id(account_id)
            return _to_detail(account) if account else None

    async def list_accounts(
        self,
        *,
        state: AccountState | None = None,
        country_iso: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> AccountListDTO:
        async with SQLAlchemyUnitOfWork(self._session_factory) as unit_of_work:
            accounts = await unit_of_work.accounts.list_accounts(
                state=state,
                country_iso=country_iso,
                limit=limit,
                offset=offset,
            )
            total = await unit_of_work.accounts.count_accounts(
                state=state,
                country_iso=country_iso,
            )
        return AccountListDTO(
            items=tuple(_to_summary(account) for account in accounts),
            total=total,
            limit=limit,
            offset=offset,
        )

    async def list_operational(
        self,
        *,
        limit: int,
        country_iso: str | None = None,
    ) -> list[AccountSummaryDTO]:
        async with SQLAlchemyUnitOfWork(self._session_factory) as unit_of_work:
            accounts = await unit_of_work.accounts.list_operational(
                limit=limit,
                country_iso=country_iso,
            )
            return [_to_summary(account) for account in accounts]

    async def get_stats(self) -> AccountStatsDTO:
        async with SQLAlchemyUnitOfWork(self._session_factory) as unit_of_work:
            by_state = await unit_of_work.accounts.count_by_state()
            total = sum(by_state.values())
        operational = by_state.get(AccountState.ACTIVE, 0)
        return AccountStatsDTO(
            total=total,
            by_state={state.name: count for state, count in by_state.items()},
            operational=operational,
        )

    async def update_account(self, account_id: int, dto: UpdateAccountDTO) -> AccountDetailDTO:
        validate_update_account(dto)
        async with SQLAlchemyUnitOfWork(self._session_factory) as unit_of_work:
            account = await unit_of_work.accounts.get_by_id(account_id)
            if account is None:
                raise AccountNotFoundError(account_id)
            updated = _apply_update(account, dto)
            saved = await unit_of_work.accounts.update(updated)
            await unit_of_work.commit()
            return _to_detail(saved)

    async def deactivate_account(self, account_id: int) -> AccountDetailDTO:
        return await self.update_account(
            account_id,
            UpdateAccountDTO(state=AccountState.DEACTIVATED),
        )

    async def import_session(
        self,
        content: bytes,
        dto: ImportSessionDTO,
    ) -> ImportSessionResultDTO:
        options = SessionImportOptions(
            password=dto.password,
            ignore_revoke=dto.ignore_revoke,
            ignore_2fa=dto.ignore_2fa,
            renew=dto.renew,
        )
        try:
            imported = await self._importer.import_file(content, options)
        except (InvalidSessionError, AccountImportError):
            raise

        now = datetime.now(tz=UTC)
        encrypted_session = self._cipher.encrypt(imported.session_string)
        async with SQLAlchemyUnitOfWork(self._session_factory) as unit_of_work:
            existing = await unit_of_work.accounts.get_by_msisdn(imported.msisdn)
            created = existing is None
            if created:
                account = Account(
                    id=0,
                    msisdn=imported.msisdn,
                    session_ciphertext=encrypted_session,
                    state=AccountState.ACTIVE,
                    country_iso=imported.country_iso,
                    telegram_user_id=imported.telegram_user_id,
                    telegram_username=imported.telegram_username,
                    display_name=imported.display_name,
                    telegram_app_id=imported.telegram_app_id,
                    telegram_app_hash=imported.telegram_app_hash,
                    two_factor_secret=imported.two_factor_secret,
                    provisioned_at=now,
                    two_factor_confirmed_at=now if imported.ignore_2fa else None,
                    foreign_sessions_revoked_at=now if imported.ignore_revoke else None,
                )
                saved = await unit_of_work.accounts.create(account)
            else:
                account = Account(
                    id=existing.id,
                    msisdn=imported.msisdn,
                    session_ciphertext=encrypted_session,
                    state=AccountState.ACTIVE,
                    country_iso=imported.country_iso or existing.country_iso,
                    telegram_user_id=imported.telegram_user_id,
                    telegram_username=imported.telegram_username,
                    display_name=imported.display_name,
                    telegram_app_id=imported.telegram_app_id,
                    telegram_app_hash=imported.telegram_app_hash,
                    two_factor_secret=imported.two_factor_secret or existing.two_factor_secret,
                    reliability_score=existing.reliability_score,
                    rate_limited_until=existing.rate_limited_until,
                    restricted_until=existing.restricted_until,
                    last_online_at=existing.last_online_at,
                    two_factor_confirmed_at=(
                        now if imported.ignore_2fa else existing.two_factor_confirmed_at
                    ),
                    foreign_sessions_revoked_at=(
                        now if imported.ignore_revoke else existing.foreign_sessions_revoked_at
                    ),
                    last_engaged_at=existing.last_engaged_at,
                    account_ttl_configured=existing.account_ttl_configured,
                    proxy_label=existing.proxy_label,
                    notes=existing.notes,
                    provisioned_at=existing.provisioned_at,
                    created_at=existing.created_at,
                    updated_at=existing.updated_at,
                )
                saved = await unit_of_work.accounts.update(account)
            await unit_of_work.commit()
        return ImportSessionResultDTO(account=_to_detail(saved), created=created)


def _apply_update(account: Account, dto: UpdateAccountDTO) -> Account:
    return Account(
        id=account.id,
        msisdn=account.msisdn,
        session_ciphertext=account.session_ciphertext,
        state=dto.state if dto.state is not None else account.state,
        country_iso=account.country_iso,
        telegram_user_id=account.telegram_user_id,
        telegram_username=account.telegram_username,
        display_name=account.display_name,
        telegram_app_id=account.telegram_app_id,
        telegram_app_hash=account.telegram_app_hash,
        two_factor_secret=account.two_factor_secret,
        reliability_score=(
            dto.reliability_score
            if dto.reliability_score is not None
            else account.reliability_score
        ),
        rate_limited_until=account.rate_limited_until,
        restricted_until=account.restricted_until,
        last_online_at=account.last_online_at,
        two_factor_confirmed_at=account.two_factor_confirmed_at,
        foreign_sessions_revoked_at=account.foreign_sessions_revoked_at,
        last_engaged_at=account.last_engaged_at,
        account_ttl_configured=account.account_ttl_configured,
        proxy_label=dto.proxy_label if dto.proxy_label is not None else account.proxy_label,
        notes=dto.notes if dto.notes is not None else account.notes,
        provisioned_at=account.provisioned_at,
        created_at=account.created_at,
        updated_at=account.updated_at,
    )


def _to_summary(account: Account) -> AccountSummaryDTO:
    return AccountSummaryDTO(
        id=account.id,
        msisdn=account.msisdn,
        state=account.state,
        country_iso=account.country_iso,
        reliability_score=account.reliability_score,
        is_operational=account.is_operational,
    )


def _to_detail(account: Account) -> AccountDetailDTO:
    return AccountDetailDTO(
        id=account.id,
        msisdn=account.msisdn,
        state=account.state,
        country_iso=account.country_iso,
        telegram_user_id=account.telegram_user_id,
        telegram_username=account.telegram_username,
        display_name=account.display_name,
        reliability_score=account.reliability_score,
        is_operational=account.is_operational,
        is_rate_limited=account.is_rate_limited,
        rate_limited_until=account.rate_limited_until,
        restricted_until=account.restricted_until,
        last_online_at=account.last_online_at,
        two_factor_confirmed_at=account.two_factor_confirmed_at,
        foreign_sessions_revoked_at=account.foreign_sessions_revoked_at,
        last_engaged_at=account.last_engaged_at,
        account_ttl_configured=account.account_ttl_configured,
        proxy_label=account.proxy_label,
        notes=account.notes,
        provisioned_at=account.provisioned_at,
        created_at=account.created_at,
        updated_at=account.updated_at,
    )
