from __future__ import annotations

import pytest

from telorax.application.dto.operation import CreateOperationDTO
from telorax.application.validators.operation_validator import validate_create_operation
from telorax.core.enums import EngagementKind
from telorax.core.exceptions import OperationValidationError


def test_validate_create_operation_requires_target_count() -> None:
    dto = CreateOperationDTO(
        engagement_kind=EngagementKind.VIEW,
        target_count=0,
        target_spec={'peer_ref': '@channel'},
    )
    with pytest.raises(OperationValidationError):
        validate_create_operation(dto)


def test_validate_create_operation_requires_peer_ref() -> None:
    dto = CreateOperationDTO(
        engagement_kind=EngagementKind.VIEW,
        target_count=10,
        target_spec={},
    )
    with pytest.raises(OperationValidationError):
        validate_create_operation(dto)


def test_validate_create_operation_requires_poll_option() -> None:
    dto = CreateOperationDTO(
        engagement_kind=EngagementKind.POLL_VOTE,
        target_count=10,
        target_spec={'peer_ref': '@channel'},
    )
    with pytest.raises(OperationValidationError):
        validate_create_operation(dto)


def test_validate_create_operation_rejects_invalid_peer_ref_type() -> None:
    dto = CreateOperationDTO(
        engagement_kind=EngagementKind.VIEW,
        target_count=10,
        target_spec={'peer_ref': ['bad']},
    )
    with pytest.raises(OperationValidationError):
        validate_create_operation(dto)


def test_validate_create_operation_accepts_valid_payload() -> None:
    dto = CreateOperationDTO(
        engagement_kind=EngagementKind.VIEW,
        target_count=10,
        target_spec={'peer_ref': '@channel'},
    )
    validate_create_operation(dto)
