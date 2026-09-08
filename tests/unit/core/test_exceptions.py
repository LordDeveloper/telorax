from __future__ import annotations

from telorax.core.exceptions import (
    AccountRateLimitedError,
    CampaignValidationError,
    DatabaseConnectionError,
    TargetNotFoundError,
    TeloraxError,
)


def test_domain_exceptions_expose_message() -> None:
    validation = CampaignValidationError('bad campaign')
    assert validation.message == 'bad campaign'
    assert str(validation) == 'bad campaign'


def test_account_and_infrastructure_exceptions() -> None:
    assert isinstance(AccountRateLimitedError(123, wait_seconds=30), TeloraxError)
    assert isinstance(DatabaseConnectionError('db'), TeloraxError)


def test_target_not_found_error_fields() -> None:
    error = TargetNotFoundError(campaign_id=9, target_ref='@missing')
    assert error.campaign_id == 9
    assert error.target_ref == '@missing'
