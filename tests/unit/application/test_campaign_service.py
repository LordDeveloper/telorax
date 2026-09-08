from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from telorax.application.dto.campaign import CreateCampaignDTO
from telorax.application.services.campaign_service import CampaignService
from telorax.core.enums import CampaignState, EngagementKind
from telorax.domain.entities import Campaign


@pytest.mark.asyncio
async def test_get_campaign_returns_summary() -> None:
    campaign = Campaign(
        id=7,
        engagement_kind=EngagementKind.VIEW,
        target_count=20,
        fulfilled_count=5,
        target_spec={'peer_ref': '@test'},
        state=CampaignState.QUEUED,
        dedup_fingerprint='abc',
    )
    unit_of_work = AsyncMock()
    unit_of_work.campaigns.get_by_id = AsyncMock(return_value=campaign)
    session_factory = MagicMock()

    with patch(
        'telorax.application.services.campaign_service.SQLAlchemyUnitOfWork',
    ) as unit_of_work_cls:
        unit_of_work_cls.return_value.__aenter__ = AsyncMock(return_value=unit_of_work)
        unit_of_work_cls.return_value.__aexit__ = AsyncMock(return_value=None)
        service = CampaignService(session_factory=session_factory)
        summary = await service.get_campaign(7)

    assert summary is not None
    assert summary.id == 7
    assert summary.remaining_count == 15


@pytest.mark.asyncio
async def test_create_campaign_persists_and_commits() -> None:
    created = Campaign(
        id=3,
        engagement_kind=EngagementKind.SUBSCRIBE,
        target_count=5,
        fulfilled_count=0,
        target_spec={'peer_ref': '@channel'},
        state=CampaignState.QUEUED,
        dedup_fingerprint='hash',
    )
    unit_of_work = AsyncMock()
    unit_of_work.campaigns.create = AsyncMock(return_value=created)
    unit_of_work.commit = AsyncMock()
    session_factory = MagicMock()
    dto = CreateCampaignDTO(
        engagement_kind=EngagementKind.SUBSCRIBE,
        target_count=5,
        target_spec={'peer_ref': '@channel'},
    )

    with patch(
        'telorax.application.services.campaign_service.SQLAlchemyUnitOfWork',
    ) as unit_of_work_cls:
        unit_of_work_cls.return_value.__aenter__ = AsyncMock(return_value=unit_of_work)
        unit_of_work_cls.return_value.__aexit__ = AsyncMock(return_value=None)
        service = CampaignService(session_factory=session_factory)
        summary = await service.create_campaign(dto)

    unit_of_work.commit.assert_awaited_once()
    assert summary.id == 3
