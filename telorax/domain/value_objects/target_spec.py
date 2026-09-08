from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ViewTargetSpec:
    peer_ref: str | int
    message_ids: list[int] | None = None
    story_ids: list[int] | None = None
    members_only: bool = False


@dataclass(frozen=True, slots=True)
class SubscribeTargetSpec:
    peer_ref: str | int
    auto_unsubscribe_days: int = 30
    read_history_on_join: bool = False
    search_query: str | None = None


@dataclass(frozen=True, slots=True)
class ReactionTargetSpec:
    peer_ref: str | int
    message_ids: list[int] | None = None
    story_ids: list[int] | None = None
    emoji: str = ''
    preflight_view: bool = False


@dataclass(frozen=True, slots=True)
class SponsoredTargetSpec:
    peer_ref: str | int
    click_probability: float = 0.0
    skip_usernames: tuple[str, ...] = ()
    report_spam: bool = False
