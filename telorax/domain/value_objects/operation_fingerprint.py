from __future__ import annotations

import hashlib
import json
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from telorax.core.enums import OperationType

_TRANSIENT_EXTRA_KEYS = frozenset({
    'failure_reason',
    'reaction',
    'leave_after_days',
    'read_history',
    'preflight_view',
    'members_only',
    'search_query',
    'impression_count',
})


def build_operation_fingerprint(
    operation_type: OperationType,
    target: str | int,
    extra: dict[str, Any],
) -> str:
    """Stable hash for dedup using only structurally relevant fields."""
    normalized_extra = {
        key: value
        for key, value in extra.items()
        if key not in _TRANSIENT_EXTRA_KEYS
    }
    normalized = {
        'type': int(operation_type),
        'target': target,
        'extra': normalized_extra,
    }
    encoded = json.dumps(normalized, sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(encoded.encode()).hexdigest()
