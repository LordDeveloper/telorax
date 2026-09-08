from __future__ import annotations

from dataclasses import asdict
from typing import Any

from fastapi import APIRouter, HTTPException, Query

from telorax.api.dependencies import CampaignServiceDep
from telorax.application.dto.campaign import CreateCampaignDTO
from telorax.core.enums import EngagementKind
from telorax.core.exceptions import CampaignValidationError

router = APIRouter(prefix='/campaigns', tags=['campaigns'])


def _parse_engagement_kind(value: object) -> EngagementKind:
    if isinstance(value, EngagementKind):
        return value
    if isinstance(value, int):
        return EngagementKind(value)
    if isinstance(value, str):
        return EngagementKind[value.upper()]
    msg = 'engagement_kind must be an integer or enum name'
    raise CampaignValidationError(msg)


@router.get('/queued')
async def list_queued_campaigns(
    campaign_service: CampaignServiceDep,
    limit: int = Query(default=50, ge=1, le=500),
) -> list[dict[str, Any]]:
    campaigns = await campaign_service.list_queued(limit=limit)
    return [asdict(campaign) for campaign in campaigns]


@router.get('/{campaign_id}')
async def get_campaign(
    campaign_id: int,
    campaign_service: CampaignServiceDep,
) -> dict[str, Any]:
    campaign = await campaign_service.get_campaign(campaign_id)
    if campaign is None:
        raise HTTPException(status_code=404, detail='Campaign not found')
    return asdict(campaign)


@router.post('', status_code=201)
async def create_campaign(
    payload: dict[str, Any],
    campaign_service: CampaignServiceDep,
) -> dict[str, Any]:
    dto = CreateCampaignDTO(
        engagement_kind=_parse_engagement_kind(payload['engagement_kind']),
        target_count=int(payload['target_count']),
        target_spec=dict(payload['target_spec']),
        priority=int(payload.get('priority', 0)),
        country_filter=payload.get('country_filter'),
        source_label=payload.get('source_label'),
    )
    try:
        campaign = await campaign_service.create_campaign(dto)
    except CampaignValidationError as exc:
        raise HTTPException(status_code=422, detail=exc.message) from exc
    return asdict(campaign)
