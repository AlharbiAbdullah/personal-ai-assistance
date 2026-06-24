"""Centralized path resolution for Rai hooks."""

import os
from pathlib import Path


def get_pai_dir() -> Path:
    """Get Rai directory from env or default."""
    pai = os.environ.get("PAI_DIR", "")
    if pai:
        return Path(pai).expanduser().resolve()
    return Path.home() / "helm" / "03-rai"


def get_memory_dir() -> Path:
    return get_pai_dir() / "memory"


def get_hooks_dir() -> Path:
    return get_pai_dir() / "hooks"


def get_skills_dir() -> Path:
    return get_pai_dir() / "skills"


def get_settings_path() -> Path:
    return get_pai_dir() / "config" / "settings.json"


def get_state_dir() -> Path:
    return get_memory_dir() / "state"


def get_work_dir() -> Path:
    return get_memory_dir() / "work"


def get_learning_dir() -> Path:
    return get_memory_dir() / "learning"
