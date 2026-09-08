from enum import IntEnum


class DispatchOutcome(IntEnum):
    """نتیجه اجرای campaign روی یک account."""

    SUCCESS = 1
    SKIPPED = 2
    FAILED = 3
