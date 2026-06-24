#!/usr/bin/env python3
"""
Session End Hook - Fast JSON file storage (no AI calls).
Saves transcript to pending/ for later summarization.

Extracts metadata:
- duration_minutes: Session length from timestamps
- files_modified: Full paths from Edit/Write tool calls
- tools_summary: Count of each tool used
- project_name: From .git, pyproject.toml, package.json, or folder
- cwd: Working directory for continuation detection
"""

import json
import re
import subprocess
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from lib.hook_errors import log_error
from lib.hook_timer import hook_timer
from lib.transcript_parse import iter_assistant_tool_uses


PENDING_DIR = Path.home() / "helm" / "03-rai" / "semantic-memory" / "pending"
CONTEXT_MAPPING_FILE = Path.home() / ".claude" / "hooks" / "context_mapping.json"


def load_context_mapping() -> dict:
    """Load path-to-context mapping from config file."""
    if CONTEXT_MAPPING_FILE.exists():
        try:
            return json.loads(CONTEXT_MAPPING_FILE.read_text())
        except Exception:
            pass
    return {}


def detect_project_name(cwd: str) -> str:
    """Detect project name from .git, pyproject.toml, package.json, or folder."""
    cwd_path = Path(cwd)

    # Check for .git and parse remote URL or folder name
    git_dir = cwd_path / ".git"
    if git_dir.exists():
        try:
            result = subprocess.run(
                ["git", "-C", cwd, "config", "--get", "remote.origin.url"],
                capture_output=True,
                text=True,
                timeout=2,
            )
            if result.returncode == 0 and result.stdout.strip():
                url = result.stdout.strip()
                # Extract repo name from URL (handles .git suffix)
                match = re.search(r"/([^/]+?)(?:\.git)?$", url)
                if match:
                    return match.group(1)
        except Exception:
            pass

    # Check for pyproject.toml
    pyproject = cwd_path / "pyproject.toml"
    if pyproject.exists():
        try:
            content = pyproject.read_text()
            match = re.search(r'^\s*name\s*=\s*["\']([^"\']+)["\']', content, re.MULTILINE)
            if match:
                return match.group(1)
        except Exception:
            pass

    # Check for package.json
    package_json = cwd_path / "package.json"
    if package_json.exists():
        try:
            data = json.loads(package_json.read_text())
            if data.get("name"):
                return data["name"]
        except Exception:
            pass

    # Fallback to folder name
    return cwd_path.name


def apply_context_mapping(cwd: str) -> str:
    """Map CWD to a context name using context_mapping.json."""
    mapping = load_context_mapping()
    cwd_expanded = str(Path(cwd).expanduser().resolve())

    for pattern, context_name in mapping.items():
        pattern_expanded = str(Path(pattern).expanduser().resolve())

        # Handle wildcard patterns
        if "*" in pattern_expanded:
            base_pattern = pattern_expanded.rstrip("/*")
            if cwd_expanded.startswith(base_pattern):
                if context_name == "auto-detect":
                    return detect_project_name(cwd)
                return context_name

        # Exact match or subdirectory
        if cwd_expanded == pattern_expanded or cwd_expanded.startswith(pattern_expanded + "/"):
            if context_name == "auto-detect":
                return detect_project_name(cwd)
            return context_name

    # No mapping found - auto-detect
    return detect_project_name(cwd)


def count_messages(transcript_path: Path) -> tuple[int, int]:
    """Count human and assistant messages in transcript."""
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
                    msg_type = entry.get("type")
                    if msg_type == "user":
                        human_count += 1
                    elif msg_type == "assistant":
                        assistant_count += 1
                except json.JSONDecodeError:
                    continue
    except Exception:
        pass

    return human_count, assistant_count


def get_cwd(transcript_path: Path) -> str:
    """Extract working directory from first line."""
    try:
        with open(transcript_path) as f:
            first_line = f.readline().strip()
            if first_line:
                entry = json.loads(first_line)
                return entry.get("cwd", "")
    except Exception:
        pass
    return ""


def get_context(transcript_path: Path) -> str:
    """Extract working directory context from first line."""
    cwd = get_cwd(transcript_path)
    if cwd:
        return apply_context_mapping(cwd)
    return "brainstorm"


def extract_timestamps(transcript_path: Path) -> tuple[str | None, str | None]:
    """Extract first and last timestamps from transcript."""
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
    """Calculate session duration in minutes from timestamps."""
    if not first_ts or not last_ts:
        return 0

    try:
        # Handle ISO format timestamps
        first = datetime.fromisoformat(first_ts.replace("Z", "+00:00"))
        last = datetime.fromisoformat(last_ts.replace("Z", "+00:00"))
        duration_seconds = (last - first).total_seconds()
        return max(0, int(duration_seconds / 60))
    except Exception:
        return 0


def extract_tool_usage(transcript_path: Path) -> tuple[dict, list[str]]:
    """Tool counts + unique Edit/Write file paths. Uses shared transcript walker."""
    tools_counter: Counter = Counter()
    files_modified: set[str] = set()
    for tool_use in iter_assistant_tool_uses(str(transcript_path)):
        name = tool_use.get("name", "")
        if name:
            tools_counter[name] += 1
        if name in ("Edit", "Write", "NotebookEdit"):
            fp = tool_use.get("input", {}).get("file_path", "")
            if fp:
                files_modified.add(fp)
    return dict(tools_counter), sorted(files_modified)


def save_pending_session(
    session_id: str,
    transcript_path: Path,
    context: str,
    cwd: str,
    project_name: str,
    duration_minutes: int,
    tools_summary: dict,
    files_modified: list[str],
):
    """Save session transcript as JSON file in pending directory."""
    PENDING_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = PENDING_DIR / f"session_{timestamp}.json"

    # Read transcript and save with metadata
    session_data = {
        "session_id": session_id,
        "timestamp": datetime.now().isoformat(),
        "context": context,
        "transcript_path": str(transcript_path),
        # New metadata fields
        "cwd": cwd,
        "project_name": project_name,
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
                    # Only keep user and assistant messages
                    if entry.get("type") in ("user", "assistant"):
                        session_data["messages"].append({
                            "type": entry.get("type"),
                            "message": entry.get("message", ""),
                        })
                except json.JSONDecodeError:
                    continue
    except Exception:
        return

    # Write to pending file
    output_file.write_text(json.dumps(session_data, indent=2))


def cleanup_temp_files(session_id: str):
    """Remove temp session files if they exist."""
    session_path_file = Path(f"/tmp/claude_session_{session_id}.path")
    if session_path_file.exists():
        try:
            session_file = Path(session_path_file.read_text().strip())
            session_path_file.unlink(missing_ok=True)
            if session_file.exists():
                session_file.unlink(missing_ok=True)
        except Exception:
            pass


def log_debug(msg: str):
    """Write debug log."""
    log_file = Path.home() / ".claude" / "logs" / "save-memory-debug.log"
    log_file.parent.mkdir(parents=True, exist_ok=True)
    with open(log_file, "a") as f:
        f.write(f"[{datetime.now().isoformat()}] {msg}\n")


def main():
    log_debug("Hook started")

    try:
        raw_input = sys.stdin.read()
        log_debug(f"Raw input: {raw_input[:500]}")
        input_data = json.loads(raw_input)
    except json.JSONDecodeError as e:
        log_debug(f"JSON decode error: {e}")
        log_error("save-memory", e, "stdin decode")
        sys.exit(0)

    session_id = input_data.get("session_id", "")
    transcript_path = input_data.get("transcript_path", "")
    log_debug(f"session_id: {session_id}, transcript_path: {transcript_path}")

    # Cleanup old temp files
    cleanup_temp_files(session_id)

    # Validate transcript
    if not transcript_path or not Path(transcript_path).exists():
        log_debug(f"Transcript not found or empty path")
        sys.exit(0)

    transcript_path = Path(transcript_path)

    # Count messages
    human_count, _ = count_messages(transcript_path)
    log_debug(f"Human message count: {human_count}")

    # Skip trivial sessions (< 4 human messages)
    if human_count < 4:
        log_debug(f"Skipping: only {human_count} human messages")
        sys.exit(0)

    # Extract all metadata
    cwd = get_cwd(transcript_path)
    context = get_context(transcript_path)
    project_name = detect_project_name(cwd) if cwd else "unknown"

    # Calculate duration from timestamps
    first_ts, last_ts = extract_timestamps(transcript_path)
    duration_minutes = calculate_duration(first_ts, last_ts)

    # Extract tool usage and files modified
    tools_summary, files_modified = extract_tool_usage(transcript_path)

    log_debug(f"Context: {context}, Project: {project_name}")
    log_debug(f"Duration: {duration_minutes}m, Tools: {tools_summary}")
    log_debug(f"Files modified: {len(files_modified)}")

    # Save to pending directory (fast, no AI)
    save_pending_session(
        session_id=session_id,
        transcript_path=transcript_path,
        context=context,
        cwd=cwd,
        project_name=project_name,
        duration_minutes=duration_minutes,
        tools_summary=tools_summary,
        files_modified=files_modified,
    )
    log_debug(f"Session saved to pending")


if __name__ == "__main__":
    with hook_timer("save-memory"):
        try:
            main()
        except Exception as e:
            log_error("save-memory", e, "main")
