"""Credential storage and lookup for ChinglishConverter.

Credential resolution order (first hit wins), matching the Anthropic SDK's own
convention as closely as we can:

1. ``ANTHROPIC_API_KEY`` in the environment.
2. A key saved by ``chinglish login`` in the config file
   (``$XDG_CONFIG_HOME/chinglishconverter/config.json`` or the OS equivalent).
3. Whatever the ``anthropic.Anthropic()`` client resolves on its own
   (``ANTHROPIC_AUTH_TOKEN``, an ``ant auth login`` profile, etc.).

We never transmit the key anywhere except to the Anthropic API via the SDK.
"""

from __future__ import annotations

import json
import os
import stat
from pathlib import Path
from typing import Optional

APP_NAME = "chinglishconverter"


def config_dir() -> Path:
    """Return the per-user config directory, honouring XDG / OS conventions."""
    if os.name == "nt":  # Windows
        base = os.environ.get("APPDATA") or str(Path.home() / "AppData" / "Roaming")
        return Path(base) / APP_NAME
    xdg = os.environ.get("XDG_CONFIG_HOME")
    base = Path(xdg) if xdg else Path.home() / ".config"
    return base / APP_NAME


def config_path() -> Path:
    return config_dir() / "config.json"


def _read_config() -> dict:
    path = config_path()
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def _write_config(data: dict) -> None:
    directory = config_dir()
    directory.mkdir(parents=True, exist_ok=True)
    path = config_path()
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    # Best-effort tighten permissions on POSIX (owner read/write only).
    try:
        os.chmod(path, stat.S_IRUSR | stat.S_IWUSR)
    except OSError:
        pass


def save_api_key(api_key: str) -> Path:
    """Persist an API key to the config file and return its path."""
    data = _read_config()
    data["api_key"] = api_key.strip()
    _write_config(data)
    return config_path()


def clear_api_key() -> bool:
    """Remove any stored API key. Returns True if one was present."""
    data = _read_config()
    had = data.pop("api_key", None) is not None
    if had:
        _write_config(data)
    return had


def stored_api_key() -> Optional[str]:
    """Return the API key saved by ``chinglish login``, if any."""
    key = _read_config().get("api_key")
    return key or None


def resolve_api_key() -> Optional[str]:
    """Resolve an API key from the environment or the saved config.

    Returns ``None`` when neither is set; the caller may still succeed if the
    Anthropic SDK finds credentials on its own (e.g. an ``ant auth login``
    profile), so ``None`` is not necessarily fatal.
    """
    env = os.environ.get("ANTHROPIC_API_KEY")
    if env:
        return env
    return stored_api_key()


def default_preferences() -> dict:
    """Return stored default preferences merged over built-in defaults."""
    data = _read_config()
    prefs = {
        "intensity": "medium",
        "model": "claude-opus-4-8",
    }
    prefs.update({k: v for k, v in data.items() if k in prefs})
    return prefs


def save_preference(key: str, value: str) -> None:
    data = _read_config()
    data[key] = value
    _write_config(data)
