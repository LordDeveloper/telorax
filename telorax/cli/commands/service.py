from __future__ import annotations

import subprocess

import typer

from telorax.cli.actions import run_serve_daemon

service_app = typer.Typer(help='Manage Telorax systemd service (alias for telorax serve)')


@service_app.command('status')
def status_service() -> None:
    """Show Telorax service, port, and HTTP health."""
    try:
        run_serve_daemon('status')
    except subprocess.CalledProcessError as exc:
        raise typer.Exit(code=exc.returncode) from exc


@service_app.command('start')
def start_service() -> None:
    """Enable and start Telorax via systemd."""
    run_serve_daemon('start')


@service_app.command('stop')
def stop_service() -> None:
    """Stop Telorax and disable auto-start on boot."""
    run_serve_daemon('stop')


@service_app.command('restart')
def restart_service() -> None:
    """Restart Telorax via systemd."""
    run_serve_daemon('restart')
