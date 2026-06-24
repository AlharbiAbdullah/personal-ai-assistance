"""Central identity loader for DA and Principal."""

import json
from pathlib import Path

from .paths import get_settings_path

_cache: dict | None = None


def _load_settings() -> dict:
    global _cache
    if _cache is not None:
        return _cache
    try:
        _cache = json.loads(get_settings_path().read_text())
    except Exception:
        _cache = {}
    return _cache


def clear_cache():
    global _cache
    _cache = None


def get_settings() -> dict:
    return _load_settings()


def get_da_name() -> str:
    s = _load_settings()
    return s.get("daidentity", {}).get("name", "Claude")


def get_principal_name() -> str:
    s = _load_settings()
    return s.get("principal", {}).get("name", "User")


def get_principal_timezone() -> str:
    s = _load_settings()
    return s.get("principal", {}).get("timezone", "UTC")


def get_notification_config() -> dict:
    s = _load_settings()
    return s.get("notifications", {})
