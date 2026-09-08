from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from telorax import __version__
from telorax.api.routes.v1.accounts import router as accounts_router
from telorax.api.routes.v1.operations import router as operations_router
from telorax.api.routes.v1.status import router as status_router

if TYPE_CHECKING:
    from telorax.bootstrap.container import Container

_INSTALLED_DOCS_DIR = Path('/usr/share/telorax/docs')
_DEV_DOCS_DIR = Path(__file__).resolve().parents[2] / 'docs' / 'dist'


def _resolve_docs_dir() -> Path | None:
    if override := os.environ.get('TELORAX_DOCS_DIR'):
        path = Path(override)
        if path.is_dir() and (path / 'index.html').is_file():
            return path
    for candidate in (_INSTALLED_DOCS_DIR, _DEV_DOCS_DIR):
        if candidate.is_dir() and (candidate / 'index.html').is_file():
            return candidate
    return None


def create_fastapi_app(container: Container) -> FastAPI:
    app = FastAPI(
        title='Telorax API',
        version=__version__,
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
    )
    app.state.container = container
    app.include_router(status_router, prefix='/v1', tags=['status'])
    app.include_router(operations_router, prefix='/v1')
    app.include_router(accounts_router, prefix='/v1')

    docs_dir = _resolve_docs_dir()
    if docs_dir is not None:
        app.mount('/docs', StaticFiles(directory=docs_dir, html=True), name='docs')

        @app.get('/', include_in_schema=False)
        async def root_redirect() -> RedirectResponse:
            return RedirectResponse(url='/docs/')

    return app
