from __future__ import annotations

from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import Depends

from telorax.application.services.account_service import AccountService
from telorax.application.services.campaign_service import CampaignService
from telorax.application.services.health_service import HealthService
from telorax.bootstrap.container import Container


@inject
def get_health_service(
    service: HealthService = Provide[Container.health_service],
) -> HealthService:
    return service


@inject
def get_campaign_service(
    service: CampaignService = Provide[Container.campaign_service],
) -> CampaignService:
    return service


@inject
def get_account_service(
    service: AccountService = Provide[Container.account_service],
) -> AccountService:
    return service


HealthServiceDep = Annotated[HealthService, Depends(get_health_service)]
CampaignServiceDep = Annotated[CampaignService, Depends(get_campaign_service)]
AccountServiceDep = Annotated[AccountService, Depends(get_account_service)]
