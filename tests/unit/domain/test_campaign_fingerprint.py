from __future__ import annotations

import hashlib
import json

from telorax.core.enums import EngagementKind
from telorax.domain.value_objects.campaign_fingerprint import build_campaign_fingerprint


def test_fingerprint_is_deterministic() -> None:
    target_spec = {'peer_ref': '@channel', 'message_ids': [42]}
    first = build_campaign_fingerprint(EngagementKind.VIEW, target_spec)
    second = build_campaign_fingerprint(EngagementKind.VIEW, target_spec)
    assert first == second


def test_fingerprint_excludes_transient_fields() -> None:
    base = {'peer_ref': '@channel', 'message_ids': [42]}
    with_transient = {**base, 'failure_reason': 'timeout', 'country_filter': 'IR'}
    assert build_campaign_fingerprint(EngagementKind.VIEW, base) == build_campaign_fingerprint(
        EngagementKind.VIEW,
        with_transient,
    )


def test_fingerprint_differs_by_engagement_kind() -> None:
    target_spec = {'peer_ref': '@channel', 'message_ids': [42]}
    view = build_campaign_fingerprint(EngagementKind.VIEW, target_spec)
    vote = build_campaign_fingerprint(
        EngagementKind.POLL_VOTE,
        {**target_spec, 'poll_option': 1},
    )
    assert view != vote
    assert len(view) == 64


def test_fingerprint_is_sha256() -> None:
    target_spec = {'peer_ref': 123, 'message_ids': [1]}
    normalized = {'peer_ref': 123, 'message_ids': [1], 'engagement_kind': int(EngagementKind.VIEW)}
    expected = hashlib.sha256(
        json.dumps(normalized, sort_keys=True, separators=(',', ':')).encode(),
    ).hexdigest()
    assert build_campaign_fingerprint(EngagementKind.VIEW, target_spec) == expected
