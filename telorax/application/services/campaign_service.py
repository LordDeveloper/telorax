from __future__ import annotations

from typing import TYPE_CHECKING

from telorax.application.dto.campaign import CampaignSummaryDTO, CreateCampaignDTO
from telorax.application.validators.campaign_validator import validate_create_campaign
from telorax.core.enums import CampaignState
from telorax.domain.entities import Campaign
from telorax.domain.value_objects.campaign_fingerprint import build_campaign_fingerprint
from telorax.infrastructure.database.repositories.unit_of_work import SQLAlchemyUnitOfWork

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


class CampaignService:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def get_campaign(self, campaign_id: int) -> CampaignSummaryDTO | None:
        async with SQLAlchemyUnitOfWork(self._session_factory) as unit_of_work:
            campaign = await unit_of_work.campaigns.get_by_id(campaign_id)
            return _to_summary(campaign) if campaign else None

    async def list_queued(self, *, limit: int) -> list[CampaignSummaryDTO]:
        async with SQLAlchemyUnitOfWork(self._session_factory) as unit_of_work:
            campaigns = await unit_of_work.campaigns.list_queued(limit=limit)
            return [_to_summary(campaign) for campaign in campaigns]

    async def create_campaign(self, dto: CreateCampaignDTO) -> CampaignSummaryDTO:
        validate_create_campaign(dto)
        fingerprint = build_campaign_fingerprint(dto.engagement_kind, dto.target_spec)
        campaign = Campaign(
            id=0,
            engagement_kind=dto.engagement_kind,
            target_count=dto.target_count,
            fulfilled_count=0,
            target_spec=dto.target_spec,
            state=CampaignState.QUEUED,
            dedup_fingerprint=fingerprint,
            priority=dto.priority,
            country_filter=dto.country_filter,
            source_label=dto.source_label,
        )
        async with SQLAlchemyUnitOfWork(self._session_factory) as unit_of_work:
            created = await unit_of_work.campaigns.create(campaign)
            await unit_of_work.commit()
            return _to_summary(created)


def _to_summary(campaign: Campaign) -> CampaignSummaryDTO:
    return CampaignSummaryDTO(
        id=campaign.id,
        engagement_kind=campaign.engagement_kind,
        target_count=campaign.target_count,
        fulfilled_count=campaign.fulfilled_count,
        state=campaign.state.name,
        progress_ratio=campaign.progress_ratio,
        remaining_count=campaign.remaining_count,
    )
