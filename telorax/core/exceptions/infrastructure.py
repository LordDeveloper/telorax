from telorax.core.exceptions.base import TeloraxError


class InfrastructureError(TeloraxError):
    """External system failure."""


class DatabaseConnectionError(InfrastructureError):
    pass


class RedisConnectionError(InfrastructureError):
    pass


class TelegramConnectionError(InfrastructureError):
    pass
