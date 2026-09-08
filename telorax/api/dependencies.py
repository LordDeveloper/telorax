from __future__ import annotations

from typing import Annotated, cast

from fastapi import Depends, Request

from telorax.application.services.account_service import AccountService
from telorax.application.services.campaign_service import CampaignService
from telorax.application.services.health_service import HealthService
from telorax.bootstrap.container import Container


def get_health_service(request: Request) -> HealthService:
    container = cast("Container", request.app.state.container)
    return container.health_service()


def get_campaign_service(request: Request) -> CampaignService:
    container = cast("Container", request.app.state.container)
    return container.campaign_service()


def get_account_service(request: Request) -> AccountService:
    container = cast("Container", request.app.state.container)
    return container.account_service()


HealthServiceDep = Annotated[HealthService, Depends(get_health_service)]
CampaignServiceDep = Annotated[CampaignService, Depends(get_campaign_service)]
AccountServiceDep = Annotated[AccountService, Depends(get_account_service)]
