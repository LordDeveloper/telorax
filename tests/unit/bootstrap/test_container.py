from __future__ import annotations

from telorax.bootstrap.container import Container


def test_container_exposes_core_providers() -> None:
    container = Container()
    assert container.config() is not None
    assert container.health_service() is not None
    assert container.campaign_service() is not None
    assert container.account_service() is not None
