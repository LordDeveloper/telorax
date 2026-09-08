from __future__ import annotations

import hashlib
import json

from telorax.core.enums import OperationType
from telorax.domain.value_objects.operation_fingerprint import build_operation_fingerprint


def test_fingerprint_is_stable_for_same_input() -> None:
    extra = {'message_ids': [42]}
    first = build_operation_fingerprint(OperationType.VIEW, '@channel', extra)
    second = build_operation_fingerprint(OperationType.VIEW, '@channel', extra)
    assert first == second


def test_fingerprint_ignores_transient_extra_keys() -> None:
    extra = {'message_ids': [42]}
    with_transient = {**extra, 'failure_reason': 'timeout', 'search_query': 'foo'}
    baseline = build_operation_fingerprint(OperationType.VIEW, '@channel', extra)
    with_transient_fp = build_operation_fingerprint(
        OperationType.VIEW,
        '@channel',
        with_transient,
    )
    assert baseline == with_transient_fp


def test_fingerprint_differs_by_operation_type() -> None:
    extra = {'message_ids': [42]}
    view = build_operation_fingerprint(OperationType.VIEW, '@channel', extra)
    poll = build_operation_fingerprint(
        OperationType.POLL_VOTE,
        '@channel',
        {**extra, 'option': 1},
    )
    assert view != poll


def test_fingerprint_normalization() -> None:
    extra = {'message_ids': [1]}
    normalized = {'type': int(OperationType.VIEW), 'target': 123, 'extra': extra}
    encoded = json.dumps(normalized, sort_keys=True, separators=(',', ':'))
    expected = hashlib.sha256(encoded.encode()).hexdigest()
    assert build_operation_fingerprint(OperationType.VIEW, 123, extra) == expected
