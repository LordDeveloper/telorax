from __future__ import annotations

from typing import TYPE_CHECKING

import redis.asyncio as redis
import structlog
from sqlalchemy import text

from telorax import __version__
from telorax.application.dto.health import ComponentHealthDTO, HealthReportDTO, SystemDiagnosticsDTO
from telorax.core.config.settings import Settings, default_env_path

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncEngine

log = structlog.get_logger(__name__)


class HealthService:
    def __init__(self, settings: Settings, db_engine: AsyncEngine) -> None:
        self._settings = settings
        self._db_engine = db_engine

    async def get_health_report(self) -> HealthReportDTO:
        components = [
            self._config_health(),
            await self._database_health(),
            await self._redis_health(),
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
            log.warning('health.database_failed', error=str(exc))
            return ComponentHealthDTO(name='database', status='down', detail=str(exc))
        return ComponentHealthDTO(name='database', status='ok')

    async def _redis_health(self) -> ComponentHealthDTO:
        try:
            client = redis.from_url(self._settings.redis_url)
            await client.ping()
            await client.aclose()
        except Exception as exc:
            log.warning('health.redis_failed', error=str(exc))
            return ComponentHealthDTO(name='redis', status='down', detail=str(exc))
        return ComponentHealthDTO(name='redis', status='ok')
