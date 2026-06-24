#!/usr/bin/env python3
"""
PreToolUse Hook: Security Validator.

Validates Bash commands and file operations against security patterns.
Matchers: Bash, Edit, Write, Read.

Pattern loading cascade:
  1. identity/security-patterns.yaml (user customized)
  2. security-patterns.example.yaml (fallback)

Security levels for Bash:
  - blocked: exit 2 (never allowed)
  - confirm: stdout JSON with askUser (user prompted)
  - alert: log + allow

Path protection levels:
  - zeroAccess: block all operations
  - readOnly: block write/delete
  - confirmWrite: confirm before write
  - noDelete: block delete operations

Logs to memory/security/YYYY/MM/.
Fast (<10ms typical). Fail-open on errors.
"""

import fnmatch
import json
import os
import re
import signal
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from lib.hook_errors import log_error
from lib.hook_timer import hook_timer

try:
    import yaml

    HAS_YAML = True
except ImportError:
    HAS_YAML = False


def timeout_handler(signum, frame):
    sys.exit(0)


signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(5)

PAI_DIR = Path(os.environ.get("PAI_DIR") or Path.home() / "helm" / "03-rai")
USER_PATTERNS = PAI_DIR / "identity" / "security-patterns.yaml"
EXAMPLE_PATTERNS = PAI_DIR / "security-patterns.example.yaml"
SECURITY_LOG_DIR = PAI_DIR / "memory" / "security"


def load_patterns() -> dict:
    """Load security patterns from YAML. User file first, then example."""
    if HAS_YAML:
        for path in [USER_PATTERNS, EXAMPLE_PATTERNS]:
            if path.exists():
                try:
                    with open(path) as f:
                        return yaml.safe_load(f) or {}
                except Exception:
                    continue

    # Hardcoded minimal fallback if no YAML available
    return {
        "bash": {
            "blocked": [
                {"pattern": r"rm\s+-(rf|fr)\s+/(\s|$|\*)", "reason": "Filesystem destruction (root)"},
                {"pattern": r"rm\s+-(rf|fr)\s+~(/?(\s|$)|/\*)", "reason": "Home directory destruction"},
                {"pattern": r"sudo\s+rm\s+-(rf|fr)\s+/(\s|$|\*)", "reason": "Filesystem destruction with sudo"},
                {"pattern": r"sudo\s+rm\s+-(rf|fr)\s+~(/?(\s|$)|/\*)", "reason": "Home destruction with sudo"},
                {"pattern": "diskutil eraseDisk", "reason": "Disk destruction"},
                {"pattern": "dd if=/dev/zero", "reason": "Disk overwrite"},
                {"pattern": "mkfs", "reason": "Filesystem format"},
                {"pattern": "gh repo delete", "reason": "Repo deletion"},
            ],
            "confirm": [
                {
                    "pattern": "git push --force",
                    "reason": "Force push can lose commits",
                },
                {
                    "pattern": "git push -f",
                    "reason": "Force push can lose commits",
                },
                {
                    "pattern": "git reset --hard",
                    "reason": "Loses uncommitted changes",
                },
                {"pattern": "DROP DATABASE", "reason": "Database destruction"},
                {"pattern": "DROP TABLE", "reason": "Table destruction"},
                {"pattern": "TRUNCATE", "reason": "Table data destruction"},
                {
                    "pattern": "terraform destroy",
                    "reason": "Infrastructure destruction",
                },
                {
                    "pattern": "docker system prune",
                    "reason": "Container cleanup",
                },
                {
                    "pattern": r"sudo\s+rm\s+-(rf|fr)\b",
                    "reason": "Recursive force delete with sudo",
                },
            ],
            "alert": [
                {
                    "pattern": "curl.*\\|.*sh",
                    "reason": "Piping curl to shell",
                },
                {
                    "pattern": "wget.*\\|.*bash",
                    "reason": "Piping wget to bash",
                },
            ],
        },
        "paths": {
            "zeroAccess": [
                "~/.ssh/id_*",
                "~/.ssh/*.pem",
                "~/.aws/credentials",
                "~/.gnupg/private*",
                "**/credentials.json",
                "**/service-account*.json",
            ],
            "readOnly": ["/etc/**"],
            "confirmWrite": ["**/.env", "**/.env.*", "~/.ssh/*"],
            "noDelete": [".git/**", "LICENSE*", "README.md"],
        },
    }


def log_event(event_type: str, detail: str, tool: str, blocked: bool):
    """Log security event to memory/security/YYYY/MM/."""
    try:
        now = datetime.now()
        log_dir = SECURITY_LOG_DIR / now.strftime("%Y") / now.strftime("%m")
        log_dir.mkdir(parents=True, exist_ok=True)

        entry = {
            "timestamp": now.isoformat(),
            "event": event_type,
            "tool": tool,
            "detail": detail[:500],
            "blocked": blocked,
        }

        log_file = log_dir / f"security-{now.strftime('%Y%m%d')}.jsonl"
        with open(log_file, "a") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception:
        pass  # Logging must never block execution


def expand_home(pattern: str) -> str:
    """Expand ~ to actual home directory in pattern."""
    if pattern.startswith("~"):
        return str(Path.home()) + pattern[1:]
    return pattern


def check_path(
    filepath: str, tool_name: str, patterns: dict
) -> dict | None:
    """
    Check filepath against path protection rules.
    Returns action dict or None if allowed.
    """
    path_rules = patterns.get("paths", {})
    filepath_expanded = str(Path(filepath).expanduser().resolve())

    # Zero access: block all operations
    for pat in path_rules.get("zeroAccess", []):
        expanded = expand_home(pat)
        if fnmatch.fnmatch(filepath_expanded, expanded):
            return {
                "action": "block",
                "reason": f"Zero access path: {pat}",
            }

    # Read-only: block Write/Edit
    if tool_name in ("Write", "Edit"):
        for pat in path_rules.get("readOnly", []):
            expanded = expand_home(pat)
            if fnmatch.fnmatch(filepath_expanded, expanded):
                return {
                    "action": "block",
                    "reason": f"Read-only path: {pat}",
                }

    # Confirm write
    if tool_name in ("Write", "Edit"):
        for pat in path_rules.get("confirmWrite", []):
            expanded = expand_home(pat)
            if fnmatch.fnmatch(filepath_expanded, expanded):
                return {
                    "action": "confirm",
                    "reason": f"Protected path requires confirmation: {pat}",
                }

    # No delete: we can't easily detect delete from Write/Edit,
    # but we can block Bash rm on these paths
    return None


def check_bash(command: str, patterns: dict) -> dict | None:
    """
    Check bash command against security patterns.
    Returns action dict or None if allowed.
    """
    bash_rules = patterns.get("bash", {})

    # Check blocked patterns (regex, like confirm; substring fallback on bad regex)
    for rule in bash_rules.get("blocked", []):
        pat = rule.get("pattern", "")
        reason = rule.get("reason", "Blocked command")
        try:
            if re.search(pat, command):
                return {"action": "block", "reason": reason}
        except re.error:
            if pat in command:
                return {"action": "block", "reason": reason}

    # Check confirm patterns
    for rule in bash_rules.get("confirm", []):
        pat = rule.get("pattern", "")
        reason = rule.get("reason", "Dangerous command")
        # Use regex for patterns with special chars
        try:
            if re.search(pat, command):
                return {"action": "confirm", "reason": reason}
        except re.error:
            if pat in command:
                return {"action": "confirm", "reason": reason}

    # Check alert patterns (log only)
    for rule in bash_rules.get("alert", []):
        pat = rule.get("pattern", "")
        reason = rule.get("reason", "Suspicious command")
        try:
            if re.search(pat, command):
                log_event("alert", f"{reason}: {command}", "Bash", False)
                return None  # Allow but logged
        except re.error:
            if pat in command:
                log_event("alert", f"{reason}: {command}", "Bash", False)
                return None

    return None


def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw)
    except Exception as e:
        # Fail open: if we can't parse input, allow
        log_error("security-validator", e, "stdin decode")
        sys.exit(0)

    tool_name = data.get("tool_name", "")
    tool_input = data.get("tool_input", {})

    if not tool_name:
        sys.exit(0)

    patterns = load_patterns()

    # Bash command validation
    if tool_name == "Bash":
        command = tool_input.get("command", "")
        if not command:
            sys.exit(0)

        result = check_bash(command, patterns)
        if result:
            if result["action"] == "block":
                log_event(
                    "blocked", f"{result['reason']}: {command}", "Bash", True
                )
                # Exit 2 = block the tool call
                print(
                    json.dumps(
                        {"error": f"BLOCKED: {result['reason']}"}
                    ),
                    file=sys.stderr,
                )
                sys.exit(2)
            elif result["action"] == "confirm":
                log_event(
                    "confirm",
                    f"{result['reason']}: {command}",
                    "Bash",
                    False,
                )
                # Output JSON to ask user for confirmation
                print(
                    json.dumps(
                        {
                            "decision": "ask",
                            "message": (
                                f"Security: {result['reason']}. "
                                f"Allow `{command[:100]}`?"
                            ),
                        }
                    )
                )
                sys.exit(0)

        # Pre-commit scan: block `git commit` if staged files match
        # patterns in .pai-protected.json (api keys, PII, AI attribution, etc.)
        if re.search(r"\bgit\s+commit\b", command):
            try:
                from lib.protected_scan import scan_staged_git_files
                hits = scan_staged_git_files()
                if hits:
                    summary_lines = []
                    for path, matches in list(hits.items())[:5]:
                        cats = sorted({m.category for m in matches})
                        summary_lines.append(f"{path}: {', '.join(cats)}")
                    summary = "; ".join(summary_lines)
                    if len(hits) > 5:
                        summary += f"; (+{len(hits)-5} more files)"
                    log_event(
                        "blocked",
                        f"Protected pattern in staged files: {summary}",
                        "Bash",
                        True,
                    )
                    print(
                        json.dumps({
                            "error": (
                                "BLOCKED: staged files contain protected "
                                f"patterns. {summary}. Run "
                                "`python3 -m hooks.lib.protected_scan --staged` "
                                "for full report."
                            )
                        }),
                        file=sys.stderr,
                    )
                    sys.exit(2)
            except Exception as e:
                # Fail open: scanner errors do not block commits
                log_event(
                    "alert",
                    f"protected_scan failed: {e}",
                    "Bash",
                    False,
                )

    # File operation validation (Read, Write, Edit)
    if tool_name in ("Read", "Write", "Edit"):
        filepath = tool_input.get("file_path", "")
        if filepath:
            result = check_path(filepath, tool_name, patterns)
            if result:
                if result["action"] == "block":
                    log_event(
                        "blocked",
                        f"{result['reason']}: {filepath}",
                        tool_name,
                        True,
                    )
                    print(
                        json.dumps(
                            {"error": f"BLOCKED: {result['reason']}"}
                        ),
                        file=sys.stderr,
                    )
                    sys.exit(2)
                elif result["action"] == "confirm":
                    log_event(
                        "confirm",
                        f"{result['reason']}: {filepath}",
                        tool_name,
                        False,
                    )
                    print(
                        json.dumps(
                            {
                                "decision": "ask",
                                "message": (
                                    f"Security: {result['reason']}. "
                                    f"Allow {tool_name} on "
                                    f"`{filepath}`?"
                                ),
                            }
                        )
                    )
                    sys.exit(0)

    # Default: allow
    sys.exit(0)


if __name__ == "__main__":
    with hook_timer("security-validator"):
        main()
