from __future__ import annotations

import asyncio

import typer

from telorax.bootstrap.container import Container
from telorax.cli.commands.config import config_app
from telorax.cli.commands.deps import deps_app
from telorax.cli.commands.migrate import migrate_app
from telorax.cli.commands.version import version_command
from telorax.cli.tui.app import run_dashboard

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
    container = Container()
    container.wire(modules=['telorax.cli.app'])
    health_service = container.health_service()

    async def _run() -> None:
        diagnostics = await health_service.run_diagnostics()
        typer.echo(f'Config path: {diagnostics.config_path}')
        typer.echo(f'Config exists: {diagnostics.config_exists}')
        typer.echo(f'Version: {diagnostics.version}')
        typer.echo(f'Status: {diagnostics.health.status}')
        for component in diagnostics.health.components:
            detail = f' ({component.detail})' if component.detail else ''
            typer.echo(f'  - {component.name}: {component.status}{detail}')

    asyncio.run(_run())


def main() -> None:
    app()


if __name__ == '__main__':
    main()
