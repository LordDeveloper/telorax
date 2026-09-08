from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import func, or_, select

from telorax.core.enums import AccountState, OperationState, OperationType
from telorax.domain.entities import Account, Operation
from telorax.domain.interfaces.repositories import AccountRepository, OperationRepository
from telorax.infrastructure.database import models as schema

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


def _to_account(row: schema.Account) -> Account:
    return Account(
        id=row.id,
        msisdn=row.msisdn,
        session_ciphertext=row.session_ciphertext,
        state=AccountState(row.state),
        country_iso=row.country_iso,
        telegram_user_id=row.telegram_user_id,
        telegram_username=row.telegram_username,
        display_name=row.display_name,
        telegram_app_id=row.telegram_app_id,
        telegram_app_hash=row.telegram_app_hash,
        two_factor_secret=row.two_factor_secret,
        reliability_score=row.reliability_score,
        rate_limited_until=row.rate_limited_until,
        restricted_until=row.restricted_until,
        last_online_at=row.last_online_at,
        two_factor_confirmed_at=row.two_factor_confirmed_at,
        foreign_sessions_revoked_at=row.foreign_sessions_revoked_at,
        last_engaged_at=row.last_engaged_at,
        account_ttl_configured=row.account_ttl_configured,
        proxy_label=row.proxy_label,
        notes=row.notes,
        provisioned_at=row.provisioned_at,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


def _normalize_target(target: str | int) -> str:
    return str(target)


def _parse_target(target: str) -> str | int:
    return int(target) if target.isdigit() else target


def _to_operation(row: schema.Operation) -> Operation:
    return Operation(
        id=row.id,
        type=OperationType(row.operation_type),
        quantity=row.quantity,
        completed=row.completed,
        target=_parse_target(row.target),
        extra=row.extra or {},
        state=OperationState(row.state),
        fingerprint=row.fingerprint,
        retry_attempts=row.retry_attempts,
        country=row.country,
        failure_summary=row.failure_summary,
        scheduled_at=row.scheduled_at,
        started_at=row.started_at,
        finished_at=row.finished_at,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


class SQLAlchemyAccountRepository(AccountRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, account_id: int) -> Account | None:
        row = await self._session.get(schema.Account, account_id)
        return _to_account(row) if row else None

    async def get_by_msisdn(self, msisdn: int) -> Account | None:
        result = await self._session.execute(
            select(schema.Account).where(schema.Account.msisdn == msisdn),
        )
        row = result.scalar_one_or_none()
        return _to_account(row) if row else None

    async def list_operational(
        self,
        *,
        limit: int,
        country_iso: str | None = None,
    ) -> list[Account]:
        now = datetime.now(tz=UTC)
        query = (
            select(schema.Account)
            .where(schema.Account.state == AccountState.ACTIVE.value)
            .where(
                or_(
                    schema.Account.rate_limited_until.is_(None),
                    schema.Account.rate_limited_until < now,
                ),
            )
            .order_by(schema.Account.reliability_score.desc())
            .limit(limit)
        )
        if country_iso:
            query = query.where(schema.Account.country_iso == country_iso)
        result = await self._session.execute(query)
        return [_to_account(row) for row in result.scalars()]

    async def update_state(self, account_id: int, state: AccountState) -> None:
        row = await self._session.get(schema.Account, account_id)
        if row:
            row.state = state.value

    async def update_reliability_score(self, account_id: int, score: int) -> None:
        row = await self._session.get(schema.Account, account_id)
        if row:
            row.reliability_score = score

    async def create(self, account: Account) -> Account:
        row = schema.Account(
            msisdn=account.msisdn,
            session_ciphertext=account.session_ciphertext,
            state=account.state.value,
            country_iso=account.country_iso,
            telegram_user_id=account.telegram_user_id,
            telegram_username=account.telegram_username,
            display_name=account.display_name,
            telegram_app_id=account.telegram_app_id,
            telegram_app_hash=account.telegram_app_hash,
            two_factor_secret=account.two_factor_secret,
            reliability_score=account.reliability_score,
            proxy_label=account.proxy_label,
            notes=account.notes,
            provisioned_at=account.provisioned_at,
            two_factor_confirmed_at=account.two_factor_confirmed_at,
            foreign_sessions_revoked_at=account.foreign_sessions_revoked_at,
        )
        self._session.add(row)
        await self._session.flush()
        return _to_account(row)

    async def list_accounts(
        self,
        *,
        state: AccountState | None = None,
        country_iso: str | None = None,
        limit: int,
        offset: int,
    ) -> list[Account]:
        query = select(schema.Account).order_by(schema.Account.id.desc()).limit(limit).offset(offset)
        if state is not None:
            query = query.where(schema.Account.state == state.value)
        if country_iso:
            query = query.where(schema.Account.country_iso == country_iso)
        result = await self._session.execute(query)
        return [_to_account(row) for row in result.scalars()]

    async def count_accounts(
        self,
        *,
        state: AccountState | None = None,
        country_iso: str | None = None,
    ) -> int:
        query = select(func.count()).select_from(schema.Account)
        if state is not None:
            query = query.where(schema.Account.state == state.value)
        if country_iso:
            query = query.where(schema.Account.country_iso == country_iso)
        result = await self._session.execute(query)
        return int(result.scalar_one())

    async def count_by_state(self) -> dict[AccountState, int]:
        result = await self._session.execute(
            select(schema.Account.state, func.count())
            .group_by(schema.Account.state),
        )
        return {AccountState(state): int(count) for state, count in result.all()}

    async def update(self, account: Account) -> Account:
        row = await self._session.get(schema.Account, account.id)
        if row is None:
            msg = f'Account {account.id} not found'
            raise ValueError(msg)
        row.msisdn = account.msisdn
        row.session_ciphertext = account.session_ciphertext
        row.state = account.state.value
        row.country_iso = account.country_iso
        row.telegram_user_id = account.telegram_user_id
        row.telegram_username = account.telegram_username
        row.display_name = account.display_name
        row.telegram_app_id = account.telegram_app_id
        row.telegram_app_hash = account.telegram_app_hash
        row.two_factor_secret = account.two_factor_secret
        row.reliability_score = account.reliability_score
        row.rate_limited_until = account.rate_limited_until
        row.restricted_until = account.restricted_until
        row.last_online_at = account.last_online_at
        row.two_factor_confirmed_at = account.two_factor_confirmed_at
        row.foreign_sessions_revoked_at = account.foreign_sessions_revoked_at
        row.last_engaged_at = account.last_engaged_at
        row.account_ttl_configured = account.account_ttl_configured
        row.proxy_label = account.proxy_label
        row.notes = account.notes
        row.provisioned_at = account.provisioned_at
        await self._session.flush()
        return _to_account(row)


class SQLAlchemyOperationRepository(OperationRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, operation_id: int) -> Operation | None:
        row = await self._session.get(schema.Operation, operation_id)
        return _to_operation(row) if row else None

    async def list_queued(self, *, limit: int) -> list[Operation]:
        result = await self._session.execute(
            select(schema.Operation)
            .where(schema.Operation.state == OperationState.QUEUED.value)
            .order_by(schema.Operation.id.asc())
            .limit(limit),
        )
        return [_to_operation(row) for row in result.scalars()]

    async def create(self, operation: Operation) -> Operation:
        row = schema.Operation(
            operation_type=operation.type.value,
            quantity=operation.quantity,
            completed=operation.completed,
            target=_normalize_target(operation.target),
            extra=operation.extra,
            state=operation.state.value,
            fingerprint=operation.fingerprint,
            country=operation.country,
        )
        self._session.add(row)
        await self._session.flush()
        return _to_operation(row)

    async def update_fulfillment(
        self,
        operation_id: int,
        *,
        completed: int,
        state: OperationState,
    ) -> None:
        row = await self._session.get(schema.Operation, operation_id)
        if row:
            row.completed = completed
            row.state = state.value
