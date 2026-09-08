from __future__ import annotations

import asyncio
import shutil
import subprocess
from http import HTTPStatus
from pathlib import Path

import httpx

from telorax.application.dto.health import HealthReportDTO
from telorax.bootstrap.container import Container
from telorax.core.config.settings import Settings, default_env_path
from telorax.core.network import is_port_open, probe_host

SERVICE_UNIT = 'telorax.service'


def run_doctor() -> None:
    container = Container()
    container.wire(modules=['telorax.cli.actions'])
    health_service = container.health_service()

    async def _run() -> None:
        diagnostics = await health_service.run_diagnostics()
        print(f'Config path: {diagnostics.config_path}')
        print(f'Config exists: {diagnostics.config_exists}')
        print(f'Version: {diagnostics.version}')
        print(f'Status: {diagnostics.health.status}')
        for component in diagnostics.health.components:
            detail = f' ({component.detail})' if component.detail else ''
            print(f'  - {component.name}: {component.status}{detail}')

    asyncio.run(_run())


def fetch_health_report() -> HealthReportDTO:
    container = Container()
    container.wire(modules=['telorax.cli.actions'])
    health_service = container.health_service()
    return asyncio.run(health_service.get_health_report())


def run_deps(action: str) -> None:
    script = _deps_script_path()
    bash = shutil.which('bash')
    if bash is None:
        msg = 'bash is required to manage dependencies.'
        raise RuntimeError(msg)
    subprocess.run([bash, str(script), action], check=True)


def run_config_init() -> None:
    from telorax.cli.commands.config import init_config

    init_config()


def run_config_validate() -> None:
    from telorax.cli.commands.config import validate_config

    validate_config()


def run_migrations() -> None:
    from telorax.cli.commands.migrate import run_migrations as migrate

    migrate()


def run_serve() -> None:
    from telorax.bootstrap.application import Application
    from telorax.bootstrap.container import Container

    container = Container()
    container.wire(modules=['telorax.cli.actions'])
    application = Application(container)
    asyncio.run(application.run_server())


def load_settings_summary() -> tuple[Path, Settings | None]:
    env_path = default_env_path()
    if not env_path.is_file():
        return env_path, None
    return env_path, Settings.load(env_path)


def _deps_script_path() -> Path:
    candidates = (
        Path('/usr/share/telorax/deps.sh'),
        Path(__file__).resolve().parents[2] / 'scripts' / 'deps.sh',
    )
    for path in candidates:
        if path.is_file():
            return path
    msg = 'deps.sh not found. Reinstall Telorax or run install.sh from release assets.'
    raise FileNotFoundError(msg)


def _systemctl_path() -> str:
    systemctl = shutil.which('systemctl')
    if systemctl is None:
        msg = 'systemctl is required to manage the Telorax service.'
        raise RuntimeError(msg)
    return systemctl


def _unit_state(action: str) -> str:
    systemctl = _systemctl_path()
    result = subprocess.run(
        [systemctl, action, SERVICE_UNIT],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout.strip() or 'unknown'


def show_service_status() -> None:
    _, settings = load_settings_summary()
    host = settings.app_host if settings else '0.0.0.0'
    port = settings.app_port if settings else 8000
    target = probe_host(host)

    try:
        print(f'Systemd active: {_unit_state("is-active")}')
        print(f'Systemd enabled: {_unit_state("is-enabled")}')
    except RuntimeError as exc:
        print(f'Systemd: unavailable ({exc})')

    if is_port_open(host, port):
        print(f'Listen {host}:{port}: open on {target}')
        try:
            response = httpx.get(f'http://{target}:{port}/v1/health', timeout=2.0)
            if response.status_code == HTTPStatus.OK:
                payload = response.json()
                status = payload.get('status', '?') if isinstance(payload, dict) else '?'
                print(f'HTTP /v1/health: {status}')
            else:
                print(f'HTTP /v1/health: port in use but not Telorax (HTTP {response.status_code})')
        except Exception as exc:
            print(f'HTTP /v1/health: port in use but not Telorax ({exc})')
    else:
        print(f'Listen {host}:{port}: closed')


def run_service(action: str) -> None:
    systemctl = _systemctl_path()
    if action == 'status':
        show_service_status()
        result = subprocess.run(
            [systemctl, 'status', SERVICE_UNIT, '--no-pager', '-l'],
            check=False,
        )
        if result.returncode != 0:
            raise subprocess.CalledProcessError(result.returncode, result.args)
        return

    subprocess.run([systemctl, action, SERVICE_UNIT], check=True)
    show_service_status()
