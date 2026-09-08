import typer

from telorax import __version__


def version_command() -> None:
    typer.echo(f'telorax v{__version__}')
