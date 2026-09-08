from __future__ import annotations

import pytest

from telorax.application.dto.campaign import CreateCampaignDTO
from telorax.application.validators.campaign_validator import validate_create_campaign
from telorax.core.enums import EngagementKind
from telorax.core.exceptions import CampaignValidationError


def test_validate_create_campaign_requires_target_count() -> None:
    dto = CreateCampaignDTO(
        engagement_kind=EngagementKind.VIEW,
        target_count=0,
        target_spec={'peer_ref': '@channel'},
    )
    with pytest.raises(CampaignValidationError):
        validate_create_campaign(dto)


def test_validate_create_campaign_requires_peer_ref() -> None:
    dto = CreateCampaignDTO(
        engagement_kind=EngagementKind.VIEW,
        target_count=10,
        target_spec={},
    )
    with pytest.raises(CampaignValidationError):
        validate_create_campaign(dto)


def test_validate_create_campaign_requires_poll_option() -> None:
    dto = CreateCampaignDTO(
        engagement_kind=EngagementKind.POLL_VOTE,
        target_count=10,
        target_spec={'peer_ref': '@channel'},
    )
    with pytest.raises(CampaignValidationError):
        validate_create_campaign(dto)


def test_validate_create_campaign_rejects_invalid_peer_ref_type() -> None:
    dto = CreateCampaignDTO(
        engagement_kind=EngagementKind.VIEW,
        target_count=10,
        target_spec={'peer_ref': ['bad']},
    )
    with pytest.raises(CampaignValidationError):
        validate_create_campaign(dto)


def test_validate_create_campaign_accepts_valid_payload() -> None:
    dto = CreateCampaignDTO(
        engagement_kind=EngagementKind.VIEW,
        target_count=10,
        target_spec={'peer_ref': '@channel'},
    )
    validate_create_campaign(dto)
