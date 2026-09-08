from __future__ import annotations

from typing import TYPE_CHECKING

from telorax.application.dto.mobile_agent import (
    MobileAgentConfigDTO,
    MobileAgentHeartbeatDTO,
    MobileAgentRegisterDTO,
    MobileAgentUpdateDTO,
    TelegramCapabilitiesDTO,
    WireGuardConfigDTO,
)

if TYPE_CHECKING:
    from telorax.core.config.settings import Settings


class MobileAgentService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._devices: dict[str, MobileAgentRegisterDTO] = {}

    def register(self, agent_id: str, dto: MobileAgentRegisterDTO) -> dict[str, str]:
        self._devices[agent_id] = dto
        return {'device_id': agent_id, 'status': 'registered'}

    def heartbeat(self, agent_id: str, dto: MobileAgentHeartbeatDTO) -> dict[str, str]:
        if agent_id in self._devices:
            previous = self._devices[agent_id]
            self._devices[agent_id] = MobileAgentRegisterDTO(
                platform=previous.platform,
                arch=previous.arch,
                version=previous.version,
                capabilities=dto.capabilities,
            )
        return {'status': 'ok'}

    def get_config(self, agent_id: str) -> MobileAgentConfigDTO:
        _ = agent_id
        client_ip = self._settings.wireguard_client_address_template.format(
            octet=self._settings.wireguard_client_address_octet,
        )
        wg_config = self._build_wireguard_config(client_ip)
        return MobileAgentConfigDTO(
            poll_interval_seconds=self._settings.mobile_agent_poll_seconds,
            wireguard=WireGuardConfigDTO(
                enabled=self._settings.wireguard_enabled,
                config_text=wg_config,
                interface_name=self._settings.wireguard_interface_name,
                endpoint=self._settings.wireguard_endpoint,
                server_public_key=self._settings.wireguard_server_public_key,
                client_address=client_ip,
            ),
            telegram={
                'target_package': 'org.telegram.messenger',
                'requires_accessibility': True,
            },
        )

    def check_update(
        self,
        *,
        current_version: str,
        platform: str,
        arch: str,
    ) -> MobileAgentUpdateDTO:
        latest = self._settings.mobile_agent_latest_version
        available = latest != current_version and bool(self._settings.mobile_agent_update_url)
        return MobileAgentUpdateDTO(
            update_available=available,
            version=latest,
            url=self._settings.mobile_agent_update_url if available else '',
            sha256=self._settings.mobile_agent_update_sha256 if available else '',
            mandatory=self._settings.mobile_agent_update_mandatory,
            release_notes=self._settings.mobile_agent_update_notes,
        )

    def _build_wireguard_config(self, client_address: str) -> str:
        if not self._settings.wireguard_enabled:
            return ''
        private_key = self._settings.wireguard_client_private_key.get_secret_value()
        if not private_key or not self._settings.wireguard_server_public_key:
            return ''
        endpoint = self._settings.wireguard_endpoint
        server_key = self._settings.wireguard_server_public_key
        allowed_ips = self._settings.wireguard_allowed_ips
        dns = self._settings.wireguard_dns
        return (
            '[Interface]\n'
            f'PrivateKey = {private_key}\n'
            f'Address = {client_address}\n'
            f'DNS = {dns}\n'
            '\n'
            '[Peer]\n'
            f'PublicKey = {server_key}\n'
            f'AllowedIPs = {allowed_ips}\n'
            f'Endpoint = {endpoint}\n'
            'PersistentKeepalive = 25\n'
        )

    @staticmethod
    def parse_capabilities(payload: dict[str, object]) -> TelegramCapabilitiesDTO:
        return TelegramCapabilitiesDTO(
            accessibility_enabled=bool(payload.get('accessibility_enabled')),
            can_observe_ui=bool(payload.get('can_observe_ui')),
            can_perform_actions=bool(payload.get('can_perform_actions')),
            package_installed=bool(payload.get('package_installed')),
            notes=str(payload['notes']) if payload.get('notes') else None,
        )
