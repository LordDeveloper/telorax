from __future__ import annotations

import os
from functools import cached_property
from pathlib import Path
from types import SimpleNamespace
from urllib.parse import quote_plus

from pydantic import SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

CONFIG_DIR = Path('/etc/telorax')
ENV_FILENAME = '.env'

_DB_DRIVERS = {
    'mysql': 'mysql+asyncmy',
    'mariadb': 'mysql+asyncmy',
}


def default_env_path() -> Path:
    if override := os.getenv('ENV_FILE'):
        return Path(override)
    return CONFIG_DIR / ENV_FILENAME


def default_config_dir() -> Path:
    return default_env_path().parent


def default_config_path() -> Path:
    return default_env_path()


class Settings(BaseSettings):
    """Flat env configuration loaded from /etc/telorax/.env"""

    model_config = SettingsConfigDict(
        env_file_encoding='utf-8',
        case_sensitive=False,
        extra='ignore',
    )

    # Application
    app_timezone: str = 'UTC'
    app_host: str = '0.0.0.0'
    app_port: int = 8000

    # Auth
    auth_username: str = 'telorax'
    auth_password: SecretStr = SecretStr('changeme')

    # Database
    db_connection: str = 'mysql'
    db_host: str = '127.0.0.1'
    db_port: int = 3306
    db_name: str = 'telorax'
    db_user: str = 'telorax'
    db_password: SecretStr = SecretStr('secret')
    db_pool_size: int = 20
    db_max_overflow: int = 10
    db_echo: bool = False

    # Redis
    redis_host: str = '127.0.0.1'
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: SecretStr | None = None

    # Telegram
    telegram_default_api_id: int = 0
    telegram_default_api_hash: str = ''
    telegram_connection_timeout: int = 1
    telegram_connection_retries: int = 0
    telegram_request_retries: int = 0

    # Worker
    worker_cycle_interval_seconds: int = 15
    worker_max_concurrent_accounts: int = 500
    worker_operation_batch_size: int = 100
    worker_isolated_account_limit: int = 30
    worker_reshot_account_limit: int = 100
    worker_reshot_groups: list[str] = []
    worker_reshot_message_limit: int = 100
    worker_cycle_timeout_seconds: int = 120
    worker_fallback_poll_seconds: int = 60

    # Proxy
    proxy_url: str = ''
    proxy_use_global: bool = False

    # Email (2FA)
    email_username: str = ''
    email_password: SecretStr = SecretStr('')
    email_base_domain: str = ''
    email_default_2fa_password: SecretStr = SecretStr('')

    # Security
    master_key: SecretStr | None = None

    # Logging
    log_level: str = 'INFO'
    log_json: bool = True

    @field_validator('worker_reshot_groups', mode='before')
    @classmethod
    def parse_reshot_groups(cls, value: object) -> list[str]:
        if isinstance(value, str):
            return [group.strip() for group in value.split(',') if group.strip()]
        if isinstance(value, list):
            return value
        return []

    @classmethod
    def load(cls, env_path: Path | None = None) -> Settings:
        path = env_path or default_env_path()
        if path.is_file() and os.access(path, os.R_OK):
            return cls(_env_file=path, _env_file_encoding='utf-8')
        return cls()

    @property
    def env_path(self) -> Path:
        return default_env_path()

    @cached_property
    def database_url(self) -> str:
        driver = _DB_DRIVERS.get(self.db_connection.lower())
        if driver is None:
            msg = f'Unsupported DB_CONNECTION: {self.db_connection}'
            raise ValueError(msg)
        password = quote_plus(self.db_password.get_secret_value())
        user = quote_plus(self.db_user)
        return f'{driver}://{user}:{password}@{self.db_host}:{self.db_port}/{self.db_name}'

    @cached_property
    def redis_url(self) -> str:
        if self.redis_password:
            password = quote_plus(self.redis_password.get_secret_value())
            return f'redis://:{password}@{self.redis_host}:{self.redis_port}/{self.redis_db}'
        return f'redis://{self.redis_host}:{self.redis_port}/{self.redis_db}'

    @cached_property
    def app(self) -> SimpleNamespace:
        return SimpleNamespace(
            timezone=self.app_timezone,
            host=self.app_host,
            port=self.app_port,
        )

    @cached_property
    def auth(self) -> SimpleNamespace:
        return SimpleNamespace(
            username=self.auth_username,
            password=self.auth_password,
        )

    @cached_property
    def database(self) -> SimpleNamespace:
        return SimpleNamespace(
            url=self.database_url,
            pool_size=self.db_pool_size,
            max_overflow=self.db_max_overflow,
            echo=self.db_echo,
        )

    @cached_property
    def redis(self) -> SimpleNamespace:
        return SimpleNamespace(url=self.redis_url)

    @cached_property
    def telegram(self) -> SimpleNamespace:
        return SimpleNamespace(
            default_api_id=self.telegram_default_api_id,
            default_api_hash=self.telegram_default_api_hash,
            connection_timeout=self.telegram_connection_timeout,
            connection_retries=self.telegram_connection_retries,
            request_retries=self.telegram_request_retries,
        )

    @cached_property
    def worker(self) -> SimpleNamespace:
        return SimpleNamespace(
            cycle_interval_seconds=self.worker_cycle_interval_seconds,
            max_concurrent_accounts=self.worker_max_concurrent_accounts,
            operation_batch_size=self.worker_operation_batch_size,
            isolated_account_limit=self.worker_isolated_account_limit,
            reshot_account_limit=self.worker_reshot_account_limit,
            reshot_groups=self.worker_reshot_groups,
            reshot_message_limit=self.worker_reshot_message_limit,
            cycle_timeout_seconds=self.worker_cycle_timeout_seconds,
            fallback_poll_seconds=self.worker_fallback_poll_seconds,
        )

    @cached_property
    def logging(self) -> SimpleNamespace:
        return SimpleNamespace(
            level=self.log_level,
            json_output=self.log_json,
        )
