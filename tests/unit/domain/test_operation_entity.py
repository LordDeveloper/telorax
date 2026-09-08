from __future__ import annotations

from telorax.core.enums import OperationState, OperationType
from telorax.domain.entities import Operation


def test_operation_remaining() -> None:
    operation = Operation(
        id=1,
        type=OperationType.VIEW,
        quantity=100,
        completed=37,
        target='@test',
        extra={},
    )
    assert operation.remaining == 63
    assert operation.is_complete is False


def test_operation_progress_ratio() -> None:
    operation = Operation(
        id=1,
        type=OperationType.SUBSCRIBE,
        quantity=10,
        completed=0,
        target='@channel',
        extra={},
        state=OperationState.QUEUED,
    )
    assert operation.progress_ratio == 0.0


def test_operation_is_complete_when_quantity_reached() -> None:
    operation = Operation(
        id=1,
        type=OperationType.REACTION,
        quantity=50,
        completed=50,
        target='@channel',
        extra={},
        state=OperationState.COMPLETED,
    )
    assert operation.is_complete is True
    assert operation.remaining == 0
    assert operation.progress_ratio == 1.0
