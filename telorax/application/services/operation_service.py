from __future__ import annotations

from typing import TYPE_CHECKING

from telorax.application.dto.operation import CreateOperationDTO, OperationSummaryDTO
from telorax.application.validators.operation_validator import validate_create_operation
from telorax.core.enums import OperationState
from telorax.domain.entities import Operation
from telorax.domain.value_objects.operation_fingerprint import build_operation_fingerprint
from telorax.infrastructure.database.repositories.unit_of_work import SQLAlchemyUnitOfWork

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


class OperationService:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def get_operation(self, operation_id: int) -> OperationSummaryDTO | None:
        async with SQLAlchemyUnitOfWork(self._session_factory) as unit_of_work:
            operation = await unit_of_work.operations.get_by_id(operation_id)
            return _to_summary(operation) if operation else None

    async def list_queued(self, *, limit: int) -> list[OperationSummaryDTO]:
        async with SQLAlchemyUnitOfWork(self._session_factory) as unit_of_work:
            operations = await unit_of_work.operations.list_queued(limit=limit)
            return [_to_summary(operation) for operation in operations]

    async def create_operation(self, dto: CreateOperationDTO) -> OperationSummaryDTO:
        validate_create_operation(dto)
        extra = dict(dto.extra)
        fingerprint = build_operation_fingerprint(dto.type, dto.target, extra)
        operation = Operation(
            id=0,
            type=dto.type,
            quantity=dto.quantity,
            completed=0,
            target=dto.target,
            extra=extra,
            state=OperationState.QUEUED,
            fingerprint=fingerprint,
            country=dto.country,
        )
        async with SQLAlchemyUnitOfWork(self._session_factory) as unit_of_work:
            created = await unit_of_work.operations.create(operation)
            await unit_of_work.commit()
            return _to_summary(created)


def _to_summary(operation: Operation) -> OperationSummaryDTO:
    return OperationSummaryDTO(
        id=operation.id,
        type=operation.type,
        quantity=operation.quantity,
        completed=operation.completed,
        remaining=operation.remaining,
        state=operation.state.name,
        progress_ratio=operation.progress_ratio,
    )
