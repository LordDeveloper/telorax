from __future__ import annotations

from contextvars import ContextVar
from uuid import uuid4

import structlog

correlation_id_var: ContextVar[str] = ContextVar('correlation_id', default='')
cycle_id_var: ContextVar[str] = ContextVar('cycle_id', default='')


def bind_context(**kwargs: object) -> None:
    structlog.contextvars.bind_contextvars(**kwargs)


def bind_correlation_id(correlation_id: str | None = None) -> str:
    value = correlation_id or uuid4().hex[:12]
    correlation_id_var.set(value)
    bind_context(correlation_id=value)
    return value


def bind_cycle_id(cycle_id: str | None = None) -> str:
    value = cycle_id or uuid4().hex[:8]
    cycle_id_var.set(value)
    bind_context(cycle_id=value)
    return value


def mask_phone(phone: int | str) -> str:
    phone_str = str(phone)
    if len(phone_str) <= 5:
        return '***'
    return f'{phone_str[:5]}***'
