from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any

from telorax.core.enums import ProvisioningState


@dataclass(frozen=True, slots=True)
class CreateProvisioningJobDTO:
    msisdn: int
    first_name: str
    last_name: str
    country_iso: str | None = None
    two_factor_password: str | None = None
    provider: str = 'android-agent'
    metadata: dict[str, Any] | None = None


@dataclass(frozen=True, slots=True)
class ProvisioningJobDTO:
    id: int
    msisdn: int
    state: ProvisioningState
    provider: str
    country_iso: str | None
    first_name: str
    last_name: str
    two_factor_password: str | None
    agent_id: str | None
    account_id: int | None
    failure_reason: str | None
    metadata: dict[str, Any]
    claimed_at: datetime | None
    completed_at: datetime | None
    created_at: datetime | None
    updated_at: datetime | None

    def to_api_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload['state'] = self.state.name
        return payload


@dataclass(frozen=True, slots=True)
class CompleteProvisioningJobDTO:
    ignore_revoke: bool = False
    ignore_2fa: bool = False
    renew: bool = True
