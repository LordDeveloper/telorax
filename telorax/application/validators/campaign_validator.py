from __future__ import annotations

from typing import Any

from telorax.application.dto.campaign import CreateCampaignDTO
from telorax.core.enums import EngagementKind
from telorax.core.exceptions import CampaignValidationError


def validate_create_campaign(dto: CreateCampaignDTO) -> None:
    if dto.target_count <= 0:
        raise CampaignValidationError('target_count must be greater than zero')

    if not dto.target_spec:
        raise CampaignValidationError('target_spec is required')

    if dto.engagement_kind in {
        EngagementKind.VIEW,
        EngagementKind.SUBSCRIBE,
        EngagementKind.REACTION,
        EngagementKind.SPONSORED,
        EngagementKind.SEARCH_VIEW,
        EngagementKind.BUTTON_CLICK,
        EngagementKind.BOT_START,
    } and 'peer_ref' not in dto.target_spec:
        raise CampaignValidationError('target_spec.peer_ref is required for this engagement kind')

    if dto.engagement_kind == EngagementKind.POLL_VOTE and 'option' not in dto.target_spec:
        raise CampaignValidationError('target_spec.option is required for POLL_VOTE campaigns')

    _validate_target_spec_values(dto.target_spec)


def _validate_target_spec_values(target_spec: dict[str, Any]) -> None:
    peer_ref = target_spec.get('peer_ref')
    if peer_ref is not None and not isinstance(peer_ref, (str, int)):
        raise CampaignValidationError('target_spec.peer_ref must be a string or integer')
