from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from telorax.core.enums import EngagementKind, OperationState

if TYPE_CHECKING:
    from datetime import datetime


@dataclass(slots=True)
class Operation:
    """Batch request to perform one engagement kind on Telegram."""

    id: int
    engagement_kind: EngagementKind
    target_count: int
    fulfilled_count: int
    target_spec: dict[str, Any]
    state: OperationState = OperationState.QUEUED
    dedup_fingerprint: str | None = None
    retry_attempts: int = 0
    priority: int = 0
    country_filter: str | None = None
    source_label: str | None = None
    failure_summary: str | None = None
    scheduled_at: datetime | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @property
    def remaining_count(self) -> int:
        return max(self.target_count - self.fulfilled_count, 0)

    @property
    def is_fulfilled(self) -> bool:
        return self.remaining_count <= 0

    @property
    def progress_ratio(self) -> float:
        if self.target_count <= 0:
            return 1.0
        return min(self.fulfilled_count / self.target_count, 1.0)

    def dispatch_key_for(self, account_id: int) -> str:
        if not self.dedup_fingerprint:
            msg = f'Operation {self.id} has no dedup fingerprint'
            raise ValueError(msg)
        return f'{self.dedup_fingerprint}:{account_id}'
