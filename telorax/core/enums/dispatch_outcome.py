from enum import IntEnum


class DispatchOutcome(IntEnum):
    """Outcome of running a campaign against a single account."""

    SUCCESS = 1
    SKIPPED = 2
    FAILED = 3
