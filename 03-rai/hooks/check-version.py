#!/usr/bin/env python3
"""
SessionStart Hook: Check Claude Code version.

Compares installed version against latest npm version.
Prints update notification to stderr if outdated.
Skipped for subagents. Non-blocking.
"""

import json
import re
import signal
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from lib.hook_errors import log_error
from lib.hook_timer import hook_timer


def timeout_handler(signum, frame):
    sys.exit(0)


signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(5)


def get_current_version() -> str | None:
    try:
        result = subprocess.run(
            ["claude", "--version"],
            capture_output=True, text=True, timeout=3,
        )
        match = re.search(r"(\d+\.\d+\.\d+)", result.stdout)
        return match.group(1) if match else None
    except Exception:
        return None


def get_latest_version() -> str | None:
    try:
        result = subprocess.run(
            ["npm", "view", "@anthropic-ai/claude-code", "version"],
            capture_output=True, text=True, timeout=5,
        )
        match = re.search(r"(\d+\.\d+\.\d+)", result.stdout)
        return match.group(1) if match else None
    except Exception:
        return None


def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw)
    except Exception as e:
        log_error("check-version", e, "stdin decode")
        sys.exit(0)

    if data.get("is_subagent"):
        sys.exit(0)

    try:
        current = get_current_version()
        latest = get_latest_version()
        if current and latest and current != latest:
            print(
                f"Claude Code update available: {current} -> {latest}. "
                f"Run: npm install -g @anthropic-ai/claude-code",
                file=sys.stderr,
            )
    except Exception as e:
        log_error("check-version", e, "version check")


if __name__ == "__main__":
    with hook_timer("check-version"):
        main()
