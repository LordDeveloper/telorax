from __future__ import annotations

from dataclasses import asdict
from typing import Any

from fastapi import APIRouter

from telorax.api.dependencies import HealthServiceDep

router = APIRouter()


@router.get('/status')
async def get_status(health_service: HealthServiceDep) -> dict[str, Any]:
    report = await health_service.get_health_report()
    return {
        'version': report.version,
        'status': report.status,
        'components': [asdict(component) for component in report.components],
    }


@router.get('/health')
async def health_check(health_service: HealthServiceDep) -> dict[str, str]:
    report = await health_service.get_health_report()
    return {'status': report.status}
