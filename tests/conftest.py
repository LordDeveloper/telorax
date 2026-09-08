from __future__ import annotations

from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from telorax.api.app import create_fastapi_app
from telorax.application.dto.campaign import CampaignSummaryDTO
from telorax.application.dto.health import ComponentHealthDTO, HealthReportDTO
from telorax.bootstrap.container import Container
from telorax.core.enums import EngagementKind


@pytest.fixture
def api_client() -> TestClient:
    container = Container()
    campaign_service = AsyncMock()
    campaign_service.list_queued = AsyncMock(return_value=[])
    campaign_service.get_campaign = AsyncMock(return_value=None)
    campaign_service.create_campaign = AsyncMock(
        return_value=CampaignSummaryDTO(
            id=1,
            engagement_kind=EngagementKind.VIEW,
            target_count=10,
            fulfilled_count=0,
            state='QUEUED',
            progress_ratio=0.0,
            remaining_count=10,
        ),
    )
    health_service = AsyncMock()
    health_service.get_health_report = AsyncMock(
        return_value=HealthReportDTO(
            version='0.1.0',
            status='healthy',
            components=(
                ComponentHealthDTO(name='config', status='ok'),
                ComponentHealthDTO(name='database', status='ok'),
                ComponentHealthDTO(name='redis', status='ok'),
            ),
        ),
    )
    container.campaign_service.override(campaign_service)
    container.health_service.override(health_service)
    app = create_fastapi_app(container)
    return TestClient(app)
