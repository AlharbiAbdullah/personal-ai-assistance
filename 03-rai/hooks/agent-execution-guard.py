#!/usr/bin/env python3
"""
PreToolUse Hook: Agent Execution Guard.

Warns when Task tool is called without run_in_background: true
in non-fast contexts. Injects system-reminder suggestion.
"""

import json
import signal
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from lib.hook_errors import log_error
from lib.hook_timer import hook_timer


def timeout_handler(signum, frame):
    sys.exit(0)


signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(5)


def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw)
    except Exception as e:
        log_error("agent-execution-guard", e, "stdin decode")
        sys.exit(0)

    tool_name = data.get("tool_name", "")
    tool_input = data.get("tool_input", {})

    if tool_name != "Task":
        sys.exit(0)

    # PASS: already running in background
    if tool_input.get("run_in_background"):
        sys.exit(0)

    # PASS: haiku model (fast tier)
    model = tool_input.get("model", "")
    if model == "haiku":
        sys.exit(0)

    # PASS: Explore agent (quick lookups)
    agent_type = tool_input.get("subagent_type", "")
    if agent_type == "Explore":
        sys.exit(0)

    # PASS: prompt indicates fast scope
    prompt = tool_input.get("prompt", "")
    if "Timing: FAST" in prompt:
        sys.exit(0)

    # WARN: suggest background execution
    print(json.dumps({
        "decision": "allow",
        "message": (
            "Consider adding run_in_background: true to this Task call "
            "for better parallelism. Use TaskOutput to poll results."
        ),
    }))


if __name__ == "__main__":
    with hook_timer("agent-execution-guard"):
        main()
