from __future__ import annotations

import hashlib
import json
from typing import Any

from telorax.core.enums import EngagementKind

_TRANSIENT_SPEC_KEYS = frozenset({
    'failure_reason',
    'reaction',
    'option',
    'leave_after_days',
    'read_history',
    'preflight_view',
    'members_only',
    'country_filter',
    'search_query',
    'impression_count',
})


def build_campaign_fingerprint(
    engagement_kind: EngagementKind,
    target_spec: dict[str, Any],
) -> str:
    """Hash پایدار برای dedup — فقط فیلدهای structurally relevant."""
    normalized = {
        key: value
        for key, value in target_spec.items()
        if key not in _TRANSIENT_SPEC_KEYS
    }
    normalized['engagement_kind'] = int(engagement_kind)
    encoded = json.dumps(normalized, sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(encoded.encode()).hexdigest()
