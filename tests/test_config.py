import pytest

from app.config import ConfigError, load_config


def test_load_config_requires_api_key(monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "")
    monkeypatch.delenv("OPENAI_MODEL", raising=False)
    monkeypatch.delenv("APP_DEBUG", raising=False)

    with pytest.raises(ConfigError):
        load_config()


def test_load_config_parses_model_and_debug(monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("OPENAI_MODEL", "gpt-4o-mini")
    monkeypatch.setenv("APP_DEBUG", "true")

    config = load_config()

    assert config.openai_api_key == "test-key"
    assert config.openai_model == "gpt-4o-mini"
    assert config.debug is True
