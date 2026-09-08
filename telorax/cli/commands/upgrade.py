from __future__ import annotations

import typer

from telorax.cli.actions import run_migrations, run_upgrade, show_upgrade_status

upgrade_app = typer.Typer(help='Upgrade Telorax and migrate between versions')


@upgrade_app.callback(invoke_without_command=True)
def upgrade_root(ctx: typer.Context) -> None:
    if ctx.invoked_subcommand is not None:
        return
    show_upgrade_status()


@upgrade_app.command('check')
def upgrade_check() -> None:
    """Show installed version vs latest release."""
    show_upgrade_status()


@upgrade_app.command('run')
def upgrade_run() -> None:
    """Download latest package, migrate database, and restart service."""
    run_upgrade('run')


@upgrade_app.command('migrate')
def upgrade_migrate() -> None:
    """Run pending database migrations only."""
    run_migrations()
