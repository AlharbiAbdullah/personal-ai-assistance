"""
Scanner for .pai-protected.json patterns.

Loads the patterns file once, exposes scan(text) and scan_staged_git_files()
helpers. Returns a list of (category, pattern, sample) tuples for any matches.

Used by security-validator.py to block `git commit` when staged files contain
sensitive data. Can also be invoked manually:

    python3 -m hooks.lib.protected_scan path/to/file.txt
    python3 -m hooks.lib.protected_scan --staged   # scan staged git files
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Match:
    category: str
    pattern: str
    sample: str
    severity: str = "medium"


def _patterns_path() -> Path:
    """Locate .pai-protected.json. Defaults to PAI_DIR or fallback."""
    import os
    pai = os.environ.get("PAI_DIR")
    if pai:
        p = Path(pai).expanduser().resolve() / ".pai-protected.json"
        if p.exists():
            return p
    # Fallback: walk up from this file to find Rai root
    here = Path(__file__).resolve()
    for ancestor in [here.parent.parent.parent, here.parent.parent, here.parent]:
        candidate = ancestor / ".pai-protected.json"
        if candidate.exists():
            return candidate
    # Last resort: try ~/helm/03-rai/
    home_path = Path.home() / "helm" / "03-rai" / ".pai-protected.json"
    if home_path.exists():
        return home_path
    raise FileNotFoundError("Could not locate .pai-protected.json")


def load_patterns() -> dict:
    return json.loads(_patterns_path().read_text())


def _allowed_by_context(text_window: str, allowed_prefixes: list[str]) -> bool:
    """Return True if any allowed-prefix fragment appears within the same line/window."""
    lower = text_window.lower()
    return any(prefix.lower() in lower for prefix in allowed_prefixes)


def scan(text: str, patterns: dict | None = None) -> list[Match]:
    """Scan text against all categories. Returns list of Match objects."""
    if patterns is None:
        patterns = load_patterns()

    cats = patterns.get("categories", {})
    exception_ctx = patterns.get("exception_contexts", {}).get("allowed_prefixes", [])
    out: list[Match] = []

    for cat_name, cat_def in cats.items():
        severity = cat_def.get("severity", "medium")
        for pat in cat_def.get("patterns", []):
            try:
                rx = re.compile(pat)
            except re.error:
                continue
            for m in rx.finditer(text):
                # Check the line containing the match for an allowed prefix
                start_line = text.rfind("\n", 0, m.start()) + 1
                end_line = text.find("\n", m.end())
                if end_line < 0:
                    end_line = len(text)
                line = text[start_line:end_line]
                if _allowed_by_context(line, exception_ctx):
                    continue
                sample = m.group(0)
                if len(sample) > 80:
                    sample = sample[:77] + "..."
                out.append(Match(cat_name, pat, sample, severity))

    return out


def scan_file(path: Path, patterns: dict | None = None) -> list[Match]:
    if not path.exists() or not path.is_file():
        return []
    try:
        text = path.read_text(errors="replace")
    except Exception:
        return []
    return scan(text, patterns)


def _staged_files() -> list[Path]:
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=AM"],
            capture_output=True, text=True, timeout=5,
        )
        if result.returncode != 0:
            return []
        return [Path(line.strip()) for line in result.stdout.splitlines() if line.strip()]
    except Exception:
        return []


def scan_staged_git_files() -> dict:
    """Return {file: [Match]} for any staged file with matches."""
    patterns = load_patterns()
    exception_files = set(patterns.get("exception_files", []))
    out: dict[str, list[Match]] = {}

    for f in _staged_files():
        # Exception list lives at repo root relative paths
        if str(f) in exception_files:
            continue
        # Wildcard match for exception_files entries
        skip = False
        for ex in exception_files:
            if "*" in ex:
                pattern = re.escape(ex).replace(r"\*", ".*")
                if re.fullmatch(pattern, str(f)):
                    skip = True
                    break
        if skip:
            continue

        if not f.exists():
            continue
        matches = scan_file(f, patterns)
        if matches:
            out[str(f)] = matches

    return out


def _format_report(by_file: dict) -> str:
    lines = []
    for path, matches in by_file.items():
        lines.append(f"FILE: {path}")
        for m in matches:
            lines.append(f"  [{m.severity}] {m.category}: {m.sample}")
    return "\n".join(lines)


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] in ("--staged", "-s"):
        result = scan_staged_git_files()
        if not result:
            print("No protected patterns found in staged files.")
            sys.exit(0)
        print(_format_report(result))
        sys.exit(1)
    target = Path(sys.argv[1])
    matches = scan_file(target)
    if not matches:
        print(f"No matches in {target}.")
        sys.exit(0)
    for m in matches:
        print(f"  [{m.severity}] {m.category}: {m.sample}")
    sys.exit(1)
