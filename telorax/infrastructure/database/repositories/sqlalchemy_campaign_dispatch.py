from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from telorax.domain.entities import CampaignDispatch
from telorax.domain.interfaces.repositories import CampaignDispatchRepository
from telorax.infrastructure.database.models import CampaignDispatchModel


class SQLAlchemyCampaignDispatchRepository(CampaignDispatchRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def exists(self, campaign_id: int, account_id: int) -> bool:
        result = await self._session.execute(
            select(CampaignDispatchModel).where(
                CampaignDispatchModel.campaign_id == campaign_id,
                CampaignDispatchModel.account_id == account_id,
            ),
        )
        return result.scalar_one_or_none() is not None

    async def record(self, dispatch: CampaignDispatch) -> None:
        self._session.add(
            CampaignDispatchModel(
                campaign_id=dispatch.campaign_id,
                account_id=dispatch.account_id,
                outcome=dispatch.outcome.value,
                error_code=dispatch.error_code,
                dispatched_at=dispatch.dispatched_at,
            ),
        )
