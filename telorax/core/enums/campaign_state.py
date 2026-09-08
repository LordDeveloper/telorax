from enum import IntEnum


class CampaignState(IntEnum):
    """وضعیت lifecycle یک campaign."""

    FAILED = -1
    CANCELLED = 0
    COMPLETED = 1
    QUEUED = 2
    RUNNING = 3
