from __future__ import annotations

from dependency_injector import containers, providers

from telorax.application.services.account_service import AccountService
from telorax.application.services.health_service import HealthService
from telorax.application.services.operation_service import OperationService
from telorax.bootstrap.application import Application
from telorax.core.config.settings import Settings
from telorax.infrastructure.database.engine import create_engine, create_session_factory


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        packages=['telorax.api', 'telorax.cli'],
    )

    __self__ = providers.Self()

    config = providers.Singleton(Settings.load)

    db_engine = providers.Singleton(
        create_engine,
        database_url=providers.Callable(lambda cfg: cfg.database_url, config),
        echo=providers.Callable(lambda cfg: cfg.db_echo, config),
    )

    session_factory = providers.Singleton(create_session_factory, engine=db_engine)

    health_service = providers.Singleton(
        HealthService,
        settings=config,
        db_engine=db_engine,
    )

    operation_service = providers.Singleton(
        OperationService,
        session_factory=session_factory,
    )

    account_service = providers.Singleton(
        AccountService,
        session_factory=session_factory,
    )

    application = providers.Singleton(Application, container=__self__)
