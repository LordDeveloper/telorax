from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from telorax.application.dto.operation import CreateOperationDTO
from telorax.application.services.operation_service import OperationService
from telorax.core.enums import EngagementKind, OperationState
from telorax.domain.entities import Operation


@pytest.mark.asyncio
async def test_get_operation_returns_summary() -> None:
    operation = Operation(
        id=7,
        engagement_kind=EngagementKind.VIEW,
        target_count=20,
        fulfilled_count=5,
        target_spec={'peer_ref': '@test'},
        state=OperationState.QUEUED,
        dedup_fingerprint='abc',
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
    assert summary.remaining_count == 15


@pytest.mark.asyncio
async def test_create_operation_persists_and_commits() -> None:
    created = Operation(
        id=3,
        engagement_kind=EngagementKind.SUBSCRIBE,
        target_count=5,
        fulfilled_count=0,
        target_spec={'peer_ref': '@channel'},
        state=OperationState.QUEUED,
        dedup_fingerprint='hash',
    )
    unit_of_work = AsyncMock()
    unit_of_work.operations.create = AsyncMock(return_value=created)
    unit_of_work.commit = AsyncMock()
    session_factory = MagicMock()
    dto = CreateOperationDTO(
        engagement_kind=EngagementKind.SUBSCRIBE,
        target_count=5,
        target_spec={'peer_ref': '@channel'},
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
