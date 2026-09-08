from __future__ import annotations

from typing import Annotated, cast

from fastapi import Header, HTTPException, Request, status

from telorax.bootstrap.container import Container


def verify_signup_agent(
    request: Request,
    agent_token: Annotated[str | None, Header(alias='X-Telorax-Agent-Token')] = None,
    agent_id: Annotated[str | None, Header(alias='X-Telorax-Agent-Id')] = None,
) -> str:
    if not agent_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='X-Telorax-Agent-Id header is required',
        )
    container = cast('Container', request.app.state.container)
    settings = container.config()
    expected = settings.signup_agent_token.get_secret_value() if settings.signup_agent_token else ''
    if not expected or agent_token != expected:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid agent token',
        )
    return agent_id
