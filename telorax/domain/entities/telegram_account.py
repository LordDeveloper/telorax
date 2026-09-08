from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from telorax.core.enums import AccountState


@dataclass(slots=True)
class TelegramAccount:
    """A real Telegram user account backed by a session."""

    id: int
    msisdn: int
    session_ciphertext: str
    state: AccountState = AccountState.ACTIVE
    country_iso: str | None = None
    telegram_user_id: int | None = None
    telegram_username: str | None = None
    display_name: str | None = None
    telegram_app_id: int | None = None
    telegram_app_hash: str | None = None
    two_factor_secret: str | None = None
    reliability_score: int = 100
    rate_limited_until: datetime | None = None
    restricted_until: datetime | None = None
    last_online_at: datetime | None = None
    two_factor_confirmed_at: datetime | None = None
    foreign_sessions_revoked_at: datetime | None = None
    last_engaged_at: datetime | None = None
    account_ttl_configured: bool = False
    proxy_label: str | None = None
    notes: str | None = None
    provisioned_at: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @property
    def is_operational(self) -> bool:
        return self.state == AccountState.ACTIVE

    @property
    def is_rate_limited(self) -> bool:
        if self.rate_limited_until is None:
            return False

        limit_until = self.rate_limited_until
        if limit_until.tzinfo is None:
            limit_until = limit_until.replace(tzinfo=UTC)
        return limit_until > datetime.now(tz=UTC)
