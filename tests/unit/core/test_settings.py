from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import SecretStr

from telorax.core.config.settings import Settings


def test_default_settings() -> None:
    settings = Settings()
    assert settings.app_port == 8000
    assert settings.worker_max_concurrent_accounts == 500


def test_auth_password_is_secret() -> None:
    settings = Settings(auth_password=SecretStr('secret'))
    assert isinstance(settings.auth_password, SecretStr)


def test_database_url_is_generated() -> None:
    settings = Settings(
        db_connection='mysql',
        db_host='10.0.0.5',
        db_port=3306,
        db_name='telorax_prod',
        db_user='telorax',
        db_password=SecretStr('p@ss:word'),
    )
    assert settings.database_url == (
        'mysql+asyncmy://telorax:p%40ss%3Aword@10.0.0.5:3306/telorax_prod'
    )


def test_redis_url_without_password() -> None:
    settings = Settings(redis_host='127.0.0.1', redis_port=6379, redis_db=2)
    assert settings.redis_url == 'redis://127.0.0.1:6379/2'


def test_load_from_env_file(tmp_path: Path) -> None:
    env_file = tmp_path / '.env'
    env_file.write_text(
        'APP_PORT=9000\nAUTH_USERNAME=admin\nDB_NAME=custom_db\n',
        encoding='utf-8',
    )
    settings = Settings.load(env_file)
    assert settings.app_port == 9000
    assert settings.auth_username == 'admin'
    assert settings.db_name == 'custom_db'
    assert 'custom_db' in settings.database_url
