from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from telorax.core.enums import OperationState, OperationType

if TYPE_CHECKING:
    from datetime import datetime


@dataclass(slots=True)
class Operation:
    """Batch request to perform one operation type on Telegram."""

    id: int
    type: OperationType
    quantity: int
    completed: int
    target: str | int
    extra: dict[str, Any]
    state: OperationState = OperationState.QUEUED
    fingerprint: str | None = None
    retry_attempts: int = 0
    country: str | None = None
    failure_summary: str | None = None
    scheduled_at: datetime | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @property
    def remaining(self) -> int:
        return max(self.quantity - self.completed, 0)

    @property
    def is_complete(self) -> bool:
        return self.remaining <= 0

    @property
    def progress_ratio(self) -> float:
        if self.quantity <= 0:
            return 1.0
        return min(self.completed / self.quantity, 1.0)

    def dispatch_key_for(self, account_id: int) -> str:
        if not self.fingerprint:
            msg = f'Operation {self.id} has no fingerprint'
            raise ValueError(msg)
        return f'{self.fingerprint}:{account_id}'
