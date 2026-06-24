#!/usr/bin/env python3
"""
SessionEnd Hook: Work Completion Learning.

Reads memory/state/current-work.json and extracts learnings from
significant sessions. Writes to memory/learning/{system|algorithm}/YYYY-MM/.
"""

import json
import os
import signal
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from lib.hook_errors import log_error
from lib.hook_timer import hook_timer


def timeout_handler(signum, frame):
    sys.exit(0)


signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(5)

PAI_DIR = Path(os.environ.get("PAI_DIR") or Path.home() / "helm" / "03-rai")
STATE_DIR = PAI_DIR / "memory" / "state"
LEARNING_DIR = PAI_DIR / "memory" / "learning"
CURRENT_WORK = STATE_DIR / "current-work.json"

ALGORITHM_KEYWORDS = (
    "workflow", "process", "planning", "algorithm", "approach",
    "methodology", "strategy", "pattern", "architecture", "design",
    "refactor", "refactoring", "optimization", "optimize", "migrate",
    "migration", "audit", "review", "consolidate", "consolidation",
    "trim", "simplify", "orchestrate", "pipeline", "lifecycle",
)


def is_significant(work: dict) -> bool:
    if len(work.get("files_changed", [])) >= 3:
        return True
    if len(work.get("tasks_completed", [])) >= 1:
        return True
    if work.get("status") == "completed":
        return True
    return False


def get_learning_category(work: dict) -> str:
    """algorithm = process/workflow work. system = code/tool work."""
    description = (work.get("task_description", "") or "").lower()
    for keyword in ALGORITHM_KEYWORDS:
        if keyword in description:
            return "algorithm"
    return "system"


def write_learning(work: dict, session_id: str):
    category = get_learning_category(work)
    now = datetime.now()
    month_dir = LEARNING_DIR / category / now.strftime("%Y-%m")
    month_dir.mkdir(parents=True, exist_ok=True)

    learning = {
        "timestamp": now.isoformat(),
        "session_id": session_id,
        "type": "work_completion",
        "category": category,
        "task": work.get("task_description", ""),
        "files_changed": work.get("files_changed", []),
        "tasks_completed": work.get("tasks_completed", []),
        "status": work.get("status", "unknown"),
    }

    filename = f"work-{now.strftime('%Y%m%d_%H%M%S')}.json"
    (month_dir / filename).write_text(json.dumps(learning, indent=2))


def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw)
    except Exception as e:
        log_error("work-completion-learning", e, "stdin decode")
        sys.exit(0)

    session_id = data.get("session_id", "unknown")

    if not CURRENT_WORK.exists():
        return

    try:
        work = json.loads(CURRENT_WORK.read_text())
    except Exception as e:
        log_error("work-completion-learning", e, "current-work parse")
        return

    if not is_significant(work):
        return

    try:
        write_learning(work, session_id)
    except Exception as e:
        log_error("work-completion-learning", e, "write learning")
        return

    try:
        CURRENT_WORK.unlink()
    except Exception:
        pass


if __name__ == "__main__":
    with hook_timer("work-completion-learning"):
        main()
