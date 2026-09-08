from enum import IntEnum


class OperationState(IntEnum):
    """Lifecycle state of an operation."""

    DRAFT = 1
    QUEUED = 2
    RUNNING = 3
    PAUSED = 4
    COMPLETED = 5
    FAILED = 6
    CANCELLED = 7
