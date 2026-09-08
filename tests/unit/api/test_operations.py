from __future__ import annotations

from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from telorax.api.app import create_fastapi_app
from telorax.api.routes.v1.operations import _parse_engagement_kind
from telorax.bootstrap.container import Container
from telorax.core.enums import EngagementKind
from telorax.core.exceptions import OperationValidationError


def test_list_queued_operations(api_client: TestClient) -> None:
    response = api_client.get('/v1/operations/queued')
    assert response.status_code == 200
    assert response.json() == []


def test_get_operation_not_found(api_client: TestClient) -> None:
    response = api_client.get('/v1/operations/999')
    assert response.status_code == 404


def test_create_operation(api_client: TestClient) -> None:
    response = api_client.post(
        '/v1/operations',
        json={
            'engagement_kind': 'VIEW',
            'target_count': 10,
            'target_spec': {'peer_ref': '@channel'},
        },
    )
    assert response.status_code == 201
    payload = response.json()
    assert payload['id'] == 1
    assert payload['engagement_kind'] == EngagementKind.VIEW.value


def test_create_operation_validation_error() -> None:
    container = Container()
    operation_service = AsyncMock()
    operation_service.create_operation = AsyncMock(
        side_effect=OperationValidationError('invalid payload'),
    )
    container.operation_service.override(operation_service)
    client = TestClient(create_fastapi_app(container))
    response = client.post(
        '/v1/operations',
        json={
            'engagement_kind': 1,
            'target_count': 10,
            'target_spec': {'peer_ref': '@channel'},
        },
    )
    assert response.status_code == 422


def test_parse_engagement_kind_invalid() -> None:
    with pytest.raises(OperationValidationError):
        _parse_engagement_kind({'invalid': True})
