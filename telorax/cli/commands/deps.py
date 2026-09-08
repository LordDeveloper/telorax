from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import typer

deps_app = typer.Typer(help='Install and manage MariaDB/MySQL and Redis')


def _deps_script_path() -> Path:
    candidates = (
        Path('/usr/share/telorax/deps.sh'),
        Path(__file__).resolve().parents[3] / 'scripts' / 'deps.sh',
    )
    for path in candidates:
        if path.is_file():
            return path
    typer.echo('deps.sh not found. Reinstall Telorax or run install.sh from release assets.')
    raise typer.Exit(code=1)


def _run_deps(action: str) -> None:
    script = _deps_script_path()
    bash = shutil.which('bash')
    if bash is None:
        typer.echo('bash is required to manage dependencies.')
        raise typer.Exit(code=1)
    subprocess.run([bash, str(script), action], check=True)


@deps_app.command('install')
def install_deps() -> None:
    """Install MariaDB/MySQL and Redis, then provision the Telorax database."""
    _run_deps('install')


@deps_app.command('status')
def status_deps() -> None:
    """Show dependency service and connectivity status."""
    _run_deps('status')


@deps_app.command('start')
def start_deps() -> None:
    """Start MariaDB/MySQL and Redis."""
    _run_deps('start')


@deps_app.command('stop')
def stop_deps() -> None:
    """Stop MariaDB/MySQL and Redis."""
    _run_deps('stop')


@deps_app.command('restart')
def restart_deps() -> None:
    """Restart MariaDB/MySQL and Redis."""
    _run_deps('restart')


@deps_app.command('provision')
def provision_deps() -> None:
    """Create or update Telorax database and user from /etc/telorax/.env."""
    _run_deps('provision')
