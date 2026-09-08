from __future__ import annotations

from telorax.cli.console import RED, decode_key, is_interactive, paint


def test_is_interactive_returns_bool() -> None:
    assert isinstance(is_interactive(), bool)


def test_decode_key_maps_enter() -> None:
    assert decode_key('\r') == 'enter'
    assert decode_key('\n') == 'enter'


def test_paint_wraps_text_with_color() -> None:
    assert paint('ok', RED).startswith('\033[91m')
