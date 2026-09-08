from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import FastAPI

from telorax import __version__
from telorax.api.routes.v1.campaigns import router as campaigns_router
from telorax.api.routes.v1.status import router as status_router

if TYPE_CHECKING:
    from telorax.bootstrap.container import Container


def create_fastapi_app(container: Container) -> FastAPI:
    app = FastAPI(title='Telorax API', version=__version__)
    app.state.container = container
    app.include_router(status_router, prefix='/v1', tags=['status'])
    app.include_router(campaigns_router, prefix='/v1')
    return app
