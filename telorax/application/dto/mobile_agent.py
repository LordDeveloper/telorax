from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class TelegramCapabilitiesDTO:
    accessibility_enabled: bool = False
    can_observe_ui: bool = False
    can_perform_actions: bool = False
    package_installed: bool = False
    notes: str | None = None

    def to_api_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class MobileAgentRegisterDTO:
    platform: str
    arch: str
    version: str
    capabilities: TelegramCapabilitiesDTO


@dataclass(frozen=True, slots=True)
class MobileAgentHeartbeatDTO:
    status: str
    capabilities: TelegramCapabilitiesDTO
    tunnel_up: bool


@dataclass(frozen=True, slots=True)
class WireGuardConfigDTO:
    enabled: bool
    config_text: str
    interface_name: str
    endpoint: str
    server_public_key: str
    client_address: str

    def to_api_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class MobileAgentConfigDTO:
    poll_interval_seconds: int
    wireguard: WireGuardConfigDTO
    telegram: dict[str, Any]

    def to_api_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload['wireguard'] = self.wireguard.to_api_dict()
        return payload


@dataclass(frozen=True, slots=True)
class MobileAgentUpdateDTO:
    update_available: bool
    version: str
    url: str
    sha256: str
    mandatory: bool
    release_notes: str

    def to_api_dict(self) -> dict[str, Any]:
        return asdict(self)
