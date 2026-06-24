#!/usr/bin/env python3
"""
Project-Level SessionEnd Hook - Save session transcript to project_memory/pending/.

Fast, no AI calls. Extracts metadata from transcript and saves to pending/ for later processing.
Mirrors the global save-memory.py pattern but scoped to the project.

This script is copied into each project's .claude/hooks/ by /project_init.
It detects the project root by walking up from CWD looking for project_memory/.
"""

import json
import re
import subprocess
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path


def find_project_root(cwd: str) -> Path | None:
    """Walk up from CWD to find a directory containing project_memory/."""
    current = Path(cwd).resolve()
    for _ in range(10):  # max 10 levels up
        if (current / "project_memory").is_dir():
            return current
        parent = current.parent
        if parent == current:
            break
        current = parent
    return None


def detect_project_name(project_root: Path) -> str:
    """Detect project name from git, pyproject.toml, package.json, or folder."""
    # Git remote
    try:
        result = subprocess.run(
            ["git", "-C", str(project_root), "config", "--get", "remote.origin.url"],
            capture_output=True, text=True, timeout=2,
        )
        if result.returncode == 0 and result.stdout.strip():
            match = re.search(r"/([^/]+?)(?:\.git)?$", result.stdout.strip())
            if match:
                return match.group(1)
    except Exception:
        pass

    # pyproject.toml
    pyproject = project_root / "pyproject.toml"
    if pyproject.exists():
        try:
            content = pyproject.read_text()
            match = re.search(r'^\s*name\s*=\s*["\']([^"\']+)["\']', content, re.MULTILINE)
            if match:
                return match.group(1)
        except Exception:
            pass

    # package.json
    package_json = project_root / "package.json"
    if package_json.exists():
        try:
            data = json.loads(package_json.read_text())
            if data.get("name"):
                return data["name"]
        except Exception:
            pass

    return project_root.name


def count_messages(transcript_path: Path) -> tuple[int, int]:
    """Count human and assistant messages."""
    human_count = 0
    assistant_count = 0
    try:
        with open(transcript_path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    if entry.get("type") == "user":
                        human_count += 1
                    elif entry.get("type") == "assistant":
                        assistant_count += 1
                except json.JSONDecodeError:
                    continue
    except Exception:
        pass
    return human_count, assistant_count


def extract_timestamps(transcript_path: Path) -> tuple[str | None, str | None]:
    """Extract first and last timestamps."""
    first_ts = None
    last_ts = None
    try:
        with open(transcript_path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    ts = entry.get("timestamp")
                    if ts:
                        if first_ts is None:
                            first_ts = ts
                        last_ts = ts
                except json.JSONDecodeError:
                    continue
    except Exception:
        pass
    return first_ts, last_ts


def calculate_duration(first_ts: str | None, last_ts: str | None) -> int:
    """Calculate session duration in minutes."""
    if not first_ts or not last_ts:
        return 0
    try:
        first = datetime.fromisoformat(first_ts.replace("Z", "+00:00"))
        last = datetime.fromisoformat(last_ts.replace("Z", "+00:00"))
        return max(0, int((last - first).total_seconds() / 60))
    except Exception:
        return 0


def extract_tool_usage(transcript_path: Path) -> tuple[dict, list[str]]:
    """Extract tool usage summary and files modified."""
    tools_counter = Counter()
    files_modified = set()
    try:
        with open(transcript_path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    if entry.get("type") != "assistant":
                        continue
                    content = entry.get("message", {}).get("content", [])
                    if not isinstance(content, list):
                        continue
                    for item in content:
                        if not isinstance(item, dict) or item.get("type") != "tool_use":
                            continue
                        tool_name = item.get("name", "")
                        if tool_name:
                            tools_counter[tool_name] += 1
                        if tool_name in ("Edit", "Write", "NotebookEdit"):
                            file_path = item.get("input", {}).get("file_path", "")
                            if file_path:
                                files_modified.add(file_path)
                except json.JSONDecodeError:
                    continue
    except Exception:
        pass
    return dict(tools_counter), sorted(files_modified)


def get_cwd(transcript_path: Path) -> str:
    """Extract working directory from first entry that has one."""
    try:
        with open(transcript_path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    cwd = entry.get("cwd", "")
                    if cwd:
                        return cwd
                except json.JSONDecodeError:
                    continue
    except Exception:
        pass
    return ""


def main():
    # Read hook input from stdin
    try:
        raw_input = sys.stdin.read()
        input_data = json.loads(raw_input)
    except json.JSONDecodeError:
        sys.exit(0)

    session_id = input_data.get("session_id", "")
    transcript_path_str = input_data.get("transcript_path", "")

    if not transcript_path_str or not Path(transcript_path_str).exists():
        sys.exit(0)

    transcript_path = Path(transcript_path_str)

    # Get CWD and find project root
    cwd = get_cwd(transcript_path)
    if not cwd:
        sys.exit(0)

    project_root = find_project_root(cwd)
    if not project_root:
        sys.exit(0)  # No project_memory/ found, skip

    pending_dir = project_root / "project_memory" / "pending"

    # Count messages — skip trivial sessions
    human_count, _ = count_messages(transcript_path)
    if human_count < 4:
        sys.exit(0)

    # Extract metadata
    project_name = detect_project_name(project_root)
    first_ts, last_ts = extract_timestamps(transcript_path)
    duration_minutes = calculate_duration(first_ts, last_ts)
    tools_summary, files_modified = extract_tool_usage(transcript_path)

    # Save to pending
    pending_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    output_file = pending_dir / f"session_{timestamp}.json"

    session_data = {
        "session_id": session_id,
        "timestamp": datetime.now().isoformat(),
        "project_name": project_name,
        "project_root": str(project_root),
        "cwd": cwd,
        "duration_minutes": duration_minutes,
        "tools_summary": tools_summary,
        "files_modified": files_modified,
        "messages": [],
    }

    try:
        with open(transcript_path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    if entry.get("type") in ("user", "assistant"):
                        session_data["messages"].append({
                            "type": entry.get("type"),
                            "message": entry.get("message", ""),
                        })
                except json.JSONDecodeError:
                    continue
    except Exception:
        sys.exit(0)

    output_file.write_text(json.dumps(session_data, indent=2))


if __name__ == "__main__":
    main()
