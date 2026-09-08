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
from telorax.core.version import version_lt

SERVICE_UNIT = 'telorax.service'
GITHUB_REPO = 'LordDeveloper/telorax'


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


def fetch_latest_release_version() -> str:
    response = httpx.get(
        f'https://api.github.com/repos/{GITHUB_REPO}/releases/latest',
        timeout=10.0,
        headers={'Accept': 'application/vnd.github+json'},
    )
    response.raise_for_status()
    payload = response.json()
    tag = payload.get('tag_name')
    if not isinstance(tag, str) or not tag:
        msg = 'Could not resolve latest release tag.'
        raise RuntimeError(msg)
    return tag.lstrip('v')


def show_upgrade_status() -> None:
    script = _upgrade_script_path()
    bash = shutil.which('bash')
    if script.is_file() and bash is not None:
        subprocess.run([bash, str(script), 'check'], check=False)
        return

    from telorax import __version__

    installed = __version__
    print(f'Installed: {installed}')

    try:
        latest = fetch_latest_release_version()
    except Exception as exc:
        print(f'Latest:    unavailable ({exc})')
        return

    print(f'Latest:    {latest}')
    if version_lt(installed, latest):
        print('Status:    update available')
    elif installed == latest:
        print('Status:    up to date')
    else:
        print('Status:    installed version is ahead of latest release')


def run_upgrade(action: str) -> None:
    script = _upgrade_script_path()
    bash = shutil.which('bash')
    if bash is None:
        msg = 'bash is required to upgrade Telorax.'
        raise RuntimeError(msg)
    if not script.is_file():
        msg = 'upgrade.sh not found. Reinstall Telorax or run install.sh from release assets.'
        raise FileNotFoundError(msg)
    subprocess.run([bash, str(script), action], check=True)


def run_serve_foreground() -> None:
    from telorax.bootstrap.application import Application
    from telorax.bootstrap.container import Container

    container = Container()
    container.wire(modules=['telorax.cli.actions'])
    application = Application(container)
    asyncio.run(application.run_server())


def run_serve_daemon(action: str) -> None:
    systemctl = _systemctl_path()
    if action == 'status':
        show_service_status()
        subprocess.run(
            [systemctl, 'status', SERVICE_UNIT, '--no-pager', '-l'],
            check=False,
        )
        return

    if action == 'start':
        subprocess.run([systemctl, 'enable', '--now', SERVICE_UNIT], check=True)
    elif action == 'stop':
        subprocess.run([systemctl, 'disable', '--now', SERVICE_UNIT], check=True)
    elif action == 'restart':
        subprocess.run([systemctl, 'restart', SERVICE_UNIT], check=True)
    else:
        msg = f'Unknown serve action: {action}'
        raise RuntimeError(msg)

    show_service_status()


def run_service(action: str) -> None:
    run_serve_daemon(action)


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


def _upgrade_script_path() -> Path:
    candidates = (
        Path('/usr/share/telorax/upgrade.sh'),
        Path(__file__).resolve().parents[2] / 'scripts' / 'upgrade.sh',
    )
    for path in candidates:
        if path.is_file():
            return path
    return candidates[1]


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
