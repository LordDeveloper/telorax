from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import select

from telorax.core.enums import PeerKind
from telorax.domain.entities import Membership
from telorax.domain.interfaces.repositories import MembershipRepository
from telorax.infrastructure.database.models import MembershipModel

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


def _to_membership(model: MembershipModel) -> Membership:
    return Membership(
        id=model.id,
        account_id=model.account_id,
        telegram_peer_id=model.telegram_peer_id,
        subscribed_at=model.subscribed_at,
        peer_kind=PeerKind(model.peer_kind),
        username=model.username,
        access_hash=model.access_hash,
        source_fingerprint=model.source_fingerprint,
        unsubscribe_scheduled_at=model.unsubscribe_scheduled_at,
        last_activity_at=model.last_activity_at,
        is_active=model.is_active,
    )


class SQLAlchemyMembershipRepository(MembershipRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def record(self, membership: Membership) -> Membership:
        model = MembershipModel(
            account_id=membership.account_id,
            telegram_peer_id=membership.telegram_peer_id,
            username=membership.username,
            access_hash=membership.access_hash,
            peer_kind=membership.peer_kind.value,
            source_fingerprint=membership.source_fingerprint,
            subscribed_at=membership.subscribed_at,
            unsubscribe_scheduled_at=membership.unsubscribe_scheduled_at,
            last_activity_at=membership.last_activity_at,
            is_active=membership.is_active,
        )
        self._session.add(model)
        await self._session.flush()
        return _to_membership(model)

    async def list_due_for_unsubscribe(self, *, limit: int) -> list[Membership]:
        result = await self._session.execute(
            select(MembershipModel)
            .where(MembershipModel.is_active.is_(True))
            .where(MembershipModel.unsubscribe_scheduled_at.is_not(None))
            .order_by(MembershipModel.unsubscribe_scheduled_at.asc())
            .limit(limit),
        )
        return [_to_membership(model) for model in result.scalars()]
