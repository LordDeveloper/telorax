from __future__ import annotations

from telorax.bootstrap.application import Application
from telorax.bootstrap.container import Container


def test_application_receives_container_instance() -> None:
    container = Container()
    application = Application(container)

    assert application._container is container
    assert application._container.config() is not None
