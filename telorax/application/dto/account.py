from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any

from telorax.core.enums import AccountState


@dataclass(frozen=True, slots=True)
class AccountSummaryDTO:
    id: int
    msisdn: int
    state: AccountState
    country_iso: str | None
    reliability_score: int
    is_operational: bool

    def to_api_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload['state'] = self.state.name
        return payload


@dataclass(frozen=True, slots=True)
class AccountDetailDTO:
    id: int
    msisdn: int
    state: AccountState
    country_iso: str | None
    telegram_user_id: int | None
    telegram_username: str | None
    display_name: str | None
    reliability_score: int
    is_operational: bool
    is_rate_limited: bool
    rate_limited_until: datetime | None
    restricted_until: datetime | None
    last_online_at: datetime | None
    two_factor_confirmed_at: datetime | None
    foreign_sessions_revoked_at: datetime | None
    last_engaged_at: datetime | None
    account_ttl_configured: bool
    proxy_label: str | None
    notes: str | None
    provisioned_at: datetime | None
    created_at: datetime | None
    updated_at: datetime | None

    def to_api_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload['state'] = self.state.name
        return payload


@dataclass(frozen=True, slots=True)
class AccountListDTO:
    items: tuple[AccountSummaryDTO, ...]
    total: int
    limit: int
    offset: int

    def to_api_dict(self) -> dict[str, Any]:
        return {
            'items': [item.to_api_dict() for item in self.items],
            'total': self.total,
            'limit': self.limit,
            'offset': self.offset,
        }


@dataclass(frozen=True, slots=True)
class AccountStatsDTO:
    total: int
    by_state: dict[str, int]
    operational: int

    def to_api_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class UpdateAccountDTO:
    state: AccountState | None = None
    notes: str | None = None
    proxy_label: str | None = None
    reliability_score: int | None = None


@dataclass(frozen=True, slots=True)
class ImportSessionDTO:
    password: str | None = None
    ignore_revoke: bool = False
    ignore_2fa: bool = False
    renew: bool = True


@dataclass(frozen=True, slots=True)
class ImportSessionResultDTO:
    account: AccountDetailDTO
    created: bool

    def to_api_dict(self) -> dict[str, Any]:
        return {
            'account': self.account.to_api_dict(),
            'created': self.created,
        }
