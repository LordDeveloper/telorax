from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from telorax.application.services.health_service import HealthService
from telorax.core.config.settings import Settings


@pytest.mark.asyncio
async def test_health_report_marks_missing_config_as_degraded() -> None:
    settings = Settings()
    connection = AsyncMock()
    connection.__aenter__.return_value = connection
    connection.execute = AsyncMock()
    engine = MagicMock()
    engine.connect.return_value = connection

    service = HealthService(settings=settings, db_engine=engine)
    report = await service.get_health_report()

    assert report.version
    assert report.status == 'degraded'
    config_component = next(
        component for component in report.components if component.name == 'config'
    )
    assert config_component.status == 'degraded'
