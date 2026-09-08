from __future__ import annotations

from telorax.core.enums import EngagementKind, OperationState
from telorax.domain.entities import Operation


def test_operation_remaining_count() -> None:
    operation = Operation(
        id=1,
        engagement_kind=EngagementKind.VIEW,
        target_count=100,
        fulfilled_count=37,
        target_spec={'peer_ref': '@test'},
    )
    assert operation.remaining_count == 63
    assert operation.is_fulfilled is False
    assert operation.progress_ratio == 0.37


def test_operation_dispatch_key_requires_fingerprint() -> None:
    operation = Operation(
        id=1,
        engagement_kind=EngagementKind.SUBSCRIBE,
        target_count=10,
        fulfilled_count=0,
        target_spec={'peer_ref': '@channel'},
    )
    try:
        operation.dispatch_key_for(42)
        raise AssertionError('expected ValueError')
    except ValueError:
        pass


def test_operation_is_fulfilled_when_target_reached() -> None:
    operation = Operation(
        id=2,
        engagement_kind=EngagementKind.REACTION,
        target_count=50,
        fulfilled_count=50,
        target_spec={},
        state=OperationState.COMPLETED,
    )
    assert operation.is_fulfilled is True
    assert operation.remaining_count == 0
