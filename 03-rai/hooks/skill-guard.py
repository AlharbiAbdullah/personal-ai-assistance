#!/usr/bin/env python3
"""
PreToolUse Hook: Skill Guard.

Blocks false-positive skill invocations caused by position bias.
Currently blocks: keybindings-help (first in skills list,
triggers on aggressive BLOCKING REQUIREMENT language).
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

BLOCKED_SKILLS = {"keybindings-help"}


def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw)
    except Exception as e:
        log_error("skill-guard", e, "stdin decode")
        sys.exit(0)

    tool_name = data.get("tool_name", "")
    tool_input = data.get("tool_input", {})

    if tool_name != "Skill":
        sys.exit(0)

    skill_name = tool_input.get("skill", "")

    if skill_name in BLOCKED_SKILLS:
        print(json.dumps({
            "decision": "block",
            "reason": (
                f"Skill '{skill_name}' blocked by SkillGuard. "
                "This is likely a false-positive invocation."
            ),
        }))
        sys.exit(2)


if __name__ == "__main__":
    with hook_timer("skill-guard"):
        main()
