from __future__ import annotations

from telorax.core.logging.context import (
    bind_context,
    bind_correlation_id,
    bind_cycle_id,
    mask_phone,
)
from telorax.domain.value_objects.target_spec import (
    ReactionTargetSpec,
    SubscribeTargetSpec,
    ViewTargetSpec,
)


def test_mask_phone_short_value() -> None:
    assert mask_phone('123') == '***'


def test_mask_phone_masks_suffix() -> None:
    assert mask_phone('989121234567').endswith('***')


def test_bind_correlation_id_returns_value() -> None:
    value = bind_correlation_id('abc123')
    assert value == 'abc123'


def test_bind_cycle_id_returns_value() -> None:
    value = bind_cycle_id('cycle-1')
    assert value == 'cycle-1'


def test_bind_context_accepts_kwargs() -> None:
    bind_context(account_id=1)


def test_target_spec_dataclasses() -> None:
    view = ViewTargetSpec(peer_ref='@channel', message_ids=[1, 2])
    subscribe = SubscribeTargetSpec(peer_ref='@channel', auto_unsubscribe_days=7)
    reaction = ReactionTargetSpec(peer_ref='@channel', emoji='👍')
    assert view.members_only is False
    assert subscribe.read_history_on_join is False
    assert reaction.preflight_view is False
