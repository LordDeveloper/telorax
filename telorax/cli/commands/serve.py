from __future__ import annotations

import subprocess

import typer

from telorax.cli.actions import run_serve_daemon, run_serve_foreground

serve_app = typer.Typer(help='Manage Telorax API server')


@serve_app.callback(invoke_without_command=True)
def serve_root(ctx: typer.Context) -> None:
    if ctx.invoked_subcommand is not None:
        return
    try:
        run_serve_foreground()
    except RuntimeError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=1) from exc
    except Exception as exc:
        typer.echo(f'Server failed: {exc}', err=True)
        raise typer.Exit(code=1) from exc


@serve_app.command('status')
def serve_status() -> None:
    """Show API server status."""
    try:
        run_serve_daemon('status')
    except subprocess.CalledProcessError as exc:
        raise typer.Exit(code=exc.returncode) from exc


@serve_app.command('start')
def serve_start() -> None:
    """Enable and start Telorax as a persistent systemd service."""
    run_serve_daemon('start')


@serve_app.command('stop')
def serve_stop() -> None:
    """Stop Telorax and disable auto-start on boot."""
    run_serve_daemon('stop')


@serve_app.command('restart')
def serve_restart() -> None:
    """Restart the Telorax systemd service."""
    run_serve_daemon('restart')


@serve_app.command('run')
def serve_run() -> None:
    """Run API server in foreground (stops when the terminal closes)."""
    try:
        run_serve_foreground()
    except RuntimeError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=1) from exc
    except Exception as exc:
        typer.echo(f'Server failed: {exc}', err=True)
        raise typer.Exit(code=1) from exc
