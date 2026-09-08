from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import select

from telorax.domain.interfaces.repositories import OperationDispatchRepository
from telorax.infrastructure.database.models import OperationDispatchModel

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from telorax.domain.entities import OperationDispatch


class SQLAlchemyOperationDispatchRepository(OperationDispatchRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def exists(self, operation_id: int, account_id: int) -> bool:
        result = await self._session.execute(
            select(OperationDispatchModel).where(
                OperationDispatchModel.operation_id == operation_id,
                OperationDispatchModel.account_id == account_id,
            ),
        )
        return result.scalar_one_or_none() is not None

    async def record(self, dispatch: OperationDispatch) -> None:
        self._session.add(
            OperationDispatchModel(
                operation_id=dispatch.operation_id,
                account_id=dispatch.account_id,
                outcome=dispatch.outcome.value,
                error_code=dispatch.error_code,
                dispatched_at=dispatch.dispatched_at,
            ),
        )
