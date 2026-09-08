from __future__ import annotations

from telorax.core.exceptions import (
    AccountRateLimitedError,
    DatabaseConnectionError,
    OperationValidationError,
    TargetNotFoundError,
    TeloraxError,
)


def test_domain_exceptions_expose_message() -> None:
    validation = OperationValidationError('bad operation')
    assert validation.message == 'bad operation'
    assert str(validation) == 'bad operation'


def test_account_and_infrastructure_exceptions() -> None:
    assert isinstance(AccountRateLimitedError(123, wait_seconds=30), TeloraxError)
    assert isinstance(DatabaseConnectionError('db'), TeloraxError)


def test_target_not_found_error_fields() -> None:
    error = TargetNotFoundError(operation_id=9, target_ref='@missing')
    assert error.operation_id == 9
    assert error.target_ref == '@missing'
