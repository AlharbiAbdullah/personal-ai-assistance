"""Shared time utilities for Rai hooks."""

import json
from datetime import datetime, timezone
from pathlib import Path

from .paths import get_settings_path


def _get_timezone() -> str:
    """Read timezone from settings.json principal config."""
    try:
        settings = json.loads(get_settings_path().read_text())
        return settings.get("principal", {}).get("timezone", "UTC")
    except Exception:
        return "UTC"


def get_iso_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_local_timestamp() -> str:
    return datetime.now().isoformat()


def get_year_month() -> str:
    return datetime.now().strftime("%Y-%m")


def get_date() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def get_filename_timestamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")
