from enum import IntEnum


class DispatchOutcome(IntEnum):
    """Outcome of running an operation against a single account."""

    SUCCESS = 1
    SKIPPED = 2
    FAILED = 3
