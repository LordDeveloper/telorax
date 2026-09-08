import contextlib
import os
import sys
from http import HTTPStatus
from pathlib import Path

import typer

from telorax.core.config.settings import Settings, default_env_path

config_app = typer.Typer(help='Configuration management')

_PACKAGING_EXAMPLE = Path(__file__).resolve().parents[3] / 'packaging' / 'env.example'


@config_app.command('init')
def init_config() -> None:
    """Create default env file at /etc/telorax/.env"""
    env_path = default_env_path()
    env_path.parent.mkdir(parents=True, exist_ok=True)

    if env_path.exists():
        typer.echo(f'Config already exists: {env_path}')
        raise typer.Exit(code=1)

    content = (
        _PACKAGING_EXAMPLE.read_text(encoding='utf-8')
        if _PACKAGING_EXAMPLE.is_file()
        else _default_env_content()
    )
    env_path.write_text(content, encoding='utf-8')
    with contextlib.suppress(OSError):
        env_path.chmod(0o600)
    if sys.platform != 'win32':
        with contextlib.suppress(OSError):
            import pwd

            account = pwd.getpwnam('telorax')
            os.chown(env_path, account.pw_uid, account.pw_gid)
    typer.echo(f'Created config: {env_path}')


@config_app.command('validate')
def validate_config() -> None:
    """Validate /etc/telorax/.env"""
    env_path = default_env_path()
    if not env_path.is_file():
        typer.echo(f'Config not found: {env_path}')
        raise typer.Exit(code=1)

    settings = Settings.load(env_path)
    typer.echo(f'Config valid: {env_path}')
    typer.echo(f'Listen: {settings.app_host}:{settings.app_port}')
    typer.echo(f'Database: {settings.db_connection}://{settings.db_host}/{settings.db_name}')

    from telorax.core.network import is_port_open, probe_host

    if is_port_open(settings.app_host, settings.app_port):
        target = probe_host(settings.app_host)
        try:
            import httpx

            response = httpx.get(
                f'http://{target}:{settings.app_port}/v1/health',
                timeout=2.0,
            )
            if response.status_code != HTTPStatus.OK:
                typer.secho(
                    f'Warning: port {settings.app_port} is in use but does not look like Telorax.',
                    fg=typer.colors.YELLOW,
                )
        except Exception:
            typer.secho(
                f'Warning: port {settings.app_port} is in use on {target}.',
                fg=typer.colors.YELLOW,
            )


def _default_env_content() -> str:
    return """APP_TIMEZONE=UTC
APP_HOST=0.0.0.0
APP_PORT=8000
AUTH_USERNAME=telorax
AUTH_PASSWORD=changeme
DB_CONNECTION=mysql
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=telorax
DB_USER=telorax
DB_PASSWORD=secret
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
REDIS_DB=0
LOG_LEVEL=INFO
LOG_JSON=true
"""
