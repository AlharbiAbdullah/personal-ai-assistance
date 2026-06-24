#!/usr/bin/env python3
"""
SessionEnd Hook: Algorithm Scan.

Replaces per-PostToolUse algorithm-tracker.py. Parses the transcript once
at session end, extracts TaskCreate criteria + Task agent spawns + final
phase hints, writes one state/algorithms/{session_id}.json.
"""

import json
import re
import signal
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from lib.algorithm_state import (
    read_state, write_state, phase_transition,
    criteria_add, agent_add, algorithm_end,
)
from lib.hook_errors import log_error
from lib.hook_timer import hook_timer
from lib.transcript_parse import (
    iter_assistant_tool_uses, iter_transcript,
)


def timeout_handler(signum, frame):
    sys.exit(0)


signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(10)

PHASE_PATTERNS = {
    "OBSERVE": re.compile(r"\bobserv(e|ing)\b", re.I),
    "THINK": re.compile(r"\bthink(ing)?\b|\banalysis\b", re.I),
    "PLAN": re.compile(r"\bplan(ning)?\b", re.I),
    "BUILD": re.compile(r"\bbuild(ing)?\b|\bimplement", re.I),
    "EXECUTE": re.compile(r"\bexecut(e|ing)\b|\brunning\b", re.I),
    "VERIFY": re.compile(r"\bverif(y|ying|ication)\b", re.I),
    "LEARN": re.compile(r"\blearn(ing)?\b|\breflect", re.I),
}

ISC_PATTERN = re.compile(r"ISC-[CA]\d+", re.I)


def _detect_phase(text: str) -> str | None:
    for phase, pattern in PHASE_PATTERNS.items():
        if pattern.search(text):
            return phase
    return None


def _extract_criteria(text: str) -> list[dict]:
    out = []
    seen = set()
    for match in ISC_PATTERN.findall(text):
        if match in seen:
            continue
        seen.add(match)
        ctype = "anti_criterion" if "-A" in match.upper() else "criterion"
        out.append({"id": match, "type": ctype})
    return out


def _scan_assistant_text(transcript_path: str) -> str | None:
    """Return the last phase hint found in assistant text blocks."""
    last_phase = None
    for entry in iter_transcript(transcript_path):
        if entry.get("type") != "assistant":
            continue
        content = entry.get("message", {}).get("content", [])
        if not isinstance(content, list):
            continue
        for item in content:
            if not isinstance(item, dict):
                continue
            if item.get("type") != "text":
                continue
            phase = _detect_phase(item.get("text", "")[:1000])
            if phase:
                last_phase = phase
    return last_phase


def scan(session_id: str, transcript_path: str) -> None:
    """Walk transcript once, apply all algorithm-state updates."""
    for tool_use in iter_assistant_tool_uses(transcript_path):
        name = tool_use.get("name", "")
        tin = tool_use.get("input", {}) or {}

        if name == "TaskCreate":
            subject = tin.get("subject", "")
            desc = tin.get("description", "")
            combined = f"{subject} {desc}"
            for c in _extract_criteria(combined):
                criteria_add(session_id, combined, c["type"])
            phase = _detect_phase(combined)
            if phase:
                phase_transition(session_id, phase)

        elif name == "Task":
            agent_add(session_id, {
                "type": tin.get("subagent_type", ""),
                "description": tin.get("description", ""),
            })

    final_phase = _scan_assistant_text(transcript_path)
    if final_phase:
        state = read_state(session_id)
        if state.get("phase") != final_phase:
            phase_transition(session_id, final_phase)

    algorithm_end(session_id)


def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw)
    except Exception as e:
        log_error("algorithm-scan", e, "stdin decode")
        sys.exit(0)

    session_id = data.get("session_id", "unknown")
    transcript_path = data.get("transcript_path", "")

    if not transcript_path:
        return

    try:
        scan(session_id, transcript_path)
    except Exception as e:
        log_error("algorithm-scan", e, f"session={session_id}")


if __name__ == "__main__":
    with hook_timer("algorithm-scan"):
        main()
