from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query

from telorax.api.dependencies import get_mobile_agent_service
from telorax.api.middleware.agent_auth import verify_signup_agent
from telorax.application.dto.mobile_agent import (
    MobileAgentHeartbeatDTO,
    MobileAgentRegisterDTO,
)
from telorax.application.services.mobile_agent_service import MobileAgentService

router = APIRouter(
    prefix='/mobile-agent',
    tags=['mobile-agent'],
    dependencies=[Depends(verify_signup_agent)],
)


@router.post('/register')
async def register_mobile_agent(
    payload: dict[str, Any],
    agent_id: Annotated[str, Depends(verify_signup_agent)],
    mobile_agent_service: Annotated[MobileAgentService, Depends(get_mobile_agent_service)],
) -> dict[str, str]:
    raw_capabilities = dict(payload.get('capabilities') or {})
    dto = MobileAgentRegisterDTO(
        platform=str(payload.get('platform') or 'android'),
        arch=str(payload.get('arch') or 'arm64'),
        version=str(payload.get('version') or '0.0.0'),
        capabilities=mobile_agent_service.parse_capabilities(raw_capabilities),
    )
    return mobile_agent_service.register(agent_id, dto)


@router.post('/heartbeat')
async def mobile_agent_heartbeat(
    payload: dict[str, Any],
    agent_id: Annotated[str, Depends(verify_signup_agent)],
    mobile_agent_service: Annotated[MobileAgentService, Depends(get_mobile_agent_service)],
) -> dict[str, str]:
    raw_capabilities = dict(payload.get('capabilities') or {})
    dto = MobileAgentHeartbeatDTO(
        status=str(payload.get('status') or 'online'),
        capabilities=mobile_agent_service.parse_capabilities(raw_capabilities),
        tunnel_up=bool(payload.get('tunnel_up')),
    )
    return mobile_agent_service.heartbeat(agent_id, dto)


@router.get('/config')
async def mobile_agent_config(
    agent_id: Annotated[str, Depends(verify_signup_agent)],
    mobile_agent_service: Annotated[MobileAgentService, Depends(get_mobile_agent_service)],
) -> dict[str, Any]:
    return mobile_agent_service.get_config(agent_id).to_api_dict()


@router.get('/updates/check')
async def mobile_agent_update_check(
    agent_id: Annotated[str, Depends(verify_signup_agent)],
    mobile_agent_service: Annotated[MobileAgentService, Depends(get_mobile_agent_service)],
    version: str = Query(default='0.0.0'),
    platform: str = Query(default='android'),
    arch: str = Query(default='arm64'),
) -> dict[str, Any]:
    _ = agent_id
    result = mobile_agent_service.check_update(
        current_version=version,
        platform=platform,
        arch=arch,
    )
    return result.to_api_dict()
