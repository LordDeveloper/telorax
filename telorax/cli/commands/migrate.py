import typer

migrate_app = typer.Typer(help='Database migrations')


@migrate_app.callback(invoke_without_command=True)
def migrate_default() -> None:
    """Run pending migrations."""
    typer.echo('Running migrations...')
    typer.echo('Migration runner will be wired in Phase 2.')


@migrate_app.command('revision')
def create_revision(message: str = typer.Option(..., '--message', '-m')) -> None:
    typer.echo(f'Creating revision: {message}')
