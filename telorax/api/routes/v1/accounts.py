from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile

from telorax.api.dependencies import get_account_service
from telorax.api.middleware.auth import verify_api_credentials
from telorax.application.dto.account import ImportSessionDTO, UpdateAccountDTO
from telorax.application.services.account_service import AccountService
from telorax.application.validators.account_validator import parse_account_state
from telorax.core.exceptions import (
    AccountImportError,
    AccountNotFoundError,
    InvalidSessionError,
    OperationValidationError,
)

router = APIRouter(
    prefix='/accounts',
    tags=['accounts'],
    dependencies=[Depends(verify_api_credentials)],
)


@router.get('')
async def list_accounts(
    account_service: Annotated[AccountService, Depends(get_account_service)],
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    state: str | None = Query(default=None),
    country: str | None = Query(default=None),
) -> dict[str, Any]:
    parsed_state = parse_account_state(state) if state else None
    result = await account_service.list_accounts(
        state=parsed_state,
        country_iso=country,
        limit=limit,
        offset=offset,
    )
    return result.to_api_dict()


@router.get('/stats')
async def account_stats(
    account_service: Annotated[AccountService, Depends(get_account_service)],
) -> dict[str, Any]:
    return (await account_service.get_stats()).to_api_dict()


@router.get('/{account_id}')
async def get_account(
    account_id: int,
    account_service: Annotated[AccountService, Depends(get_account_service)],
) -> dict[str, Any]:
    account = await account_service.get_account(account_id)
    if account is None:
        raise HTTPException(status_code=404, detail='Account not found')
    return account.to_api_dict()


@router.patch('/{account_id}')
async def update_account(
    account_id: int,
    payload: dict[str, Any],
    account_service: Annotated[AccountService, Depends(get_account_service)],
) -> dict[str, Any]:
    dto = UpdateAccountDTO(
        state=parse_account_state(payload['state']) if 'state' in payload else None,
        notes=payload.get('notes'),
        proxy_label=payload.get('proxy_label'),
        reliability_score=(
            int(payload['reliability_score']) if 'reliability_score' in payload else None
        ),
    )
    try:
        account = await account_service.update_account(account_id, dto)
    except OperationValidationError as exc:
        raise HTTPException(status_code=422, detail=exc.message) from exc
    except AccountNotFoundError as exc:
        raise HTTPException(status_code=404, detail=exc.message) from exc
    return account.to_api_dict()


@router.post('/{account_id}/deactivate')
async def deactivate_account(
    account_id: int,
    account_service: Annotated[AccountService, Depends(get_account_service)],
) -> dict[str, Any]:
    try:
        account = await account_service.deactivate_account(account_id)
    except AccountNotFoundError as exc:
        raise HTTPException(status_code=404, detail=exc.message) from exc
    return account.to_api_dict()


@router.post('/import', status_code=201)
async def import_session(
    account_service: Annotated[AccountService, Depends(get_account_service)],
    file: UploadFile = File(...),
    password: str | None = Form(default=None),
    ignore_revoke: bool = Form(default=False),
    ignore_2fa: bool = Form(default=False),
    renew: bool = Form(default=True),
) -> dict[str, Any]:
    content = await file.read()
    if not content:
        raise HTTPException(status_code=422, detail='Session file is empty')
    dto = ImportSessionDTO(
        password=password,
        ignore_revoke=ignore_revoke,
        ignore_2fa=ignore_2fa,
        renew=renew,
    )
    try:
        result = await account_service.import_session(content, dto)
    except InvalidSessionError as exc:
        raise HTTPException(status_code=422, detail=exc.detail) from exc
    except AccountImportError as exc:
        raise HTTPException(status_code=422, detail=exc.detail) from exc
    return result.to_api_dict()
