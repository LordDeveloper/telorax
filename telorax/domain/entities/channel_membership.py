from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import datetime

    from telorax.core.enums import PeerKind


@dataclass(slots=True)
class ChannelMembership:
    """Account membership in a channel/group, including scheduled leave time."""

    id: int
    account_id: int
    telegram_peer_id: int
    subscribed_at: datetime
    peer_kind: PeerKind
    username: str | None = None
    access_hash: int | None = None
    source_fingerprint: str | None = None
    unsubscribe_scheduled_at: datetime | None = None
    last_activity_at: datetime | None = None
    is_active: bool = True
