from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import select

from telorax.core.enums import PeerKind
from telorax.domain.entities import Membership
from telorax.domain.interfaces.repositories import MembershipRepository
from telorax.infrastructure.database import models as schema

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


def _to_membership(row: schema.Membership) -> Membership:
    return Membership(
        id=row.id,
        account_id=row.account_id,
        telegram_peer_id=row.telegram_peer_id,
        subscribed_at=row.subscribed_at,
        peer_kind=PeerKind(row.peer_kind),
        username=row.username,
        access_hash=row.access_hash,
        source_fingerprint=row.source_fingerprint,
        unsubscribe_scheduled_at=row.unsubscribe_scheduled_at,
        last_activity_at=row.last_activity_at,
        is_active=row.is_active,
    )


class SQLAlchemyMembershipRepository(MembershipRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def record(self, membership: Membership) -> Membership:
        row = schema.Membership(
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
        self._session.add(row)
        await self._session.flush()
        return _to_membership(row)

    async def list_due_for_unsubscribe(self, *, limit: int) -> list[Membership]:
        result = await self._session.execute(
            select(schema.Membership)
            .where(schema.Membership.is_active.is_(True))
            .where(schema.Membership.unsubscribe_scheduled_at.is_not(None))
            .order_by(schema.Membership.unsubscribe_scheduled_at.asc())
            .limit(limit),
        )
        return [_to_membership(row) for row in result.scalars()]
