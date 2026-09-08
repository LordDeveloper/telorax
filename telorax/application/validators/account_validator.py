from __future__ import annotations

from telorax.application.dto.account import UpdateAccountDTO
from telorax.core.enums import AccountState
from telorax.core.exceptions import OperationValidationError


def validate_update_account(dto: UpdateAccountDTO) -> None:
    if all(
        value is None
        for value in (dto.state, dto.notes, dto.proxy_label, dto.reliability_score)
    ):
        msg = 'At least one field must be provided'
        raise OperationValidationError(msg)

    if dto.reliability_score is not None and not 0 <= dto.reliability_score <= 100:
        msg = 'reliability_score must be between 0 and 100'
        raise OperationValidationError(msg)


def parse_account_state(value: object) -> AccountState:
    if isinstance(value, AccountState):
        return value
    if isinstance(value, int):
        return AccountState(value)
    if isinstance(value, str):
        return AccountState[value.upper()]
    msg = 'state must be a valid AccountState name or code'
    raise OperationValidationError(msg)
