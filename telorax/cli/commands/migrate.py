from __future__ import annotations

from pathlib import Path

import typer
from alembic import command
from alembic.config import Config

from telorax.core.config.settings import Settings

migrate_app = typer.Typer(help='Database migrations')


def _alembic_config() -> Config:
    candidates = (
        Path('/usr/share/telorax/alembic.ini'),
        Path(__file__).resolve().parents[3] / 'alembic.ini',
    )
    for path in candidates:
        if path.is_file():
            cfg = Config(str(path))
            cfg.set_main_option('script_location', str(path.parent / 'migrations'))
            settings = Settings.load()
            cfg.set_main_option('sqlalchemy.url', settings.database_url)
            return cfg
    typer.echo('alembic.ini not found. Reinstall Telorax or run from source checkout.')
    raise typer.Exit(code=1)


def run_migrations() -> None:
    command.upgrade(_alembic_config(), 'head')
    typer.echo('Migrations applied.')


@migrate_app.callback(invoke_without_command=True)
def migrate_default() -> None:
    """Run pending migrations."""
    run_migrations()


@migrate_app.command('revision')
def create_revision(message: str = typer.Option(..., '--message', '-m')) -> None:
    command.revision(_alembic_config(), message=message, autogenerate=True)
    typer.echo(f'Created revision: {message}')
