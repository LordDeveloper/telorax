from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from telorax.domain.interfaces.repositories import UnitOfWork
from telorax.infrastructure.database.repositories.sqlalchemy_campaign_dispatch import (
    SQLAlchemyCampaignDispatchRepository,
)


class SQLAlchemyUnitOfWork(UnitOfWork):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory
        self._session: AsyncSession | None = None
        self._dispatches: SQLAlchemyCampaignDispatchRepository | None = None

    async def __aenter__(self) -> SQLAlchemyUnitOfWork:
        self._session = self._session_factory()
        await self._session.__aenter__()
        self._dispatches = SQLAlchemyCampaignDispatchRepository(self._session)
        return self

    async def __aexit__(self, *args: object) -> None:
        if self._session:
            await self._session.__aexit__(*args)

    async def commit(self) -> None:
        if self._session:
            await self._session.commit()

    async def rollback(self) -> None:
        if self._session:
            await self._session.rollback()

    @property
    def campaign_dispatches(self) -> SQLAlchemyCampaignDispatchRepository:
        if self._dispatches is None:
            msg = 'UnitOfWork not entered'
            raise RuntimeError(msg)
        return self._dispatches
