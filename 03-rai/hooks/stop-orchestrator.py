#!/usr/bin/env python3
"""
Stop Hook: Orchestrator.

Single entry point for Stop event. Parses transcript once,
distributes to isolated handlers. Handlers run independently
and failures are isolated.
"""

import json
import os
import signal
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from lib.algorithm_state import read_state, algorithm_end
from lib.hook_errors import log_error
from lib.hook_timer import hook_timer
from lib.notifications import notify
from lib.tab_setter import set_tab_state


def timeout_handler(signum, frame):
    sys.exit(0)


signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(10)  # Longer timeout for orchestrator


def extract_last_response(data: dict) -> str:
    """Extract last assistant response from stop data."""
    transcript = data.get("transcript_path", "")
    if not transcript or not Path(transcript).exists():
        return data.get("response", "")

    last_response = ""
    try:
        with open(transcript) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    if entry.get("type") == "assistant":
                        msg = entry.get("message", {})
                        content = msg.get("content", [])
                        if isinstance(content, list):
                            for item in content:
                                if isinstance(item, dict):
                                    if item.get("type") == "text":
                                        last_response = item.get(
                                            "text", ""
                                        )
                        elif isinstance(content, str):
                            last_response = content
                except json.JSONDecodeError:
                    continue
    except Exception:
        pass
    return last_response


def handle_tab_reset(session_id: str, response: str):
    """Reset tab to completed state."""
    try:
        summary = response[:50].strip() if response else "Done"
        set_tab_state("completed", session_id, summary)
    except Exception:
        pass


def handle_algorithm_enrichment(session_id: str, response: str):
    """Enrich algorithm state with response data."""
    try:
        state = read_state(session_id)
        if state.get("phase") not in ("IDLE", "COMPLETE"):
            algorithm_end(session_id)
    except Exception:
        pass


def handle_notification(session_id: str, response: str):
    """Send completion notification if significant work."""
    try:
        state_file = (
            Path(os.environ.get("PAI_DIR") or Path.home() / "helm" / "03-rai")
            / "memory" / "state"
            / f"current-work-{session_id}.json"
        )
        if state_file.exists():
            work = json.loads(state_file.read_text())
            files = work.get("files_changed", [])
            if len(files) >= 3:
                notify(
                    "task_complete",
                    "Session Complete",
                    f"Modified {len(files)} files.",
                )
    except Exception:
        pass


def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw)
    except Exception as e:
        log_error("stop-orchestrator", e, "stdin decode")
        sys.exit(0)

    session_id = data.get("session_id", "unknown")
    response = extract_last_response(data)

    for handler in [
        handle_tab_reset,
        handle_algorithm_enrichment,
        handle_notification,
    ]:
        try:
            handler(session_id, response)
        except Exception as e:
            log_error("stop-orchestrator", e, f"handler={handler.__name__}")


if __name__ == "__main__":
    with hook_timer("stop-orchestrator"):
        main()
