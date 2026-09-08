from __future__ import annotations

from dataclasses import asdict
from typing import Annotated, Any

from fastapi import APIRouter, Depends

from telorax.api.dependencies import get_health_service
from telorax.application.services.health_service import HealthService

router = APIRouter()


@router.get('/status')
async def get_status(
    health_service: Annotated[HealthService, Depends(get_health_service)],
) -> dict[str, Any]:
    report = await health_service.get_health_report()
    return {
        'version': report.version,
        'status': report.status,
        'components': [asdict(component) for component in report.components],
    }


@router.get('/health')
async def health_check() -> dict[str, str]:
    return {'status': 'ok'}
