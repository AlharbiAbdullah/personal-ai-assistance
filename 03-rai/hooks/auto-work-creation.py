#!/usr/bin/env python3
"""
UserPromptSubmit Hook: Auto Work Creation.

Creates session/task hierarchy in memory/work/.
Structure: WORK/{timestamp}_{slug}/tasks/{001_slug}/
Each task gets ISC.json, THREAD.md, PRD.md.
Manages current-work.json state file.
"""

import json
import signal
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from lib.hook_errors import log_error
from lib.hook_timer import hook_timer
from lib.name_extraction import short_name, work_slug
from lib.paths import get_state_dir, get_work_dir
from lib.prd_template import generate_prd_template
from lib.time_utils import get_filename_timestamp, get_iso_timestamp


def timeout_handler(signum, frame):
    sys.exit(0)


signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(5)


def read_current_work(session_id: str) -> dict | None:
    scoped = get_state_dir() / f"current-work-{session_id}.json"
    legacy = get_state_dir() / "current-work.json"
    for path in (scoped, legacy):
        if path.exists():
            try:
                return json.loads(path.read_text())
            except Exception:
                pass
    return None


def write_current_work(state: dict):
    session_id = state.get("session_id", "")
    get_state_dir().mkdir(parents=True, exist_ok=True)
    path = get_state_dir() / f"current-work-{session_id}.json"
    path.write_text(json.dumps(state, indent=2))
    legacy = get_state_dir() / "current-work.json"
    legacy.write_text(json.dumps(state, indent=2))


def classify_prompt(prompt: str, has_session: bool) -> str:
    """Heuristic classifier: conversational | work | continuation."""
    stripped = prompt.strip()
    if len(stripped) < 20 and stripped.lower() in (
        "yes", "no", "ok", "sure", "continue", "go ahead",
        "do it", "proceed", "next", "done", "thanks",
    ):
        return "conversational"
    if not has_session:
        return "work"
    return "continuation"


def create_session_dir(title: str, slug: str, session_id: str) -> Path:
    ts = get_filename_timestamp()
    dirname = f"{ts}_{slug}" if slug else ts
    session_dir = get_work_dir() / dirname
    session_dir.mkdir(parents=True, exist_ok=True)
    (session_dir / "tasks").mkdir(exist_ok=True)
    (session_dir / "scratch").mkdir(exist_ok=True)

    meta = {
        "id": dirname,
        "title": title,
        "session_id": session_id,
        "created_at": get_iso_timestamp(),
        "status": "ACTIVE",
        "completed_at": None,
    }
    (session_dir / "META.yaml").write_text(
        "\n".join(f"{k}: {v}" for k, v in meta.items())
    )
    return session_dir


def create_task_dir(
    session_dir: Path, task_num: int, title: str,
) -> Path:
    slug = work_slug(title, 30)
    dirname = f"{task_num:03d}_{slug}" if slug else f"{task_num:03d}"
    task_dir = session_dir / "tasks" / dirname
    task_dir.mkdir(parents=True, exist_ok=True)

    isc = {
        "criteria": [],
        "antiCriteria": [],
        "satisfaction": {
            "satisfied": 0, "partial": 0, "failed": 0, "total": 0,
        },
    }
    (task_dir / "ISC.json").write_text(json.dumps(isc, indent=2))
    (task_dir / "THREAD.md").write_text(
        f"# {title}\n\nCreated: {get_iso_timestamp()}\n"
    )
    (task_dir / "PRD.md").write_text(generate_prd_template(title))

    current = session_dir / "tasks" / "current"
    if current.is_symlink():
        current.unlink()
    try:
        current.symlink_to(task_dir.name)
    except Exception:
        pass

    return task_dir


def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw)
    except Exception as e:
        log_error("auto-work-creation", e, "stdin decode")
        sys.exit(0)

    prompt = data.get("prompt", "")
    session_id = data.get("session_id", "unknown")

    if not prompt:
        sys.exit(0)

    try:
        existing = read_current_work(session_id)
        classification = classify_prompt(prompt, existing is not None)

        if classification == "conversational":
            return
        if classification != "work" or existing is not None:
            return

        title = short_name(prompt)
        slug = work_slug(prompt, 40)
        session_dir = create_session_dir(title, slug, session_id)
        create_task_dir(session_dir, 1, title)

        state = {
            "session_id": session_id,
            "started_at": get_iso_timestamp(),
            "work_dir": str(session_dir),
            "task_description": title,
            "files_changed": [],
            "tasks_completed": [],
            "status": "active",
        }
        write_current_work(state)
    except Exception as e:
        log_error("auto-work-creation", e, f"session={session_id}")


if __name__ == "__main__":
    with hook_timer("auto-work-creation"):
        main()
