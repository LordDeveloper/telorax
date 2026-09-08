from __future__ import annotations

from typing import Annotated, cast

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from telorax.bootstrap.container import Container

security = HTTPBasic()


def verify_api_credentials(
    request: Request,
    credentials: Annotated[HTTPBasicCredentials, Depends(security)],
) -> HTTPBasicCredentials:
    container = cast('Container', request.app.state.container)
    settings = container.config()
    username = settings.auth_username
    password = settings.auth_password.get_secret_value()
    if credentials.username != username or credentials.password != password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid credentials',
            headers={'WWW-Authenticate': 'Basic'},
        )
    return credentials
