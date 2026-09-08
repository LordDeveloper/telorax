from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from telorax.application.dto.operation import CreateOperationDTO
from telorax.application.services.operation_service import OperationService
from telorax.core.enums import OperationState, OperationType
from telorax.domain.entities import Operation


@pytest.mark.asyncio
async def test_get_operation_returns_summary() -> None:
    operation = Operation(
        id=7,
        type=OperationType.VIEW,
        quantity=20,
        completed=5,
        target='@test',
        extra={},
        state=OperationState.QUEUED,
        fingerprint='abc',
    )
    unit_of_work = AsyncMock()
    unit_of_work.operations.get_by_id = AsyncMock(return_value=operation)
    session_factory = MagicMock()

    with patch(
        'telorax.application.services.operation_service.SQLAlchemyUnitOfWork',
    ) as unit_of_work_cls:
        unit_of_work_cls.return_value.__aenter__ = AsyncMock(return_value=unit_of_work)
        unit_of_work_cls.return_value.__aexit__ = AsyncMock(return_value=None)
        service = OperationService(session_factory=session_factory)
        summary = await service.get_operation(7)

    assert summary is not None
    assert summary.id == 7
    assert summary.remaining == 15


@pytest.mark.asyncio
async def test_create_operation_persists_and_commits() -> None:
    created = Operation(
        id=3,
        type=OperationType.SUBSCRIBE,
        quantity=5,
        completed=0,
        target='@channel',
        extra={},
        state=OperationState.QUEUED,
        fingerprint='hash',
    )
    unit_of_work = AsyncMock()
    unit_of_work.operations.create = AsyncMock(return_value=created)
    unit_of_work.commit = AsyncMock()
    session_factory = MagicMock()
    dto = CreateOperationDTO(
        type=OperationType.SUBSCRIBE,
        quantity=5,
        target='@channel',
        extra={},
    )

    with patch(
        'telorax.application.services.operation_service.SQLAlchemyUnitOfWork',
    ) as unit_of_work_cls:
        unit_of_work_cls.return_value.__aenter__ = AsyncMock(return_value=unit_of_work)
        unit_of_work_cls.return_value.__aexit__ = AsyncMock(return_value=None)
        service = OperationService(session_factory=session_factory)
        summary = await service.create_operation(dto)

    unit_of_work.commit.assert_awaited_once()
    assert summary.id == 3
