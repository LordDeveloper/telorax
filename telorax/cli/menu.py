from __future__ import annotations

import shutil
import subprocess
import sys
from typing import TYPE_CHECKING

from telorax import __version__
from telorax.cli import actions
from telorax.cli.console import (
    CYAN,
    DIM,
    GREEN,
    LOGO,
    MAGENTA,
    RED,
    TAGLINE,
    WHITE,
    YELLOW,
    Choice,
    clear_screen,
    confirm,
    double_line,
    enable_ansi,
    is_interactive,
    kv,
    paint,
    pause,
    select,
    show_cursor,
)
from telorax.core.config.settings import default_env_path

if TYPE_CHECKING:
    from collections.abc import Callable


def _print(text: str = '') -> None:
    print(text)


def _status_color(status: str) -> str:
    if status == 'ok':
        return GREEN
    if status == 'down':
        return RED
    return YELLOW


def render_header(subtitle: str | None = None) -> None:
    clear_screen()
    _print(paint(LOGO, CYAN))
    _print()
    _print(paint(f' {TAGLINE}', WHITE))
    if subtitle:
        _print(paint(f' {subtitle}', DIM))
    _print()
    _print(double_line())
    _print(kv('Version', f'v{__version__}', GREEN))
    _print(kv('Config', str(default_env_path()), CYAN))
    _print(double_line())

    try:
        report = actions.fetch_health_report()
        _print(kv('Overall', report.status, _status_color(report.status)))
        for component in report.components:
            _print(kv(component.name.capitalize(), component.status, _status_color(component.status)))
    except Exception as exc:
        _print(kv('Health', 'unavailable', RED))
        _print(paint(f' {exc}', DIM))
    _print(double_line())
    _print()


def _run_action(title: str, fn: Callable[[], None]) -> None:
    render_header(title)
    try:
        fn()
    except subprocess.CalledProcessError as exc:
        _print(paint(f'\n Command failed with exit code {exc.returncode}.', RED))
    except FileNotFoundError as exc:
        _print(paint(f'\n {exc}', RED))
    except RuntimeError as exc:
        _print(paint(f'\n {exc}', RED))
    except KeyboardInterrupt:
        _print(paint('\n Cancelled.', YELLOW))
    pause()


def _show_doctor() -> None:
    actions.run_doctor()


def _show_config() -> None:
    env_path, settings = actions.load_settings_summary()
    _print(kv('Path', str(env_path), CYAN))
    if settings is None:
        _print(paint(' Config file not found.', YELLOW))
        return
    _print(kv('Listen', f'{settings.app_host}:{settings.app_port}', GREEN))
    _print(kv('Database', f'{settings.db_host}:{settings.db_port}/{settings.db_name}', GREEN))
    _print(kv('Redis', f'{settings.redis_host}:{settings.redis_port}', GREEN))


def _deps_menu() -> None:
    while True:
        render_header('Dependencies')
        picked = select(
            [
                Choice('status', 'Show status', CYAN, '1'),
                Choice('install', 'Install MariaDB + Redis', GREEN, '2'),
                Choice('provision', 'Provision database user', YELLOW, '3'),
                Choice('restart', 'Restart dependency services', WHITE, '4'),
                Choice('back', 'Back', WHITE, '0'),
            ],
        )
        if picked in {None, 'back'}:
            return
        if picked == 'status':
            _run_action('Dependency status', lambda: actions.run_deps('status'))
            continue
        if picked == 'install':
            if not confirm('Install local MariaDB and Redis under /opt/telorax?', default=True):
                continue
            _run_action('Install dependencies', lambda: actions.run_deps('install'))
            continue
        if picked == 'provision':
            _run_action('Provision database', lambda: actions.run_deps('provision'))
            continue
        if picked == 'restart':
            _run_action('Restart dependencies', lambda: actions.run_deps('restart'))


def _config_menu() -> None:
    while True:
        render_header('Configuration')
        picked = select(
            [
                Choice('show', 'Show current config', CYAN, '1'),
                Choice('init', 'Create default .env', GREEN, '2'),
                Choice('validate', 'Validate .env', YELLOW, '3'),
                Choice('back', 'Back', WHITE, '0'),
            ],
        )
        if picked in {None, 'back'}:
            return
        if picked == 'show':
            _run_action('Configuration', _show_config)
            continue
        if picked == 'init':
            _run_action('Initialize config', actions.run_config_init)
            continue
        if picked == 'validate':
            _run_action('Validate config', actions.run_config_validate)


def _setup_wizard() -> None:
    render_header('Setup wizard')
    env_path = default_env_path()
    if env_path.is_file():
        _print(paint(f' Config already exists: {env_path}', YELLOW))
    elif confirm('Create default config at /etc/telorax/.env?', default=True):
        actions.run_config_init()

    if confirm('Install local MariaDB and Redis now?', default=True):
        actions.run_deps('install')
    elif confirm('Provision database from existing .env?', default=True):
        actions.run_deps('provision')

    if confirm('Run database migrations now?', default=True):
        actions.run_migrations()

    _show_doctor()
    pause()


def _service_menu() -> None:
    while True:
        render_header('Telorax service')
        picked = select(
            [
                Choice('status', 'Show status', CYAN, '1'),
                Choice('start', 'Start service', GREEN, '2'),
                Choice('stop', 'Stop service', RED, '3'),
                Choice('restart', 'Restart service', YELLOW, '4'),
                Choice('foreground', 'Run in foreground', WHITE, '5'),
                Choice('back', 'Back', WHITE, '0'),
            ],
        )
        if picked in {None, 'back'}:
            return
        if picked == 'status':
            _run_action('Service status', lambda: actions.run_service('status'))
            continue
        if picked == 'start':
            _run_action('Start service', lambda: actions.run_service('start'))
            continue
        if picked == 'stop':
            if not confirm('Stop Telorax service?', default=False):
                continue
            _run_action('Stop service', lambda: actions.run_service('stop'))
            continue
        if picked == 'restart':
            _run_action('Restart service', lambda: actions.run_service('restart'))
            continue
        if picked == 'foreground':
            _run_action('Foreground server', _serve_hint)


def _serve_hint() -> None:
    _print(paint(' Start the API server with:', CYAN))
    _print(paint('   telorax serve', GREEN))
    _print()
    _print(paint(' Requires a free APP_PORT. Check with:', DIM))
    _print(paint('   telorax service status', GREEN))
    _print()
    _print(paint(' Or manage the systemd unit:', DIM))
    _print(paint('   sudo systemctl enable --now telorax', GREEN))


def run_interactive() -> int:
    if not is_interactive():
        print('Interactive menu needs a TTY. Use: telorax --help', file=sys.stderr)
        return 2

    enable_ansi()
    columns = shutil.get_terminal_size((80, 24)).columns
    if columns < 48:
        print('Widen the terminal a bit, then run telorax again.', file=sys.stderr)
        return 2

    try:
        while True:
            render_header()
            picked = select(
                [
                    Choice('wizard', 'Setup wizard', GREEN, '1'),
                    Choice('deps', 'Dependencies', CYAN, '2'),
                    Choice('config', 'Configuration', YELLOW, '3'),
                    Choice('migrate', 'Run migrations', WHITE, '4'),
                    Choice('doctor', 'Diagnostics', MAGENTA, '5'),
                    Choice('service', 'Telorax service', GREEN, '6'),
                    Choice('exit', 'Exit', WHITE, '0'),
                ],
            )
            if picked in {None, 'exit'}:
                show_cursor()
                return 0
            if picked == 'wizard':
                _setup_wizard()
            elif picked == 'deps':
                _deps_menu()
            elif picked == 'config':
                _config_menu()
            elif picked == 'migrate':
                _run_action('Migrations', actions.run_migrations)
            elif picked == 'doctor':
                _run_action('Diagnostics', _show_doctor)
            elif picked == 'service':
                _service_menu()
    except KeyboardInterrupt:
        show_cursor()
        return 130
