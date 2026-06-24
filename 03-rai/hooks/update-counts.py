#!/usr/bin/env python3
"""
SessionEnd Hook: Update Counts.

Refreshes settings.json "counts" block with skills/hooks/ratings/work/learnings
totals. Also appends a time-series entry to memory/learning/system/counts-history.jsonl
for trend analysis.
"""

import json
import os
import signal
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from lib.hook_errors import log_error
from lib.hook_timer import hook_timer
from lib.paths import (
    get_hooks_dir, get_learning_dir, get_memory_dir, get_settings_path,
    get_skills_dir, get_work_dir,
)
from lib.time_utils import get_iso_timestamp


def timeout_handler(signum, frame):
    sys.exit(0)


signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(5)

HISTORY_LOG = get_learning_dir() / "system" / "counts-history.jsonl"


def count_skills() -> int:
    skills_dir = get_skills_dir()
    if not skills_dir.exists():
        return 0
    return sum(
        1 for d in skills_dir.iterdir()
        if d.is_dir() and (d / "SKILL.md").exists()
    )


def count_hooks() -> int:
    hooks_dir = get_hooks_dir()
    if not hooks_dir.exists():
        return 0
    return len(list(hooks_dir.glob("*.py")))


def count_ratings() -> int:
    ratings = get_memory_dir() / "learning" / "signals" / "ratings.jsonl"
    if not ratings.exists():
        return 0
    try:
        with ratings.open() as f:
            return sum(1 for _ in f)
    except Exception:
        return 0


def count_work_dirs() -> int:
    work = get_work_dir()
    if not work.exists():
        return 0
    return sum(1 for d in work.iterdir() if d.is_dir())


def count_learning_files() -> int:
    learning = get_memory_dir() / "learning"
    if not learning.exists():
        return 0
    count = 0
    for _, _, files in os.walk(learning):
        count += sum(1 for f in files if f.endswith(".json"))
    return count


def get_counts() -> dict:
    return {
        "skills": count_skills(),
        "hooks": count_hooks(),
        "ratings": count_ratings(),
        "work": count_work_dirs(),
        "learnings": count_learning_files(),
        "updatedAt": get_iso_timestamp(),
    }


def update_settings(counts: dict):
    path = get_settings_path()
    if not path.exists():
        return
    try:
        settings = json.loads(path.read_text())
        settings["counts"] = counts
        path.write_text(json.dumps(settings, indent=2) + "\n")
    except Exception as e:
        log_error("update-counts", e, "settings write")


def append_history(counts: dict):
    try:
        HISTORY_LOG.parent.mkdir(parents=True, exist_ok=True)
        with HISTORY_LOG.open("a") as f:
            f.write(json.dumps(counts) + "\n")
    except Exception as e:
        log_error("update-counts", e, "history append")


def main():
    try:
        sys.stdin.read()
    except Exception:
        pass

    try:
        counts = get_counts()
        update_settings(counts)
        append_history(counts)
    except Exception as e:
        log_error("update-counts", e, "main")


if __name__ == "__main__":
    with hook_timer("update-counts"):
        main()
