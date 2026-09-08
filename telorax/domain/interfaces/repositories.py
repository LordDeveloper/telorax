from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from telorax.core.enums import AccountState, OperationState
    from telorax.domain.entities import Account, Dispatch, Membership, Operation


class AccountRepository(Protocol):
    async def get_by_id(self, account_id: int) -> Account | None: ...

    async def get_by_msisdn(self, msisdn: int) -> Account | None: ...

    async def list_operational(
        self,
        *,
        limit: int,
        country_iso: str | None = None,
    ) -> list[Account]: ...

    async def update_state(self, account_id: int, state: AccountState) -> None: ...

    async def update_reliability_score(self, account_id: int, score: int) -> None: ...

    async def create(self, account: Account) -> Account: ...


class OperationRepository(Protocol):
    async def get_by_id(self, operation_id: int) -> Operation | None: ...

    async def list_queued(self, *, limit: int) -> list[Operation]: ...

    async def create(self, operation: Operation) -> Operation: ...

    async def update_fulfillment(
        self,
        operation_id: int,
        *,
        completed: int,
        state: OperationState,
    ) -> None: ...


class MembershipRepository(Protocol):
    async def record(self, membership: Membership) -> Membership: ...

    async def list_due_for_unsubscribe(self, *, limit: int) -> list[Membership]: ...


class DispatchRepository(Protocol):
    async def exists(self, operation_id: int, account_id: int) -> bool: ...

    async def record(self, dispatch: Dispatch) -> None: ...


class UnitOfWork(Protocol):
    async def __aenter__(self) -> UnitOfWork: ...

    async def __aexit__(self, *args: object) -> None: ...

    async def commit(self) -> None: ...

    async def rollback(self) -> None: ...

    @property
    def accounts(self) -> AccountRepository: ...

    @property
    def operations(self) -> OperationRepository: ...

    @property
    def memberships(self) -> MembershipRepository: ...

    @property
    def dispatches(self) -> DispatchRepository: ...
