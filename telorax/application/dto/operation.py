from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from telorax.core.enums import OperationType


@dataclass(frozen=True, slots=True)
class CreateOperationDTO:
    type: OperationType
    quantity: int
    target: str | int
    extra: dict[str, Any]
    country: str | None = None


@dataclass(frozen=True, slots=True)
class OperationSummaryDTO:
    id: int
    type: OperationType
    quantity: int
    completed: int
    remaining: int
    state: str
    progress_ratio: float

    def to_api_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload['type'] = int(self.type)
        return payload
