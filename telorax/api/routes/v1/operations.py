from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Query

from telorax.api.dependencies import OperationServiceDep
from telorax.application.dto.operation import CreateOperationDTO, OperationSummaryDTO
from telorax.core.enums import OperationType
from telorax.core.exceptions import OperationValidationError

router = APIRouter(prefix='/operations', tags=['operations'])


def _parse_operation_type(value: object) -> OperationType:
    if isinstance(value, OperationType):
        return value
    if isinstance(value, int):
        return OperationType(value)
    if isinstance(value, str):
        return OperationType[value.upper()]
    msg = 'type must be an integer operation type code'
    raise OperationValidationError(msg)


def _serialize_summary(operation: OperationSummaryDTO) -> dict[str, Any]:
    return operation.to_api_dict()


@router.get('/queued')
async def list_queued_operations(
    operation_service: OperationServiceDep,
    limit: int = Query(default=50, ge=1, le=500),
) -> list[dict[str, Any]]:
    operations = await operation_service.list_queued(limit=limit)
    return [_serialize_summary(operation) for operation in operations]


@router.get('/{operation_id}')
async def get_operation(
    operation_id: int,
    operation_service: OperationServiceDep,
) -> dict[str, Any]:
    operation = await operation_service.get_operation(operation_id)
    if operation is None:
        raise HTTPException(status_code=404, detail='Operation not found')
    return _serialize_summary(operation)


@router.post('', status_code=201)
async def create_operation(
    payload: dict[str, Any],
    operation_service: OperationServiceDep,
) -> dict[str, Any]:
    dto = CreateOperationDTO(
        type=_parse_operation_type(payload['type']),
        quantity=int(payload['quantity']),
        target=payload['target'],
        extra=dict(payload.get('extra') or {}),
        country=payload.get('country'),
    )
    try:
        operation = await operation_service.create_operation(dto)
    except OperationValidationError as exc:
        raise HTTPException(status_code=422, detail=exc.message) from exc
    return _serialize_summary(operation)
