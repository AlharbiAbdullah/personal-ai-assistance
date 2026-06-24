"""Algorithm state management for per-session tracking."""

import json
from pathlib import Path
from typing import Any

from .paths import get_state_dir
from .time_utils import get_iso_timestamp

ALGO_DIR = get_state_dir() / "algorithms"

PHASES = [
    "IDLE", "OBSERVE", "THINK", "PLAN",
    "BUILD", "EXECUTE", "VERIFY", "LEARN", "COMPLETE",
]


def _state_path(session_id: str) -> Path:
    return ALGO_DIR / f"{session_id}.json"


def read_state(session_id: str) -> dict:
    """Read algorithm state for session."""
    path = _state_path(session_id)
    if path.exists():
        try:
            return json.loads(path.read_text())
        except Exception:
            pass
    return _default_state(session_id)


def write_state(session_id: str, state: dict):
    """Write algorithm state for session."""
    ALGO_DIR.mkdir(parents=True, exist_ok=True)
    _state_path(session_id).write_text(json.dumps(state, indent=2))


def _default_state(session_id: str) -> dict:
    return {
        "session_id": session_id,
        "phase": "IDLE",
        "phase_history": [],
        "criteria": [],
        "anti_criteria": [],
        "agents_spawned": [],
        "effort_level": "Standard",
        "rework_cycles": 0,
        "created_at": get_iso_timestamp(),
        "updated_at": get_iso_timestamp(),
    }


def phase_transition(session_id: str, new_phase: str) -> dict:
    """Record a phase transition."""
    state = read_state(session_id)
    old_phase = state.get("phase", "IDLE")

    # Detect rework (re-entering OBSERVE after completion)
    if new_phase == "OBSERVE" and old_phase in ("COMPLETE", "LEARN"):
        state["rework_cycles"] = state.get("rework_cycles", 0) + 1

    state["phase"] = new_phase
    state["phase_history"].append({
        "from": old_phase,
        "to": new_phase,
        "timestamp": get_iso_timestamp(),
    })
    state["updated_at"] = get_iso_timestamp()
    write_state(session_id, state)
    return state


def criteria_add(
    session_id: str,
    criterion: str,
    ctype: str = "criterion",
) -> dict:
    """Add a criterion or anti-criterion."""
    state = read_state(session_id)
    entry = {
        "text": criterion,
        "type": ctype,
        "status": "PENDING",
        "created_in_phase": state.get("phase", "UNKNOWN"),
        "created_at": get_iso_timestamp(),
    }
    if ctype == "anti_criterion":
        state["anti_criteria"].append(entry)
    else:
        state["criteria"].append(entry)
    state["updated_at"] = get_iso_timestamp()
    write_state(session_id, state)
    return state


def agent_add(session_id: str, agent_info: dict) -> dict:
    """Record an agent spawn."""
    state = read_state(session_id)
    state["agents_spawned"].append({
        **agent_info,
        "spawned_at": get_iso_timestamp(),
    })
    state["updated_at"] = get_iso_timestamp()
    write_state(session_id, state)
    return state


def algorithm_end(session_id: str) -> dict:
    """Mark algorithm as complete."""
    state = read_state(session_id)
    state["phase"] = "COMPLETE"
    state["completed_at"] = get_iso_timestamp()
    state["updated_at"] = get_iso_timestamp()
    write_state(session_id, state)
    return state
