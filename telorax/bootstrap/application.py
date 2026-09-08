from __future__ import annotations

import asyncio
import contextlib
import signal
from typing import TYPE_CHECKING

import structlog
import uvicorn

from telorax import __version__
from telorax.api.app import create_fastapi_app
from telorax.core.logging import configure_logging

if TYPE_CHECKING:
    from telorax.bootstrap.container import Container

log = structlog.get_logger(__name__)


class Application:
    def __init__(self, container: Container) -> None:
        self._container = container
        self._shutdown_event = asyncio.Event()

    async def start(self) -> None:
        settings = self._container.config()
        configure_logging(
            level=settings.logging.level,
            json_output=settings.logging.json_output,
        )
        log.info('application.started', version=__version__)

    async def stop(self) -> None:
        engine = self._container.db_engine()
        await engine.dispose()
        log.info('application.stopped')

    async def run_server(self) -> None:
        await self.start()
        settings = self._container.config()
        app = create_fastapi_app(self._container)

        config = uvicorn.Config(
            app,
            host=settings.app.host,
            port=settings.app.port,
            log_level=settings.logging.level.lower(),
        )
        server = uvicorn.Server(config)

        serve_task = asyncio.create_task(server.serve())
        if hasattr(signal, 'SIGTERM'):
            loop = asyncio.get_running_loop()
            for sig in (signal.SIGINT, signal.SIGTERM):
                with contextlib.suppress(NotImplementedError):
                    loop.add_signal_handler(sig, self._shutdown_event.set)
        await self._shutdown_event.wait()
        server.should_exit = True
        await serve_task
        await self.stop()
