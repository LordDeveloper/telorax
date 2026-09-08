from __future__ import annotations

from typing import TYPE_CHECKING

from telorax.application.dto.account import AccountSummaryDTO
from telorax.domain.entities import Account
from telorax.infrastructure.database.repositories.unit_of_work import SQLAlchemyUnitOfWork

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


class AccountService:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def get_account(self, account_id: int) -> AccountSummaryDTO | None:
        async with SQLAlchemyUnitOfWork(self._session_factory) as unit_of_work:
            account = await unit_of_work.accounts.get_by_id(account_id)
            return _to_summary(account) if account else None

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


def _to_summary(account: Account) -> AccountSummaryDTO:
    return AccountSummaryDTO(
        id=account.id,
        msisdn=account.msisdn,
        state=account.state,
        country_iso=account.country_iso,
        reliability_score=account.reliability_score,
        is_operational=account.is_operational,
    )
