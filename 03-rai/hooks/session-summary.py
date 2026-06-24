#!/usr/bin/env python3
"""
SessionEnd Hook: Session Summary.

Marks work directory as COMPLETED, clears session state.
Runs alongside save-memory.py and work-completion-learning.py.
"""

import json
import os
import re
import signal
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from lib.hook_errors import log_error
from lib.hook_timer import hook_timer
from lib.paths import get_state_dir, get_work_dir
from lib.time_utils import get_iso_timestamp


def timeout_handler(signum, frame):
    sys.exit(0)


signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(5)


def find_state_file(session_id: str) -> Path | None:
    """Look up session-scoped or legacy state file."""
    scoped = get_state_dir() / f"current-work-{session_id}.json"
    legacy = get_state_dir() / "current-work.json"
    if scoped.exists():
        return scoped
    if legacy.exists():
        return legacy
    return None


def _mark_prd_files_completed(work_path: Path, ts: str) -> int:
    """Update v3.7.0 PRD.md frontmatter under tasks/*/PRD.md. Return count updated."""
    updated = 0
    for prd in work_path.glob("tasks/*/PRD.md"):
        try:
            text = prd.read_text()
            new = re.sub(
                r'^status:\s*"?(ACTIVE|DRAFT)"?$',
                "status: COMPLETED",
                text,
                flags=re.MULTILINE,
            )
            new = re.sub(
                r"^completed_at:\s*(null|None|)$",
                f'completed_at: "{ts}"',
                new,
                flags=re.MULTILINE,
            )
            if new != text:
                prd.write_text(new)
                updated += 1
        except Exception:
            pass
    return updated


def _clean_session_names(session_id: str) -> None:
    """Remove this session's entry from session-names.json (prevents IDLE ghosts)."""
    sn_path = get_state_dir() / "session-names.json"
    if not sn_path.exists():
        return
    try:
        names = json.loads(sn_path.read_text())
        if session_id in names:
            del names[session_id]
            sn_path.write_text(json.dumps(names, indent=2))
    except Exception:
        pass


def clear_session_work(session_id: str):
    """Mark work as completed (META.yaml + PRD.md) and clean up state."""
    state_file = find_state_file(session_id)
    if not state_file:
        return

    try:
        state = json.loads(state_file.read_text())
    except Exception:
        return

    ts = get_iso_timestamp()
    work_dir = state.get("work_dir", "")
    if work_dir:
        work_path = Path(work_dir)
        # Legacy: META.yaml at session root
        meta_path = work_path / "META.yaml"
        if meta_path.exists():
            try:
                content = meta_path.read_text()
                content = re.sub(r"status: ACTIVE", "status: COMPLETED", content)
                content = re.sub(
                    r"completed_at: None",
                    f"completed_at: {ts}",
                    content,
                )
                meta_path.write_text(content)
            except Exception:
                pass
        # v3.7.0: PRD.md frontmatter under tasks/*/PRD.md
        if work_path.exists():
            _mark_prd_files_completed(work_path, ts)

    # Delete state file
    try:
        state_file.unlink()
    except Exception:
        pass

    # Clean up legacy if scoped was used
    legacy = get_state_dir() / "current-work.json"
    if legacy.exists():
        try:
            legacy.unlink()
        except Exception:
            pass

    # Clean session-names.json entry to prevent ghost IDLE entries
    _clean_session_names(session_id)

    # Session is terminating. Delete the persisted tab state without touching the
    # terminal first: no reader exists after session end, and skipping the OSC write
    # + wezterm subprocess saves ~200-600ms.
    for sub in ("tab-titles", "algorithms"):
        p = get_state_dir() / sub / f"{session_id}.json"
        try:
            p.unlink()
        except OSError:
            pass


def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw)
    except Exception as e:
        log_error("session-summary", e, "stdin decode")
        sys.exit(0)

    session_id = data.get("session_id", "unknown")
    try:
        clear_session_work(session_id)
    except Exception as e:
        log_error("session-summary", e, f"session={session_id}")


if __name__ == "__main__":
    with hook_timer("session-summary"):
        main()
