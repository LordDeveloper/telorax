from __future__ import annotations

from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException

from telorax.api.routes.v1.operations import _parse_operation_type, create_operation
from telorax.application.dto.operation import OperationSummaryDTO
from telorax.core.enums import OperationType
from telorax.core.exceptions import OperationValidationError


@pytest.mark.asyncio
async def test_create_operation_route_returns_summary() -> None:
    service = AsyncMock()
    service.create_operation = AsyncMock(
        return_value=OperationSummaryDTO(
            id=1,
            type=OperationType.VIEW,
            quantity=10,
            completed=0,
            remaining=10,
            state='QUEUED',
            progress_ratio=0.0,
        ),
    )
    payload = await create_operation(
        {
            'type': 'VIEW',
            'quantity': 10,
            'target': '@channel',
            'extra': {'message_ids': [1]},
        },
        service,
    )
    assert payload['type'] == OperationType.VIEW.value
    assert payload['quantity'] == 10
    assert payload['remaining'] == 10


@pytest.mark.asyncio
async def test_create_operation_route_accepts_numeric_type() -> None:
    service = AsyncMock()
    service.create_operation = AsyncMock(
        return_value=OperationSummaryDTO(
            id=2,
            type=OperationType.VIEW,
            quantity=10,
            completed=0,
            remaining=10,
            state='QUEUED',
            progress_ratio=0.0,
        ),
    )
    await create_operation(
        {
            'type': 1,
            'quantity': 10,
            'target': '@channel',
            'extra': {},
        },
        service,
    )
    service.create_operation.assert_awaited_once()


def test_parse_operation_type_invalid() -> None:
    with pytest.raises(OperationValidationError):
        _parse_operation_type({'invalid': True})


@pytest.mark.asyncio
async def test_create_operation_route_maps_validation_error() -> None:
    service = AsyncMock()
    service.create_operation = AsyncMock(side_effect=OperationValidationError('bad request'))
    with pytest.raises(HTTPException) as exc_info:
        await create_operation(
            {
                'type': 1,
                'quantity': 10,
                'target': '@channel',
                'extra': {},
            },
            service,
        )
    assert exc_info.value.status_code == 422
