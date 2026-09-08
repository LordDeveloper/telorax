from __future__ import annotations

import pytest

from telorax.application.dto.operation import CreateOperationDTO
from telorax.application.validators.operation_validator import validate_create_operation
from telorax.core.enums import OperationType
from telorax.core.exceptions import OperationValidationError


def test_validate_create_operation_requires_quantity() -> None:
    dto = CreateOperationDTO(
        type=OperationType.VIEW,
        quantity=0,
        target='@channel',
        extra={},
    )
    with pytest.raises(OperationValidationError, match='quantity'):
        validate_create_operation(dto)


def test_validate_create_operation_requires_target() -> None:
    dto = CreateOperationDTO(
        type=OperationType.VIEW,
        quantity=10,
        target='',
        extra={},
    )
    with pytest.raises(OperationValidationError, match='target'):
        validate_create_operation(dto)


def test_validate_create_operation_requires_poll_option() -> None:
    dto = CreateOperationDTO(
        type=OperationType.POLL_VOTE,
        quantity=10,
        target='@channel',
        extra={},
    )
    with pytest.raises(OperationValidationError, match='extra.option'):
        validate_create_operation(dto)


def test_validate_create_operation_rejects_invalid_target_type() -> None:
    dto = CreateOperationDTO(
        type=OperationType.VIEW,
        quantity=10,
        target=['bad'],  # type: ignore[arg-type]
        extra={},
    )
    with pytest.raises(OperationValidationError, match='target'):
        validate_create_operation(dto)


def test_validate_create_operation_accepts_valid_payload() -> None:
    dto = CreateOperationDTO(
        type=OperationType.VIEW,
        quantity=10,
        target='@channel',
        extra={'message_ids': [1, 2]},
    )
    validate_create_operation(dto)
