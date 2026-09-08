from __future__ import annotations

from telorax.core.enums import CampaignState, EngagementKind
from telorax.domain.entities import Campaign


def test_campaign_remaining_count() -> None:
    campaign = Campaign(
        id=1,
        engagement_kind=EngagementKind.VIEW,
        target_count=100,
        fulfilled_count=37,
        target_spec={'peer_ref': '@test'},
    )
    assert campaign.remaining_count == 63
    assert campaign.is_fulfilled is False
    assert campaign.progress_ratio == 0.37


def test_campaign_dispatch_key_requires_fingerprint() -> None:
    campaign = Campaign(
        id=1,
        engagement_kind=EngagementKind.SUBSCRIBE,
        target_count=10,
        fulfilled_count=0,
        target_spec={'peer_ref': '@channel'},
    )
    try:
        campaign.dispatch_key_for(42)
        raise AssertionError('expected ValueError')
    except ValueError:
        pass


def test_campaign_is_fulfilled_when_target_reached() -> None:
    campaign = Campaign(
        id=2,
        engagement_kind=EngagementKind.REACTION,
        target_count=50,
        fulfilled_count=50,
        target_spec={},
        state=CampaignState.COMPLETED,
    )
    assert campaign.is_fulfilled is True
    assert campaign.remaining_count == 0
