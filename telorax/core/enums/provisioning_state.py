from enum import IntEnum


class ProvisioningState(IntEnum):
    QUEUED = 1
    CLAIMED = 2
    COMPLETED = 3
    FAILED = 4
    CANCELLED = 5
