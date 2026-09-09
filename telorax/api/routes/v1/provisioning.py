from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, Response, UploadFile

from telorax.api.dependencies import get_provisioning_service
from telorax.api.middleware.agent_auth import verify_signup_agent
from telorax.api.middleware.auth import verify_api_credentials
from telorax.application.dto.provisioning import (
    CompleteProvisioningJobDTO,
    CreateProvisioningJobDTO,
)
from telorax.application.services.provisioning_service import (
    ProvisioningJobNotFoundError,
    ProvisioningService,
)
from telorax.core.enums import ProvisioningState
from telorax.core.exceptions import OperationValidationError

router = APIRouter(prefix='/provisioning', tags=['provisioning'])


@router.post('/jobs', status_code=201, dependencies=[Depends(verify_api_credentials)])
async def create_provisioning_job(
    payload: dict[str, Any],
    provisioning_service: Annotated[ProvisioningService, Depends(get_provisioning_service)],
) -> dict[str, Any]:
    dto = CreateProvisioningJobDTO(
        msisdn=int(payload['msisdn']),
        first_name=str(payload['first_name']),
        last_name=str(payload['last_name']),
        country_iso=payload.get('country_iso'),
        two_factor_password=payload.get('two_factor_password'),
        provider=str(payload.get('provider') or 'android-agent'),
        metadata=dict(payload.get('metadata') or {}),
    )
    try:
        job = await provisioning_service.create_job(dto)
    except OperationValidationError as exc:
        raise HTTPException(status_code=422, detail=exc.message) from exc
    return job.to_api_dict()


@router.get('/jobs', dependencies=[Depends(verify_api_credentials)])
async def list_provisioning_jobs(
    provisioning_service: Annotated[ProvisioningService, Depends(get_provisioning_service)],
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    state: str | None = Query(default=None),
) -> list[dict[str, Any]]:
    parsed_state = ProvisioningState[state.upper()] if state else None
    jobs = await provisioning_service.list_jobs(state=parsed_state, limit=limit, offset=offset)
    return [job.to_api_dict() for job in jobs]


@router.get('/jobs/{job_id}', dependencies=[Depends(verify_api_credentials)])
async def get_provisioning_job(
    job_id: int,
    provisioning_service: Annotated[ProvisioningService, Depends(get_provisioning_service)],
) -> dict[str, Any]:
    job = await provisioning_service.get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail='Provisioning job not found')
    return job.to_api_dict()


@router.patch('/jobs/{job_id}/metadata', dependencies=[Depends(verify_api_credentials)])
async def patch_provisioning_job_metadata(
    job_id: int,
    payload: dict[str, Any],
    provisioning_service: Annotated[ProvisioningService, Depends(get_provisioning_service)],
) -> dict[str, Any]:
    try:
        job = await provisioning_service.update_job_metadata(job_id, updates=dict(payload))
    except ProvisioningJobNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except OperationValidationError as exc:
        raise HTTPException(status_code=422, detail=exc.message) from exc
    return job.to_api_dict()


agent_router = APIRouter(
    prefix='/provisioning/agent',
    tags=['provisioning-agent'],
    dependencies=[Depends(verify_signup_agent)],
)


@agent_router.post('/claim')
async def claim_provisioning_job(
    payload: dict[str, Any],
    agent_id: Annotated[str, Depends(verify_signup_agent)],
    provisioning_service: Annotated[ProvisioningService, Depends(get_provisioning_service)],
    response: Response,
) -> dict[str, Any] | None:
    provider = str(payload.get('provider') or 'android-agent')
    job = await provisioning_service.claim_next_job(provider=provider, agent_id=agent_id)
    if job is None:
        response.status_code = 204
        return None
    return job.to_api_dict()


@agent_router.get('/jobs/{job_id}')
async def get_claimed_provisioning_job(
    job_id: int,
    agent_id: Annotated[str, Depends(verify_signup_agent)],
    provisioning_service: Annotated[ProvisioningService, Depends(get_provisioning_service)],
) -> dict[str, Any]:
    job = await provisioning_service.get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail='Provisioning job not found')
    if job.agent_id != agent_id or job.state is not ProvisioningState.CLAIMED:
        raise HTTPException(status_code=403, detail='Job is not claimed by this agent')
    return job.to_api_dict()


@agent_router.patch('/jobs/{job_id}/metadata')
async def patch_claimed_provisioning_job_metadata(
    job_id: int,
    payload: dict[str, Any],
    agent_id: Annotated[str, Depends(verify_signup_agent)],
    provisioning_service: Annotated[ProvisioningService, Depends(get_provisioning_service)],
) -> dict[str, Any]:
    try:
        job = await provisioning_service.update_job_metadata(
            job_id,
            updates=dict(payload),
            agent_id=agent_id,
        )
    except ProvisioningJobNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except OperationValidationError as exc:
        raise HTTPException(status_code=422, detail=exc.message) from exc
    return job.to_api_dict()


@agent_router.post('/jobs/{job_id}/complete')
async def complete_provisioning_job(
    job_id: int,
    agent_id: Annotated[str, Depends(verify_signup_agent)],
    provisioning_service: Annotated[ProvisioningService, Depends(get_provisioning_service)],
    file: UploadFile = File(...),
    ignore_revoke: bool = Form(default=False),
    ignore_2fa: bool = Form(default=False),
    renew: bool = Form(default=True),
) -> dict[str, Any]:
    content = await file.read()
    if not content:
        raise HTTPException(status_code=422, detail='Session file is empty')
    options = CompleteProvisioningJobDTO(
        ignore_revoke=ignore_revoke,
        ignore_2fa=ignore_2fa,
        renew=renew,
    )
    try:
        job = await provisioning_service.complete_job(
            job_id,
            agent_id=agent_id,
            session_content=content,
            options=options,
        )
    except ProvisioningJobNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except OperationValidationError as exc:
        raise HTTPException(status_code=422, detail=exc.message) from exc
    return job.to_api_dict()


@agent_router.post('/jobs/{job_id}/fail')
async def fail_provisioning_job(
    job_id: int,
    payload: dict[str, Any],
    agent_id: Annotated[str, Depends(verify_signup_agent)],
    provisioning_service: Annotated[ProvisioningService, Depends(get_provisioning_service)],
) -> dict[str, Any]:
    reason = str(payload.get('reason') or 'Signup failed')
    try:
        job = await provisioning_service.fail_job(job_id, agent_id=agent_id, reason=reason)
    except ProvisioningJobNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except OperationValidationError as exc:
        raise HTTPException(status_code=422, detail=exc.message) from exc
    return job.to_api_dict()
