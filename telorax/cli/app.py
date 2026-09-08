from __future__ import annotations

import typer

from telorax.cli.commands.config import config_app
from telorax.cli.commands.deps import deps_app
from telorax.cli.commands.migrate import migrate_app
from telorax.cli.commands.serve import serve_app
from telorax.cli.commands.service import service_app
from telorax.cli.commands.signup_agent import signup_agent_app
from telorax.cli.commands.upgrade import upgrade_app
from telorax.cli.commands.version import version_command
from telorax.cli.console import is_interactive
from telorax.cli.menu import run_interactive

app = typer.Typer(
    name='telorax',
    help='Telegram account automation platform',
    no_args_is_help=False,
    invoke_without_command=True,
)

app.add_typer(config_app, name='config')
app.add_typer(deps_app, name='deps')
app.add_typer(migrate_app, name='migrate')
app.add_typer(serve_app, name='serve')
app.add_typer(service_app, name='service')
app.add_typer(signup_agent_app, name='signup-agent')
app.add_typer(upgrade_app, name='upgrade')


@app.callback(invoke_without_command=True)
def cli_root(ctx: typer.Context) -> None:
    if ctx.invoked_subcommand is not None:
        return
    if is_interactive():
        raise typer.Exit(run_interactive())
    typer.echo(ctx.get_help())


@app.command('version')
def version_cmd() -> None:
    version_command()


@app.command('doctor')
def doctor_command() -> None:
    """Run system diagnostics."""
    from telorax.cli.actions import run_doctor

    run_doctor()


def main() -> None:
    try:
        app()
    except KeyboardInterrupt:
        raise typer.Exit(code=130) from None


if __name__ == '__main__':
    main()
