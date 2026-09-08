from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import datetime

    from telorax.core.enums import DispatchOutcome


@dataclass(slots=True)
class OperationDispatch:
    """Record that an account executed an operation (dedup + audit)."""

    operation_id: int
    account_id: int
    outcome: DispatchOutcome
    dispatched_at: datetime
    error_code: str | None = None
