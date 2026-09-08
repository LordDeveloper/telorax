from telorax.core.exceptions.base import TeloraxError


class DomainError(TeloraxError):
    """Business rule violation."""


class OperationValidationError(DomainError):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class EngagementExecutionError(DomainError):
    def __init__(self, message: str, *, code: str = 'execution_failed') -> None:
        super().__init__(message)
        self.message = message
        self.code = code


class UnsupportedOperationTypeError(DomainError):
    def __init__(self, operation_type: str) -> None:
        super().__init__(f'Unsupported operation type: {operation_type}')
        self.operation_type = operation_type


class TargetNotFoundError(DomainError):
    def __init__(self, operation_id: int, target_ref: str) -> None:
        super().__init__(f'Target {target_ref} not found for operation {operation_id}')
        self.operation_id = operation_id
        self.target_ref = target_ref


class InvalidReactionError(DomainError):
    def __init__(self, reaction: str) -> None:
        super().__init__(f'Invalid reaction: {reaction}')
        self.reaction = reaction


class AlreadySubscribedError(DomainError):
    pass


class TargetInaccessibleError(DomainError):
    pass
