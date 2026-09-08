from __future__ import annotations

from typing import TYPE_CHECKING

from telorax.domain.interfaces.repositories import UnitOfWork
from telorax.infrastructure.database.repositories.sqlalchemy_membership import (
    SQLAlchemyMembershipRepository,
)
from telorax.infrastructure.database.repositories.sqlalchemy_operation_dispatch import (
    SQLAlchemyOperationDispatchRepository,
)
from telorax.infrastructure.database.repositories.sqlalchemy_repositories import (
    SQLAlchemyAccountRepository,
    SQLAlchemyOperationRepository,
)

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


class SQLAlchemyUnitOfWork(UnitOfWork):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory
        self._session: AsyncSession | None = None
        self._accounts: SQLAlchemyAccountRepository | None = None
        self._operations: SQLAlchemyOperationRepository | None = None
        self._memberships: SQLAlchemyMembershipRepository | None = None
        self._dispatches: SQLAlchemyOperationDispatchRepository | None = None

    async def __aenter__(self) -> SQLAlchemyUnitOfWork:
        self._session = self._session_factory()
        await self._session.__aenter__()
        self._accounts = SQLAlchemyAccountRepository(self._session)
        self._operations = SQLAlchemyOperationRepository(self._session)
        self._memberships = SQLAlchemyMembershipRepository(self._session)
        self._dispatches = SQLAlchemyOperationDispatchRepository(self._session)
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
    def accounts(self) -> SQLAlchemyAccountRepository:
        if self._accounts is None:
            msg = 'UnitOfWork not entered: accounts'
            raise RuntimeError(msg)
        return self._accounts

    @property
    def operations(self) -> SQLAlchemyOperationRepository:
        if self._operations is None:
            msg = 'UnitOfWork not entered: operations'
            raise RuntimeError(msg)
        return self._operations

    @property
    def memberships(self) -> SQLAlchemyMembershipRepository:
        if self._memberships is None:
            msg = 'UnitOfWork not entered: memberships'
            raise RuntimeError(msg)
        return self._memberships

    @property
    def operation_dispatches(self) -> SQLAlchemyOperationDispatchRepository:
        if self._dispatches is None:
            msg = 'UnitOfWork not entered: operation_dispatches'
            raise RuntimeError(msg)
        return self._dispatches
