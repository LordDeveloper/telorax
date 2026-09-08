from __future__ import annotations

from telorax.application.dto.operation import CreateOperationDTO
from telorax.core.enums import OperationType
from telorax.core.exceptions import OperationValidationError
from telorax.domain.value_objects.operation_extra import parse_operation_extra

_TARGET_REQUIRED_TYPES = {
    OperationType.VIEW,
    OperationType.SUBSCRIBE,
    OperationType.POLL_VOTE,
    OperationType.REACTION,
    OperationType.SPONSORED,
    OperationType.SEARCH_VIEW,
    OperationType.BUTTON_CLICK,
    OperationType.BOT_START,
}


_ISO_COUNTRY_CODE_LEN = 2


def validate_create_operation(dto: CreateOperationDTO) -> None:
    if dto.quantity <= 0:
        raise OperationValidationError('quantity must be greater than zero')

    if dto.type in _TARGET_REQUIRED_TYPES and dto.target in ('', None):
        raise OperationValidationError('target is required for this operation type')

    if not isinstance(dto.target, (str, int)):
        raise OperationValidationError('target must be a string or integer')

    if isinstance(dto.target, str) and not dto.target.strip():
        raise OperationValidationError('target must not be empty')

    if dto.extra is None:
        raise OperationValidationError('extra is required')

    if dto.country is not None and (
        not isinstance(dto.country, str) or len(dto.country) != _ISO_COUNTRY_CODE_LEN
    ):
        raise OperationValidationError('country must be a 2-letter ISO code')

    parse_operation_extra(dto.type, dict(dto.extra))
