from __future__ import annotations

from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from telorax.api.app import create_fastapi_app
from telorax.application.dto.account import (
    AccountDetailDTO,
    AccountListDTO,
    AccountStatsDTO,
    AccountSummaryDTO,
    ImportSessionResultDTO,
)
from telorax.application.dto.health import ComponentHealthDTO, HealthReportDTO
from telorax.application.dto.operation import OperationSummaryDTO
from telorax.bootstrap.container import Container
from telorax.core.enums import AccountState, OperationType


@pytest.fixture
def api_client() -> TestClient:
    container = Container()
    operation_service = AsyncMock()
    operation_service.list_queued = AsyncMock(return_value=[])
    operation_service.get_operation = AsyncMock(return_value=None)
    operation_service.create_operation = AsyncMock(
        return_value=OperationSummaryDTO(
            id=1,
            type=OperationType.VIEW,
            quantity=10,
            completed=0,
            state='QUEUED',
            progress_ratio=0.0,
            remaining=10,
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
                ComponentHealthDTO(name='api', status='ok'),
            ),
        ),
    )
    account_service = AsyncMock()
    account_service.list_accounts = AsyncMock(
        return_value=AccountListDTO(
            items=(
                AccountSummaryDTO(
                    id=1,
                    msisdn=989121234567,
                    state=AccountState.ACTIVE,
                    country_iso='IR',
                    reliability_score=100,
                    is_operational=True,
                ),
            ),
            total=1,
            limit=50,
            offset=0,
        ),
    )
    account_service.get_stats = AsyncMock(
        return_value=AccountStatsDTO(
            total=1,
            by_state={'ACTIVE': 1},
            operational=1,
        ),
    )
    detail = AccountDetailDTO(
        id=1,
        msisdn=989121234567,
        state=AccountState.ACTIVE,
        country_iso='IR',
        telegram_user_id=123,
        telegram_username='demo',
        display_name='Demo User',
        reliability_score=100,
        is_operational=True,
        is_rate_limited=False,
        rate_limited_until=None,
        restricted_until=None,
        last_online_at=None,
        two_factor_confirmed_at=None,
        foreign_sessions_revoked_at=None,
        last_engaged_at=None,
        account_ttl_configured=False,
        proxy_label=None,
        notes=None,
        provisioned_at=None,
        created_at=None,
        updated_at=None,
    )
    account_service.get_account = AsyncMock(return_value=detail)
    account_service.update_account = AsyncMock(return_value=detail)
    account_service.deactivate_account = AsyncMock(return_value=detail)
    account_service.import_session = AsyncMock(
        return_value=ImportSessionResultDTO(account=detail, created=True),
    )
    container.operation_service.override(operation_service)
    container.health_service.override(health_service)
    container.account_service.override(account_service)
    app = create_fastapi_app(container)
    return TestClient(app)


@pytest.fixture
def auth_headers() -> dict[str, str]:
    settings = Container().config()
    import base64

    token = base64.b64encode(
        f'{settings.auth_username}:{settings.auth_password.get_secret_value()}'.encode(),
    ).decode()
    return {'Authorization': f'Basic {token}'}
