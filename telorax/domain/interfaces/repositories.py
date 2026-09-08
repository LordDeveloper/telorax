from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from telorax.core.enums import AccountState, CampaignState
    from telorax.domain.entities import (
        Campaign,
        CampaignDispatch,
        ChannelMembership,
        TelegramAccount,
    )


class TelegramAccountRepository(Protocol):
    async def get_by_id(self, account_id: int) -> TelegramAccount | None: ...

    async def get_by_msisdn(self, msisdn: int) -> TelegramAccount | None: ...

    async def list_operational(
        self,
        *,
        limit: int,
        country_iso: str | None = None,
    ) -> list[TelegramAccount]: ...

    async def update_state(self, account_id: int, state: AccountState) -> None: ...

    async def update_reliability_score(self, account_id: int, score: int) -> None: ...

    async def create(self, account: TelegramAccount) -> TelegramAccount: ...


class CampaignRepository(Protocol):
    async def get_by_id(self, campaign_id: int) -> Campaign | None: ...

    async def list_queued(self, *, limit: int) -> list[Campaign]: ...

    async def create(self, campaign: Campaign) -> Campaign: ...

    async def update_fulfillment(
        self,
        campaign_id: int,
        *,
        fulfilled_count: int,
        state: CampaignState,
    ) -> None: ...


class ChannelMembershipRepository(Protocol):
    async def record(self, membership: ChannelMembership) -> ChannelMembership: ...

    async def list_due_for_unsubscribe(self, *, limit: int) -> list[ChannelMembership]: ...


class CampaignDispatchRepository(Protocol):
    async def exists(self, campaign_id: int, account_id: int) -> bool: ...

    async def record(self, dispatch: CampaignDispatch) -> None: ...


class UnitOfWork(Protocol):
    async def __aenter__(self) -> UnitOfWork: ...

    async def __aexit__(self, *args: object) -> None: ...

    async def commit(self) -> None: ...

    async def rollback(self) -> None: ...

    @property
    def campaign_dispatches(self) -> CampaignDispatchRepository: ...
