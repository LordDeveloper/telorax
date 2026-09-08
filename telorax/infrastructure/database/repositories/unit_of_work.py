from __future__ import annotations

from typing import TYPE_CHECKING

from telorax.domain.interfaces.repositories import UnitOfWork
from telorax.infrastructure.database.repositories.sqlalchemy_campaign_dispatch import (
    SQLAlchemyCampaignDispatchRepository,
)
from telorax.infrastructure.database.repositories.sqlalchemy_channel_membership import (
    SQLAlchemyChannelMembershipRepository,
)
from telorax.infrastructure.database.repositories.sqlalchemy_repositories import (
    SQLAlchemyCampaignRepository,
    SQLAlchemyTelegramAccountRepository,
)

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


class SQLAlchemyUnitOfWork(UnitOfWork):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory
        self._session: AsyncSession | None = None
        self._accounts: SQLAlchemyTelegramAccountRepository | None = None
        self._campaigns: SQLAlchemyCampaignRepository | None = None
        self._memberships: SQLAlchemyChannelMembershipRepository | None = None
        self._dispatches: SQLAlchemyCampaignDispatchRepository | None = None

    async def __aenter__(self) -> SQLAlchemyUnitOfWork:
        self._session = self._session_factory()
        await self._session.__aenter__()
        self._accounts = SQLAlchemyTelegramAccountRepository(self._session)
        self._campaigns = SQLAlchemyCampaignRepository(self._session)
        self._memberships = SQLAlchemyChannelMembershipRepository(self._session)
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
    def telegram_accounts(self) -> SQLAlchemyTelegramAccountRepository:
        if self._accounts is None:
            msg = 'UnitOfWork not entered: telegram_accounts'
            raise RuntimeError(msg)
        return self._accounts

    @property
    def campaigns(self) -> SQLAlchemyCampaignRepository:
        if self._campaigns is None:
            msg = 'UnitOfWork not entered: campaigns'
            raise RuntimeError(msg)
        return self._campaigns

    @property
    def channel_memberships(self) -> SQLAlchemyChannelMembershipRepository:
        if self._memberships is None:
            msg = 'UnitOfWork not entered: channel_memberships'
            raise RuntimeError(msg)
        return self._memberships

    @property
    def campaign_dispatches(self) -> SQLAlchemyCampaignDispatchRepository:
        if self._dispatches is None:
            msg = 'UnitOfWork not entered: campaign_dispatches'
            raise RuntimeError(msg)
        return self._dispatches
