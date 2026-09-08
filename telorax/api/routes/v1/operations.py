from __future__ import annotations

from dataclasses import asdict
from typing import Any

from fastapi import APIRouter, HTTPException, Query

from telorax.api.dependencies import OperationServiceDep
from telorax.application.dto.operation import CreateOperationDTO
from telorax.core.enums import EngagementKind
from telorax.core.exceptions import OperationValidationError

router = APIRouter(prefix='/operations', tags=['operations'])


def _parse_engagement_kind(value: object) -> EngagementKind:
    if isinstance(value, EngagementKind):
        return value
    if isinstance(value, int):
        return EngagementKind(value)
    if isinstance(value, str):
        return EngagementKind[value.upper()]
    msg = 'engagement_kind must be an integer or enum name'
    raise OperationValidationError(msg)


@router.get('/queued')
async def list_queued_operations(
    operation_service: OperationServiceDep,
    limit: int = Query(default=50, ge=1, le=500),
) -> list[dict[str, Any]]:
    operations = await operation_service.list_queued(limit=limit)
    return [asdict(operation) for operation in operations]


@router.get('/{operation_id}')
async def get_operation(
    operation_id: int,
    operation_service: OperationServiceDep,
) -> dict[str, Any]:
    operation = await operation_service.get_operation(operation_id)
    if operation is None:
        raise HTTPException(status_code=404, detail='Operation not found')
    return asdict(operation)


@router.post('', status_code=201)
async def create_operation(
    payload: dict[str, Any],
    operation_service: OperationServiceDep,
) -> dict[str, Any]:
    dto = CreateOperationDTO(
        engagement_kind=_parse_engagement_kind(payload['engagement_kind']),
        target_count=int(payload['target_count']),
        target_spec=dict(payload['target_spec']),
        priority=int(payload.get('priority', 0)),
        country_filter=payload.get('country_filter'),
        source_label=payload.get('source_label'),
    )
    try:
        operation = await operation_service.create_operation(dto)
    except OperationValidationError as exc:
        raise HTTPException(status_code=422, detail=exc.message) from exc
    return asdict(operation)
