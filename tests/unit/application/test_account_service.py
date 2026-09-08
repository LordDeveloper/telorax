from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from telorax.application.services.account_service import AccountService
from telorax.core.config.settings import Settings
from telorax.core.enums import AccountState
from telorax.domain.entities import Account


@pytest.mark.asyncio
async def test_list_operational_accounts() -> None:
    account = Account(
        id=1,
        msisdn=989121234567,
        session_ciphertext='cipher',
        state=AccountState.ACTIVE,
        country_iso='IR',
    )
    unit_of_work = AsyncMock()
    unit_of_work.accounts.list_operational = AsyncMock(return_value=[account])
    session_factory = MagicMock()

    with patch(
        'telorax.application.services.account_service.SQLAlchemyUnitOfWork',
    ) as unit_of_work_cls:
        unit_of_work_cls.return_value.__aenter__ = AsyncMock(return_value=unit_of_work)
        unit_of_work_cls.return_value.__aexit__ = AsyncMock(return_value=None)
        service = AccountService(session_factory=session_factory, settings=Settings())
        summaries = await service.list_operational(limit=10)

    assert len(summaries) == 1
    assert summaries[0].is_operational is True
