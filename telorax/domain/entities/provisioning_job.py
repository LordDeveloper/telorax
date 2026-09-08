from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from telorax.core.enums import ProvisioningState


@dataclass(slots=True)
class ProvisioningJob:
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
