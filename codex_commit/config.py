"""Configuration loading for codex-commit."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

try:
    import tomllib
except ImportError:
    import tomli as tomllib  # Python < 3.11

DEFAULT_MODEL = "gpt-4o"
DEFAULT_LANG = "en"
DEFAULT_STYLE = "conventional"
DEFAULT_TEMPERATURE = 0.3
DEFAULT_MAX_LENGTH = 72

CONFIG_FILES = [
    "pyproject.toml",
    ".codex-commit.toml",
    "codex-commit.toml",
]


class Config:
    """Typed configuration for codex-commit."""

    def __init__(self) -> None:
        self.model: str = DEFAULT_MODEL
        self.base_url: str | None = None
        self.api_key: str | None = None
        self.lang: str = DEFAULT_LANG
        self.style: str = DEFAULT_STYLE
        self.temperature: float = DEFAULT_TEMPERATURE
        self.max_length: int = DEFAULT_MAX_LENGTH
        self.scope_detection: bool = True
        self.dry_run: bool = False
        self.debug: bool = False
        self.template_path: str | None = None

    @classmethod
    def load(cls) -> Config:
        """Load config from file + env + defaults, in order of precedence."""
        cfg = cls()

        # 1. From config file (lowest precedence)
        cfg._load_from_file()

        # 2. From environment variables (medium precedence)
        cfg._load_from_env()

        # 3. API key from env (required)
        cfg.api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("CODEX_COMMIT_API_KEY")

        if not cfg.api_key:
            print(
                "❌ OPENAI_API_KEY not set.\n"
                "   export OPENAI_API_KEY='sk-...'\n"
                "   or set CODEX_COMMIT_API_KEY."
            )
            raise SystemExit(1)

        return cfg

    def _load_from_file(self) -> None:
        """Load settings from project config file."""
        for filename in CONFIG_FILES:
            path = Path.cwd() / filename
            if path.exists():
                raw = tomllib.loads(path.read_text())
                section = raw.get("tool", {}).get("codex-commit", {})
                self._apply_dict(section)
                return

    def _load_from_env(self) -> None:
        """Load settings from environment variables."""
        mapping = {
            "CODEX_COMMIT_MODEL": "model",
            "CODEX_COMMIT_BASE_URL": "base_url",
            "CODEX_COMMIT_LANG": "lang",
            "CODEX_COMMIT_STYLE": "style",
            "CODEX_COMMIT_TEMPERATURE": "temperature",
            "CODEX_COMMIT_MAX_LENGTH": "max_length",
            "CODEX_COMMIT_SCOPE_DETECTION": "scope_detection",
            "CODEX_COMMIT_TEMPLATE": "template_path",
        }
        for env_key, attr in mapping.items():
            val = os.environ.get(env_key)
            if val is not None:
                setattr(self, attr, self._cast(attr, val))

    def _apply_dict(self, d: dict[str, Any]) -> None:
        for key, val in d.items():
            if hasattr(self, key):
                setattr(self, key, val)

    @staticmethod
    def _cast(attr: str, val: str) -> Any:
        type_hints = {
            "temperature": float,
            "max_length": int,
            "scope_detection": bool,
        }
        if attr in type_hints:
            return type_hints[attr](val)
        return val
