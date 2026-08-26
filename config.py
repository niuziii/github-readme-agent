"""应用配置：读取并保存本机 .env 文件。"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

from dotenv import load_dotenv


DEFAULT_CONFIG = {
    "LLM_BASE_URL": "https://api.deepseek.com/v1",
    "LLM_API_KEY": "",
    "LLM_MODEL": "deepseek-chat",
    "LLM_TEMPERATURE": "0.3",
    "GITHUB_TOKEN": "",
    "MAX_README_CHARS": "24000",
}

ALIASES = {
    "base_url": "LLM_BASE_URL",
    "api_key": "LLM_API_KEY",
    "model": "LLM_MODEL",
    "temperature": "LLM_TEMPERATURE",
    "github_token": "GITHUB_TOKEN",
    "max_readme_chars": "MAX_README_CHARS",
}


def app_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


class AppConfig:
    def __init__(self) -> None:
        self.path = app_dir() / ".env"
        if self.path.exists():
            load_dotenv(self.path)
        self.values: dict[str, str] = {
            key: os.getenv(key, default) for key, default in DEFAULT_CONFIG.items()
        }

    @property
    def base_url(self) -> str:
        return self.values["LLM_BASE_URL"].strip().rstrip("/")

    @property
    def api_key(self) -> str:
        return self.values["LLM_API_KEY"].strip()

    @property
    def model(self) -> str:
        return self.values["LLM_MODEL"].strip()

    @property
    def temperature(self) -> float:
        try:
            return float(self.values.get("LLM_TEMPERATURE", "0.3"))
        except ValueError:
            return 0.3

    @property
    def github_token(self) -> str:
        return self.values["GITHUB_TOKEN"].strip()

    @property
    def max_readme_chars(self) -> int:
        try:
            return max(4000, int(self.values.get("MAX_README_CHARS", "24000")))
        except ValueError:
            return 24000

    def save(self, **overrides: Any) -> None:
        merged = dict(self.values)
        for key, value in overrides.items():
            if value is not None:
                env_key = ALIASES.get(key, key.upper())
                merged[env_key] = str(value)

        lines = [f"{key}={merged[key]}" for key in DEFAULT_CONFIG]
        self.path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        self.values = {key: str(merged[key]) for key in DEFAULT_CONFIG}
        os.environ.update(self.values)
