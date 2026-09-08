from enum import IntEnum


class EngagementKind(IntEnum):
    """Kind of Telegram engagement requested by an operation."""

    VIEW = 1
    SUBSCRIBE = 2
    POLL_VOTE = 3
    REACTION = 4
    SPONSORED = 5
    SEARCH_VIEW = 6
    BUTTON_CLICK = 7
    BOT_START = 8
