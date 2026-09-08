from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import or_, select

from telorax.core.enums import AccountState, OperationState, OperationType
from telorax.domain.entities import Account, Operation
from telorax.domain.interfaces.repositories import AccountRepository, OperationRepository
from telorax.infrastructure.database.models import AccountModel, OperationModel

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


def _to_account(model: AccountModel) -> Account:
    return Account(
        id=model.id,
        msisdn=model.msisdn,
        session_ciphertext=model.session_ciphertext,
        state=AccountState(model.state),
        country_iso=model.country_iso,
        telegram_user_id=model.telegram_user_id,
        telegram_username=model.telegram_username,
        display_name=model.display_name,
        telegram_app_id=model.telegram_app_id,
        telegram_app_hash=model.telegram_app_hash,
        two_factor_secret=model.two_factor_secret,
        reliability_score=model.reliability_score,
        rate_limited_until=model.rate_limited_until,
        restricted_until=model.restricted_until,
        last_online_at=model.last_online_at,
        two_factor_confirmed_at=model.two_factor_confirmed_at,
        foreign_sessions_revoked_at=model.foreign_sessions_revoked_at,
        last_engaged_at=model.last_engaged_at,
        account_ttl_configured=model.account_ttl_configured,
        proxy_label=model.proxy_label,
        notes=model.notes,
        provisioned_at=model.provisioned_at,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def _normalize_target(target: str | int) -> str:
    return str(target)


def _parse_target(target: str) -> str | int:
    return int(target) if target.isdigit() else target


def _to_operation(model: OperationModel) -> Operation:
    return Operation(
        id=model.id,
        type=OperationType(model.operation_type),
        quantity=model.quantity,
        completed=model.completed,
        target=_parse_target(model.target),
        extra=model.extra or {},
        state=OperationState(model.state),
        fingerprint=model.fingerprint,
        retry_attempts=model.retry_attempts,
        country=model.country,
        failure_summary=model.failure_summary,
        scheduled_at=model.scheduled_at,
        started_at=model.started_at,
        finished_at=model.finished_at,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


class SQLAlchemyAccountRepository(AccountRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, account_id: int) -> Account | None:
        model = await self._session.get(AccountModel, account_id)
        return _to_account(model) if model else None

    async def get_by_msisdn(self, msisdn: int) -> Account | None:
        result = await self._session.execute(
            select(AccountModel).where(AccountModel.msisdn == msisdn),
        )
        model = result.scalar_one_or_none()
        return _to_account(model) if model else None

    async def list_operational(
        self,
        *,
        limit: int,
        country_iso: str | None = None,
    ) -> list[Account]:
        now = datetime.now(tz=UTC)
        query = (
            select(AccountModel)
            .where(AccountModel.state == AccountState.ACTIVE.value)
            .where(
                or_(
                    AccountModel.rate_limited_until.is_(None),
                    AccountModel.rate_limited_until < now,
                ),
            )
            .order_by(AccountModel.reliability_score.desc())
            .limit(limit)
        )
        if country_iso:
            query = query.where(AccountModel.country_iso == country_iso)
        result = await self._session.execute(query)
        return [_to_account(model) for model in result.scalars()]

    async def update_state(self, account_id: int, state: AccountState) -> None:
        model = await self._session.get(AccountModel, account_id)
        if model:
            model.state = state.value

    async def update_reliability_score(self, account_id: int, score: int) -> None:
        model = await self._session.get(AccountModel, account_id)
        if model:
            model.reliability_score = score

    async def create(self, account: Account) -> Account:
        model = AccountModel(
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
        )
        self._session.add(model)
        await self._session.flush()
        return _to_account(model)


class SQLAlchemyOperationRepository(OperationRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, operation_id: int) -> Operation | None:
        model = await self._session.get(OperationModel, operation_id)
        return _to_operation(model) if model else None

    async def list_queued(self, *, limit: int) -> list[Operation]:
        result = await self._session.execute(
            select(OperationModel)
            .where(OperationModel.state == OperationState.QUEUED.value)
            .order_by(OperationModel.id.asc())
            .limit(limit),
        )
        return [_to_operation(model) for model in result.scalars()]

    async def create(self, operation: Operation) -> Operation:
        model = OperationModel(
            operation_type=operation.type.value,
            quantity=operation.quantity,
            completed=operation.completed,
            target=_normalize_target(operation.target),
            extra=operation.extra,
            state=operation.state.value,
            fingerprint=operation.fingerprint,
            country=operation.country,
        )
        self._session.add(model)
        await self._session.flush()
        return _to_operation(model)

    async def update_fulfillment(
        self,
        operation_id: int,
        *,
        completed: int,
        state: OperationState,
    ) -> None:
        model = await self._session.get(OperationModel, operation_id)
        if model:
            model.completed = completed
            model.state = state.value
