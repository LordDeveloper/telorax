from __future__ import annotations

import asyncio

import typer

from telorax import __version__
from telorax.bootstrap.container import Container
from telorax.cli.commands.config import config_app
from telorax.cli.commands.deps import deps_app
from telorax.cli.commands.migrate import migrate_app
from telorax.cli.commands.version import version_command
from telorax.cli.tui.app import run_dashboard
from telorax.core.config.settings import default_env_path

app = typer.Typer(
    name='telorax',
    help='Telegram account automation platform',
    no_args_is_help=False,
    invoke_without_command=True,
)

app.add_typer(config_app, name='config')
app.add_typer(deps_app, name='deps')
app.add_typer(migrate_app, name='migrate')


@app.callback(invoke_without_command=True)
def cli_root(ctx: typer.Context) -> None:
    if ctx.invoked_subcommand is None:
        run_dashboard()


@app.command('serve')
def serve_command() -> None:
    """Start API server in headless mode."""
    container = Container()
    container.wire()
    application = container.application()
    asyncio.run(application.run_server())


@app.command('version')
def version_cmd() -> None:
    version_command()


@app.command('doctor')
def doctor_command() -> None:
    """Run system diagnostics."""
    env_path = default_env_path()
    typer.echo(f'Config path: {env_path}')
    typer.echo(f'Config exists: {env_path.is_file()}')
    typer.echo(f'Version: {__version__}')
    typer.echo('Status: OK')


def main() -> None:
    app()


if __name__ == '__main__':
    main()
