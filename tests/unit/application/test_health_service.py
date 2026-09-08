from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from telorax.application.services.health_service import HealthService
from telorax.core.config.settings import Settings


def _mock_api_health(*, port_open: bool = True, telorax: bool = True) -> tuple[MagicMock, MagicMock]:
    response = MagicMock()
    response.status_code = 200 if telorax else 404
    response.json.return_value = {'status': 'healthy'} if telorax else {}

    client = AsyncMock()
    client.get = AsyncMock(return_value=response)
    client.__aenter__ = AsyncMock(return_value=client)
    client.__aexit__ = AsyncMock(return_value=None)

    return (
        patch(
            'telorax.application.services.health_service.is_port_open',
            return_value=port_open,
        ),
        patch(
            'telorax.application.services.health_service.httpx.AsyncClient',
            return_value=client,
        ),
    )


@pytest.mark.asyncio
async def test_health_report_marks_missing_config_as_degraded() -> None:
    settings = Settings()
    connection = AsyncMock()
    connection.execute = AsyncMock()
    connection.__aenter__ = AsyncMock(return_value=connection)
    connection.__aexit__ = AsyncMock(return_value=None)
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


@pytest.mark.asyncio
async def test_health_report_all_ok(tmp_path, monkeypatch) -> None:
    env_file = tmp_path / '.env'
    env_file.write_text('APP_PORT=8000\n', encoding='utf-8')
    monkeypatch.setenv('ENV_FILE', str(env_file))
    settings = Settings.load(env_file)
    connection = AsyncMock()
    connection.execute = AsyncMock()
    connection.__aenter__ = AsyncMock(return_value=connection)
    connection.__aexit__ = AsyncMock(return_value=None)
    engine = MagicMock()
    engine.connect.return_value = connection

    port_patch, client_patch = _mock_api_health()
    with (
        port_patch,
        client_patch,
        patch('telorax.application.services.health_service.redis.from_url') as redis_from_url,
    ):
        redis_client = AsyncMock()
        redis_client.ping = AsyncMock()
        redis_client.aclose = AsyncMock()
        redis_from_url.return_value = redis_client
        service = HealthService(settings=settings, db_engine=engine)
        report = await service.get_health_report()

    assert report.status == 'healthy'


@pytest.mark.asyncio
async def test_run_diagnostics(tmp_path, monkeypatch) -> None:
    env_file = tmp_path / '.env'
    env_file.write_text('APP_PORT=8000\n', encoding='utf-8')
    monkeypatch.setenv('ENV_FILE', str(env_file))
    settings = Settings.load(env_file)
    connection = AsyncMock()
    connection.execute = AsyncMock()
    connection.__aenter__ = AsyncMock(return_value=connection)
    connection.__aexit__ = AsyncMock(return_value=None)
    engine = MagicMock()
    engine.connect.return_value = connection

    port_patch, client_patch = _mock_api_health()
    with (
        port_patch,
        client_patch,
        patch('telorax.application.services.health_service.redis.from_url') as redis_from_url,
    ):
        redis_client = AsyncMock()
        redis_client.ping = AsyncMock()
        redis_client.aclose = AsyncMock()
        redis_from_url.return_value = redis_client
        service = HealthService(settings=settings, db_engine=engine)
        diagnostics = await service.run_diagnostics()

    assert diagnostics.config_exists is True
    assert diagnostics.health.status == 'healthy'


@pytest.mark.asyncio
async def test_database_health_down() -> None:
    settings = Settings()
    engine = MagicMock()
    engine.connect.side_effect = RuntimeError('db down')
    service = HealthService(settings=settings, db_engine=engine)

    component = await service._database_health()

    assert component.status == 'down'


@pytest.mark.asyncio
async def test_redis_health_down() -> None:
    settings = Settings()
    engine = MagicMock()
    service = HealthService(settings=settings, db_engine=engine)

    with patch(
        'telorax.application.services.health_service.redis.from_url',
        side_effect=RuntimeError('redis down'),
    ):
        component = await service._redis_health()

    assert component.status == 'down'


@pytest.mark.asyncio
async def test_api_health_detects_foreign_service() -> None:
    settings = Settings()
    engine = MagicMock()
    service = HealthService(settings=settings, db_engine=engine)

    port_patch, client_patch = _mock_api_health(telorax=False)
    with port_patch, client_patch:
        component = await service._api_health()

    assert component.status == 'degraded'
    assert component.detail is not None
    assert 'not Telorax' in component.detail
