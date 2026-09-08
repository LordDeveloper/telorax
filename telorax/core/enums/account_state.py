from enum import IntEnum


class AccountState(IntEnum):
    """وضعیت عملیاتی یک Telegram account."""

    DEACTIVATED = 0
    ACTIVE = 1
    RATE_LIMITED = 2
    STANDBY = 3
    DUPLICATE = 4
    RESTRICTED = 5
    SESSION_EXPIRED = 6
    PROVISIONING = 10
