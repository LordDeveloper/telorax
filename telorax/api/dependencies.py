from __future__ import annotations

from typing import cast

from fastapi import Request

from telorax.application.services.account_service import AccountService
from telorax.application.services.health_service import HealthService
from telorax.application.services.operation_service import OperationService
from telorax.bootstrap.container import Container


def get_health_service(request: Request) -> HealthService:
    container = cast('Container', request.app.state.container)
    return container.health_service()


def get_operation_service(request: Request) -> OperationService:
    container = cast('Container', request.app.state.container)
    return container.operation_service()


def get_account_service(request: Request) -> AccountService:
    container = cast('Container', request.app.state.container)
    return container.account_service()
