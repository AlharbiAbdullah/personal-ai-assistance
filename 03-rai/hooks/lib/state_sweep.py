"""Sweep orphan per-session state files left by crashed sessions."""

import json
from datetime import datetime, timedelta
from pathlib import Path

STALE_HOURS = 6


def _active_uuids(state_dir: Path, cutoff_ts: float) -> set[str]:
    """Collect UUIDs with any state file touched inside the cutoff window."""
    active: set[str] = set()
    for p in state_dir.glob("current-work-*.json"):
        try:
            if p.stat().st_mtime >= cutoff_ts:
                active.add(p.stem.removeprefix("current-work-"))
        except OSError:
            pass
    for sub in ("tab-titles", "algorithms"):
        d = state_dir / sub
        if not d.exists():
            continue
        for p in d.glob("*.json"):
            try:
                if p.stat().st_mtime >= cutoff_ts:
                    active.add(p.stem)
            except OSError:
                pass
    return active


def _safe_unlink(path: Path) -> bool:
    try:
        path.unlink()
        return True
    except OSError:
        return False


def sweep_orphans(
    current_session_id: str,
    state_dir: Path,
    stale_hours: int = STALE_HOURS,
) -> dict:
    """Delete per-session files whose session has no recent activity.

    Returns counts keyed by kind: current_work, tab_titles, algorithms, session_names.
    """
    cutoff_ts = (datetime.now() - timedelta(hours=stale_hours)).timestamp()
    active = _active_uuids(state_dir, cutoff_ts)
    if current_session_id:
        active.add(current_session_id)

    counts = {"current_work": 0, "tab_titles": 0, "algorithms": 0, "session_names": 0}

    for p in state_dir.glob("current-work-*.json"):
        if p.stem.removeprefix("current-work-") not in active and _safe_unlink(p):
            counts["current_work"] += 1

    for sub, key in (("tab-titles", "tab_titles"), ("algorithms", "algorithms")):
        d = state_dir / sub
        if not d.exists():
            continue
        for p in d.glob("*.json"):
            if p.stem not in active and _safe_unlink(p):
                counts[key] += 1

    sn_path = state_dir / "session-names.json"
    if sn_path.exists():
        try:
            names = json.loads(sn_path.read_text())
            removed = [u for u in names if u not in active]
            for u in removed:
                del names[u]
            if removed:
                sn_path.write_text(json.dumps(names, indent=2))
            counts["session_names"] = len(removed)
        except (OSError, json.JSONDecodeError):
            pass

    return counts
