from __future__ import annotations

from fastapi import APIRouter

from telorax import __version__

router = APIRouter()


@router.get('/status')
async def get_status() -> dict[str, object]:
    return {
        'version': __version__,
        'server': 'running',
        'worker': 'idle',
    }


@router.get('/health')
async def health_check() -> dict[str, object]:
    return {'status': 'healthy'}
