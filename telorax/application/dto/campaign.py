from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from telorax.core.enums import EngagementKind


@dataclass(frozen=True, slots=True)
class CreateCampaignDTO:
    engagement_kind: EngagementKind
    target_count: int
    target_spec: dict[str, Any]
    priority: int = 0
    country_filter: str | None = None
    source_label: str | None = None


@dataclass(frozen=True, slots=True)
class CampaignSummaryDTO:
    id: int
    engagement_kind: EngagementKind
    target_count: int
    fulfilled_count: int
    state: str
    progress_ratio: float
    remaining_count: int
