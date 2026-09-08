from __future__ import annotations

from telorax.core.version import parse_version, version_lt


def test_parse_version() -> None:
    assert parse_version('v0.1.6') == (0, 1, 6)
    assert parse_version('1.10.2') == (1, 10, 2)


def test_version_lt() -> None:
    assert version_lt('0.1.5', '0.1.6')
    assert not version_lt('0.1.6', '0.1.6')
    assert not version_lt('0.2.0', '0.1.9')
