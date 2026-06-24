#!/usr/bin/env python3
"""
Project-Level SessionStart Hook - Load accumulated project knowledge.

Loads accumulated_knowledge.json + recent session summaries and prints to stdout.
Claude receives this as context at session start.

This script is copied into each project's .claude/hooks/ by /project_init.
It detects the project root by walking up from CWD looking for project_memory/.
"""

import json
import signal
import sys
from pathlib import Path


def timeout_handler(signum, frame):
    print("Project memory recall timed out (skipped)")
    sys.exit(0)


signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(5)  # 5 second timeout


def find_project_root(cwd: str) -> Path | None:
    """Walk up from CWD to find a directory containing project_memory/."""
    current = Path(cwd).resolve()
    for _ in range(10):
        if (current / "project_memory").is_dir():
            return current
        parent = current.parent
        if parent == current:
            break
        current = parent
    return None


def load_accumulated_knowledge(project_root: Path) -> dict | None:
    """Load accumulated_knowledge.json if it exists."""
    ak_path = project_root / "project_memory" / "accumulated_knowledge.json"
    if not ak_path.exists():
        return None
    try:
        return json.loads(ak_path.read_text())
    except Exception:
        return None


def load_recent_sessions(project_root: Path, limit: int = 3) -> list[dict]:
    """Load the most recent processed session summaries."""
    sessions_dir = project_root / "project_memory" / "sessions"
    if not sessions_dir.exists():
        return []
    try:
        files = sorted(sessions_dir.glob("*.json"), reverse=True)[:limit]
        sessions = []
        for f in files:
            try:
                data = json.loads(f.read_text())
                sessions.append(data)
            except Exception:
                continue
        return sessions
    except Exception:
        return []


def print_knowledge(ak: dict):
    """Print accumulated knowledge in a format Claude can use."""
    print("=== Project Knowledge ===\n")

    if ak.get("decisions"):
        print("## Decisions")
        for d in ak["decisions"]:
            what = d.get("what", "")
            why = d.get("why", "")
            print(f"- {what}")
            if why:
                print(f"  Why: {why}")
            rejected = d.get("alternatives_rejected", [])
            if rejected:
                print(f"  Rejected: {', '.join(rejected)}")
        print()

    if ak.get("patterns"):
        print("## Established Patterns")
        for p in ak["patterns"]:
            pattern = p.get("pattern", "")
            files = p.get("files", [])
            print(f"- {pattern}")
            if files:
                print(f"  Files: {', '.join(files[:3])}")
        print()

    if ak.get("gotchas"):
        print("## Known Gotchas")
        for g in ak["gotchas"]:
            what = g.get("what", "")
            prevent = g.get("prevent", "")
            print(f"- {what}")
            if prevent:
                print(f"  Prevent: {prevent}")
        print()

    if ak.get("technical_learnings"):
        print("## Technical Learnings")
        for t in ak["technical_learnings"]:
            if isinstance(t, str):
                print(f"- {t}")
            elif isinstance(t, dict):
                print(f"- {t.get('learning', '')}")
        print()

    if ak.get("open_threads"):
        print("## Open Threads")
        for o in ak["open_threads"]:
            if isinstance(o, str):
                print(f"- {o}")
            elif isinstance(o, dict):
                print(f"- {o.get('thread', '')} (from {o.get('session', 'unknown')})")
        print()

    if ak.get("dependencies"):
        deps = ak["dependencies"]
        if deps.get("added"):
            print("## Dependencies Added")
            for name, version in deps["added"].items():
                print(f"- {name}@{version}")
            print()

    stats = []
    if ak.get("total_sessions"):
        stats.append(f"Sessions: {ak['total_sessions']}")
    if ak.get("last_updated"):
        stats.append(f"Updated: {ak['last_updated']}")
    if stats:
        print(f"[{' | '.join(stats)}]")


def print_recent_sessions(sessions: list[dict]):
    """Print recent session summaries."""
    if not sessions:
        return
    print("\n## Recent Sessions")
    for s in sessions:
        date = s.get("date", "unknown")
        summary = s.get("summary", "No summary")
        session_type = s.get("type", "unknown")
        print(f"\n[{date}] ({session_type})")
        print(f"{summary}")
        open_threads = s.get("open_threads", [])
        if open_threads:
            for t in open_threads:
                print(f"  OPEN: {t}")


def main():
    # Detect project root from CWD
    import os
    cwd = os.getcwd()

    project_root = find_project_root(cwd)
    if not project_root:
        sys.exit(0)  # No project_memory/ found, skip silently

    # Load accumulated knowledge
    ak = load_accumulated_knowledge(project_root)
    if not ak:
        # Check if there are pending sessions to process
        pending_dir = project_root / "project_memory" / "pending"
        if pending_dir.exists() and list(pending_dir.glob("*.json")):
            print("=== Project Memory ===")
            print("Pending sessions found but not yet processed.")
            print("Run: process project memory sessions")
            print("======================")
        sys.exit(0)

    # Print everything
    print_knowledge(ak)

    # Load and print recent sessions
    recent = load_recent_sessions(project_root)
    print_recent_sessions(recent)

    print("\n=== End Project Knowledge ===")


if __name__ == "__main__":
    main()
