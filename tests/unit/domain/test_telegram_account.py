from __future__ import annotations

from datetime import UTC, datetime, timedelta

from telorax.core.enums import AccountState
from telorax.domain.entities import TelegramAccount


def test_is_operational_only_for_active_state() -> None:
    active = TelegramAccount(id=1, msisdn=1, session_ciphertext='x', state=AccountState.ACTIVE)
    standby = TelegramAccount(id=2, msisdn=2, session_ciphertext='x', state=AccountState.STANDBY)
    assert active.is_operational is True
    assert standby.is_operational is False


def test_is_rate_limited_false_when_not_set() -> None:
    account = TelegramAccount(id=1, msisdn=1, session_ciphertext='x')
    assert account.is_rate_limited is False


def test_is_rate_limited_true_for_future_timestamp() -> None:
    account = TelegramAccount(
        id=1,
        msisdn=1,
        session_ciphertext='x',
        rate_limited_until=datetime.now(tz=UTC) + timedelta(hours=1),
    )
    assert account.is_rate_limited is True


def test_is_rate_limited_supports_naive_datetime() -> None:
    account = TelegramAccount(
        id=1,
        msisdn=1,
        session_ciphertext='x',
        rate_limited_until=datetime.now(tz=UTC).replace(tzinfo=None) + timedelta(hours=1),
    )
    assert account.is_rate_limited is True
