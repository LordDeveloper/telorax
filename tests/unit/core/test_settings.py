from __future__ import annotations

from unittest.mock import patch

from telorax.core.config.settings import Settings


def test_load_uses_environment_when_env_file_is_unreadable(tmp_path, monkeypatch) -> None:
    env_file = tmp_path / '.env'
    env_file.write_text('APP_PORT=9000\n', encoding='utf-8')
    monkeypatch.setenv('ENV_FILE', str(env_file))
    monkeypatch.setenv('APP_PORT', '2082')

    with patch('telorax.core.config.settings.os.access', return_value=False):
        settings = Settings.load(env_file)

    assert settings.app_port == 2082
