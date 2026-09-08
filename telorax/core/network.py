from __future__ import annotations

import socket


def probe_host(host: str) -> str:
    if host in {'0.0.0.0', '::', ''}:
        return '127.0.0.1'
    return host


def is_port_open(host: str, port: int, *, timeout: float = 0.5) -> bool:
    target = probe_host(host)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(timeout)
        return sock.connect_ex((target, port)) == 0


def ensure_port_available(host: str, port: int) -> None:
    if is_port_open(host, port):
        target = probe_host(host)
        msg = (
            f'Port {port} is already in use on {target}. '
            'Stop the conflicting service or set a different APP_PORT in .env.'
        )
        raise RuntimeError(msg)
