from __future__ import annotations

import typer

from telorax.cli.actions import run_service, show_service_status

service_app = typer.Typer(help='Manage Telorax systemd service')


@service_app.command('status')
def status_service() -> None:
    """Show Telorax service, port, and HTTP health."""
    show_service_status()


@service_app.command('start')
def start_service() -> None:
    """Start Telorax via systemd."""
    run_service('start')


@service_app.command('stop')
def stop_service() -> None:
    """Stop Telorax via systemd."""
    run_service('stop')


@service_app.command('restart')
def restart_service() -> None:
    """Restart Telorax via systemd."""
    run_service('restart')
