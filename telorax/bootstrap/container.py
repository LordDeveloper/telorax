from __future__ import annotations

from dependency_injector import containers, providers

from telorax.bootstrap.application import Application
from telorax.core.config.settings import Settings
from telorax.infrastructure.database.engine import create_engine, create_session_factory


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        packages=['telorax.api', 'telorax.cli'],
    )

    config = providers.Singleton(Settings.load)

    db_engine = providers.Singleton(
        create_engine,
        database_url=providers.Callable(lambda cfg: cfg.database_url, config),
        echo=providers.Callable(lambda cfg: cfg.db_echo, config),
    )

    session_factory = providers.Singleton(create_session_factory, engine=db_engine)

    application = providers.Singleton(Application, container=providers.Self())
