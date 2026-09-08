from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from telorax.core.enums import DispatchOutcome


@dataclass(slots=True)
class CampaignDispatch:
    """ثبت اینکه یک account برای یک campaign اجرا شده (dedup + audit)."""

    campaign_id: int
    account_id: int
    outcome: DispatchOutcome
    dispatched_at: datetime
    error_code: str | None = None
