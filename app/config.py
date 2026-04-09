from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


class ConfigError(Exception):
    """Raised when required configuration is missing or invalid."""


@dataclass(slots=True)
class AppConfig:
    openai_api_key: str
    openai_model: str = "gpt-4o-mini"
    app_name: str = "historical-figure-chatbot"
    debug: bool = False
    personas_dir: str = "app/personas"
    custom_personas_dir: str = "app/data/custom_personas"


def load_config() -> AppConfig:
    """
    Load runtime config from environment variables.

    Required:
    - OPENAI_API_KEY

    Optional:
    - OPENAI_MODEL
    - APP_DEBUG
    """
    load_dotenv()

    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise ConfigError(
            "OPENAI_API_KEY is not set. Please export it before running the app."
        )

    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip() or "gpt-4o-mini"
    debug_raw = os.getenv("APP_DEBUG", "false").strip().lower()
    debug = debug_raw in {"1", "true", "yes", "on"}

    return AppConfig(
        openai_api_key=api_key,
        openai_model=model,
        debug=debug,
    )
