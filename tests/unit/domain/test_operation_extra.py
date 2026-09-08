from __future__ import annotations

from typing import cast

import pytest

from telorax.core.enums import OperationType
from telorax.core.exceptions import OperationValidationError
from telorax.domain.value_objects.operation_extra import (
    BotStart,
    ButtonClick,
    PollVote,
    Reaction,
    SearchView,
    Sponsored,
    Subscribe,
    View,
    extra_to_dict,
    parse_operation_extra,
)


def test_parse_view_extra() -> None:
    result = parse_operation_extra(
        OperationType.VIEW,
        {'message_ids': [1, 2], 'story_ids': [3], 'members_only': True},
    )
    assert result == View(message_ids=[1, 2], story_ids=[3], members_only=True)


def test_parse_subscribe_extra() -> None:
    result = parse_operation_extra(
        OperationType.SUBSCRIBE,
        {'auto_unsubscribe_days': 7, 'read_history_on_join': True, 'search_query': 'news'},
    )
    assert result == Subscribe(
        auto_unsubscribe_days=7,
        read_history_on_join=True,
        search_query='news',
    )


def test_parse_poll_vote_extra() -> None:
    result = parse_operation_extra(OperationType.POLL_VOTE, {'option': 2})
    assert result == PollVote(option=2)


def test_parse_poll_vote_requires_option() -> None:
    with pytest.raises(OperationValidationError, match='extra.option is required'):
        parse_operation_extra(OperationType.POLL_VOTE, {})


def test_parse_reaction_extra() -> None:
    result = parse_operation_extra(
        OperationType.REACTION,
        {'message_ids': [4], 'emoji': '👍', 'preflight_view': True},
    )
    assert result == Reaction(message_ids=[4], story_ids=None, emoji='👍', preflight_view=True)


def test_parse_sponsored_extra() -> None:
    result = parse_operation_extra(
        OperationType.SPONSORED,
        {'click_probability': 0.5, 'skip_usernames': ['spam'], 'report_spam': True},
    )
    assert result == Sponsored(click_probability=0.5, skip_usernames=('spam',), report_spam=True)


def test_parse_search_view_extra() -> None:
    result = parse_operation_extra(
        OperationType.SEARCH_VIEW,
        {'search_query': 'python', 'message_ids': [9]},
    )
    assert result == SearchView(search_query='python', message_ids=[9])


def test_parse_button_click_extra() -> None:
    result = parse_operation_extra(
        OperationType.BUTTON_CLICK,
        {'message_ids': [1], 'button_index': 2},
    )
    assert result == ButtonClick(message_ids=[1], button_index=2)


def test_parse_bot_start_extra() -> None:
    result = parse_operation_extra(OperationType.BOT_START, {'payload': 'start'})
    assert result == BotStart(payload='start')


def test_parse_unsupported_operation_type() -> None:
    with pytest.raises(OperationValidationError, match='Unsupported operation type'):
        parse_operation_extra(cast('OperationType', 999), {})


def test_parse_invalid_message_ids_raises() -> None:
    with pytest.raises(OperationValidationError, match='Invalid extra for VIEW'):
        parse_operation_extra(OperationType.VIEW, {'message_ids': ['bad']})


def test_parse_invalid_search_query_raises() -> None:
    with pytest.raises(OperationValidationError, match='Invalid extra for SUBSCRIBE'):
        parse_operation_extra(OperationType.SUBSCRIBE, {'search_query': 123})


def test_extra_to_dict_omits_empty_values() -> None:
    assert extra_to_dict(View(message_ids=[1])) == {'message_ids': [1]}


def test_extra_to_dict_keeps_non_default_values() -> None:
    assert extra_to_dict(Subscribe(auto_unsubscribe_days=7)) == {'auto_unsubscribe_days': 7}
