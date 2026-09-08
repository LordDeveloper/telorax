from __future__ import annotations

from dataclasses import dataclass

from telorax.core.enums import AccountState


@dataclass(frozen=True, slots=True)
class AccountSummaryDTO:
    id: int
    msisdn: int
    state: AccountState
    country_iso: str | None
    reliability_score: int
    is_operational: bool
