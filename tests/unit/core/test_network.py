from __future__ import annotations

import socket

import pytest

from telorax.core.network import ensure_port_available, is_port_open, probe_host


def test_probe_host_maps_wildcard() -> None:
    assert probe_host('0.0.0.0') == '127.0.0.1'
    assert probe_host('127.0.0.1') == '127.0.0.1'


def test_ensure_port_available_on_free_port() -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(('127.0.0.1', 0))
        port = sock.getsockname()[1]
    ensure_port_available('127.0.0.1', port)


def test_ensure_port_available_raises_when_port_is_open() -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(('127.0.0.1', 0))
        sock.listen()
        port = sock.getsockname()[1]
        assert is_port_open('127.0.0.1', port)
        with pytest.raises(RuntimeError, match='already in use'):
            ensure_port_available('127.0.0.1', port)
