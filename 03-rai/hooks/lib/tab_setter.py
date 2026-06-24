"""Tab state setter for WezTerm terminal."""

import json
import subprocess
import sys
from pathlib import Path

from .paths import get_state_dir
from .tab_constants import PHASE_CONFIG, TAB_STATES

TAB_TITLES_DIR = get_state_dir() / "tab-titles"


def set_tab_title(title: str):
    """Set WezTerm tab title via OSC escape sequence. Wezterm CLI fire-and-forget."""
    try:
        # OSC 1 ; title ST (set tab/icon name) — synchronous, goes over tty
        sys.stderr.write(f"\033]1;{title}\007")
        sys.stderr.flush()
    except Exception:
        pass
    try:
        # Wezterm CLI as a belt-and-suspenders fallback. Fire-and-forget.
        subprocess.Popen(
            ["wezterm", "cli", "set-tab-title", title],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
    except Exception:
        pass


def set_tab_state(state: str, session_id: str = "", detail: str = ""):
    """
    Set tab to a named state.
    States: thinking, working, question, completed, error, idle.
    """
    base = TAB_STATES.get(state, state)
    title = f"{base}: {detail}" if detail else base
    set_tab_title(title)
    _persist_state(session_id, state, title)


def set_phase_tab(phase: str, session_id: str = "", detail: str = ""):
    """Set tab for an Algorithm phase."""
    config = PHASE_CONFIG.get(phase, {})
    label = config.get("label", phase)
    title = f"[{config.get('symbol', '?')}] {label}"
    if detail:
        title += f": {detail}"
    set_tab_title(title)
    _persist_state(session_id, f"phase:{phase}", title)


def read_tab_state(session_id: str) -> dict:
    """Read persisted tab state."""
    path = TAB_TITLES_DIR / f"{session_id}.json"
    if path.exists():
        try:
            return json.loads(path.read_text())
        except Exception:
            pass
    return {}


def _persist_state(session_id: str, state: str, title: str):
    """Persist tab state to disk for cross-hook coordination."""
    if not session_id:
        return
    try:
        TAB_TITLES_DIR.mkdir(parents=True, exist_ok=True)
        path = TAB_TITLES_DIR / f"{session_id}.json"
        data = {}
        if path.exists():
            try:
                data = json.loads(path.read_text())
            except Exception:
                pass
        data["state"] = state
        data["title"] = title
        data["previous_title"] = data.get("title", "")
        path.write_text(json.dumps(data))
    except Exception:
        pass
