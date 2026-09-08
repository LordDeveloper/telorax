from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import select

from telorax.domain.interfaces.repositories import DispatchRepository
from telorax.infrastructure.database import models as schema

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from telorax.domain.entities import Dispatch


class SQLAlchemyDispatchRepository(DispatchRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def exists(self, operation_id: int, account_id: int) -> bool:
        result = await self._session.execute(
            select(schema.Dispatch).where(
                schema.Dispatch.operation_id == operation_id,
                schema.Dispatch.account_id == account_id,
            ),
        )
        return result.scalar_one_or_none() is not None

    async def record(self, dispatch: Dispatch) -> None:
        self._session.add(
            schema.Dispatch(
                operation_id=dispatch.operation_id,
                account_id=dispatch.account_id,
                outcome=dispatch.outcome.value,
                error_code=dispatch.error_code,
                dispatched_at=dispatch.dispatched_at,
            ),
        )
