from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ComponentHealthDTO:
    name: str
    status: str
    detail: str | None = None


@dataclass(frozen=True, slots=True)
class HealthReportDTO:
    version: str
    status: str
    components: tuple[ComponentHealthDTO, ...]


@dataclass(frozen=True, slots=True)
class SystemDiagnosticsDTO:
    config_path: str
    config_exists: bool
    version: str
    health: HealthReportDTO
