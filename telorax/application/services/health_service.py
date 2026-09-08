from __future__ import annotations

from http import HTTPStatus
from typing import TYPE_CHECKING

import httpx
import redis.asyncio as redis
from sqlalchemy import text

from telorax import __version__
from telorax.application.dto.health import ComponentHealthDTO, HealthReportDTO, SystemDiagnosticsDTO
from telorax.core.config.settings import Settings, default_env_path
from telorax.core.network import is_port_open, probe_host

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncEngine


class HealthService:
    def __init__(self, settings: Settings, db_engine: AsyncEngine) -> None:
        self._settings = settings
        self._db_engine = db_engine

    async def get_health_report(self) -> HealthReportDTO:
        components = [
            self._config_health(),
            await self._database_health(),
            await self._redis_health(),
            await self._api_health(),
        ]
        status = 'healthy' if all(item.status == 'ok' for item in components) else 'degraded'
        return HealthReportDTO(
            version=__version__,
            status=status,
            components=tuple(components),
        )

    async def run_diagnostics(self) -> SystemDiagnosticsDTO:
        env_path = default_env_path()
        health = await self.get_health_report()
        return SystemDiagnosticsDTO(
            config_path=str(env_path),
            config_exists=env_path.is_file(),
            version=__version__,
            health=health,
        )

    def _config_health(self) -> ComponentHealthDTO:
        env_path = self._settings.env_path
        if env_path.is_file():
            return ComponentHealthDTO(name='config', status='ok', detail=str(env_path))
        return ComponentHealthDTO(
            name='config',
            status='degraded',
            detail=f'missing env file: {env_path}',
        )

    async def _database_health(self) -> ComponentHealthDTO:
        try:
            async with self._db_engine.connect() as connection:
                await connection.execute(text('SELECT 1'))
        except Exception as exc:
            return ComponentHealthDTO(name='database', status='down', detail=str(exc))
        return ComponentHealthDTO(name='database', status='ok')

    async def _redis_health(self) -> ComponentHealthDTO:
        try:
            client = redis.from_url(self._settings.redis_url)
            await client.ping()
            await client.aclose()
        except Exception as exc:
            return ComponentHealthDTO(name='redis', status='down', detail=str(exc))
        return ComponentHealthDTO(name='redis', status='ok')

    async def _api_health(self) -> ComponentHealthDTO:
        host = self._settings.app_host
        port = self._settings.app_port
        target = probe_host(host)

        if not is_port_open(host, port):
            return ComponentHealthDTO(
                name='api',
                status='down',
                detail=f'not listening on {target}:{port}',
            )

        url = f'http://{target}:{port}/v1/health'
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                response = await client.get(url)
            if response.status_code == HTTPStatus.OK:
                payload = response.json()
                if isinstance(payload, dict) and 'status' in payload:
                    return ComponentHealthDTO(name='api', status='ok', detail=f'{target}:{port}')
            detail = (
                f'port {port} in use but response was not Telorax '
                f'(HTTP {response.status_code})'
            )
            return ComponentHealthDTO(name='api', status='degraded', detail=detail)
        except Exception as exc:
            return ComponentHealthDTO(
                name='api',
                status='degraded',
                detail=f'port {port} in use but not Telorax ({exc})',
            )
