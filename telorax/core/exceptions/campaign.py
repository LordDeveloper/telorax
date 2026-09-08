from telorax.core.exceptions.base import TeloraxError


class DomainError(TeloraxError):
    """Business rule violation."""


class CampaignValidationError(DomainError):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class EngagementExecutionError(DomainError):
    def __init__(self, message: str, *, code: str = 'execution_failed') -> None:
        super().__init__(message)
        self.message = message
        self.code = code


class UnsupportedEngagementKindError(DomainError):
    def __init__(self, engagement_kind: str) -> None:
        super().__init__(f'Unsupported engagement kind: {engagement_kind}')
        self.engagement_kind = engagement_kind


class TargetNotFoundError(DomainError):
    def __init__(self, campaign_id: int, target_ref: str) -> None:
        super().__init__(f'Target {target_ref} not found for campaign {campaign_id}')
        self.campaign_id = campaign_id
        self.target_ref = target_ref


class InvalidReactionError(DomainError):
    def __init__(self, reaction: str) -> None:
        super().__init__(f'Invalid reaction: {reaction}')
        self.reaction = reaction


class AlreadySubscribedError(DomainError):
    pass


class TargetInaccessibleError(DomainError):
    pass
