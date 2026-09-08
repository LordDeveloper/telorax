from __future__ import annotations

import asyncio
import shutil
import subprocess
from pathlib import Path

from telorax.application.dto.health import HealthReportDTO
from telorax.bootstrap.container import Container
from telorax.core.config.settings import Settings, default_env_path


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
