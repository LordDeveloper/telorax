from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from telorax.core.enums import OperationType
from telorax.core.exceptions import OperationValidationError


@dataclass(frozen=True, slots=True)
class View:
    message_ids: list[int] | None = None
    story_ids: list[int] | None = None
    members_only: bool = False


@dataclass(frozen=True, slots=True)
class Subscribe:
    auto_unsubscribe_days: int = 30
    read_history_on_join: bool = False
    search_query: str | None = None


@dataclass(frozen=True, slots=True)
class PollVote:
    option: int


@dataclass(frozen=True, slots=True)
class Reaction:
    message_ids: list[int] | None = None
    story_ids: list[int] | None = None
    emoji: str = ''
    preflight_view: bool = False


@dataclass(frozen=True, slots=True)
class Sponsored:
    click_probability: float = 0.0
    skip_usernames: tuple[str, ...] = ()
    report_spam: bool = False


@dataclass(frozen=True, slots=True)
class SearchView:
    search_query: str | None = None
    message_ids: list[int] | None = None


@dataclass(frozen=True, slots=True)
class ButtonClick:
    message_ids: list[int] | None = None
    button_index: int = 0


@dataclass(frozen=True, slots=True)
class BotStart:
    payload: str | None = None


OperationParams = (
    View
    | Subscribe
    | PollVote
    | Reaction
    | Sponsored
    | SearchView
    | ButtonClick
    | BotStart
)


def parse_operation_extra(operation_type: OperationType, extra: dict[str, Any]) -> OperationParams:  # noqa: PLR0911, PLR0912
    try:
        match operation_type:
            case OperationType.VIEW:
                return View(
                    message_ids=_optional_int_list(extra.get('message_ids')),
                    story_ids=_optional_int_list(extra.get('story_ids')),
                    members_only=bool(extra.get('members_only', False)),
                )
            case OperationType.SUBSCRIBE:
                return Subscribe(
                    auto_unsubscribe_days=int(extra.get('auto_unsubscribe_days', 30)),
                    read_history_on_join=bool(extra.get('read_history_on_join', False)),
                    search_query=_optional_str(extra.get('search_query')),
                )
            case OperationType.POLL_VOTE:
                if 'option' not in extra:
                    msg = 'extra.option is required for POLL_VOTE operations'
                    raise OperationValidationError(msg)
                return PollVote(option=int(extra['option']))
            case OperationType.REACTION:
                return Reaction(
                    message_ids=_optional_int_list(extra.get('message_ids')),
                    story_ids=_optional_int_list(extra.get('story_ids')),
                    emoji=str(extra.get('emoji', '')),
                    preflight_view=bool(extra.get('preflight_view', False)),
                )
            case OperationType.SPONSORED:
                return Sponsored(
                    click_probability=float(extra.get('click_probability', 0.0)),
                    skip_usernames=tuple(extra.get('skip_usernames', ())),
                    report_spam=bool(extra.get('report_spam', False)),
                )
            case OperationType.SEARCH_VIEW:
                return SearchView(
                    search_query=_optional_str(extra.get('search_query')),
                    message_ids=_optional_int_list(extra.get('message_ids')),
                )
            case OperationType.BUTTON_CLICK:
                return ButtonClick(
                    message_ids=_optional_int_list(extra.get('message_ids')),
                    button_index=int(extra.get('button_index', 0)),
                )
            case OperationType.BOT_START:
                return BotStart(payload=_optional_str(extra.get('payload')))
            case _:
                msg = f'Unsupported operation type: {operation_type}'
                raise OperationValidationError(msg)
    except (TypeError, ValueError) as exc:
        raise OperationValidationError(f'Invalid extra for {operation_type.name}: {exc}') from exc


def extra_to_dict(extra: OperationParams) -> dict[str, Any]:
    empty_values = (None, '', (), False, 0, 0.0)
    return {key: value for key, value in asdict(extra).items() if value not in empty_values}


def _optional_str(value: object) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise TypeError('expected string or null')
    return value


def _optional_int_list(value: object) -> list[int] | None:
    if value is None:
        return None
    if not isinstance(value, list) or not all(isinstance(item, int) for item in value):
        raise TypeError('expected list of integers or null')
    return value
