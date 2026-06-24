"""
Work index — scan memory/work/ and build a master index at memory/state/work.json.

Lists every active and completed PRD with: slug, tier, status, ISC progress,
capabilities_used. Read-only on PRD files; write-only to work.json.

Usage:
    python3 -m hooks.lib.work_index           # refresh work.json
    python3 hooks/lib/work_index.py           # same, direct invocation
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

try:
    from .paths import get_state_dir, get_work_dir
except ImportError:
    from hooks.lib.paths import get_state_dir, get_work_dir


FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL)
ISC_LINE_RE = re.compile(r"^\s*-\s*\[(?P<box>[ xX])\]\s*ISC(?P<anti>-A)?:\s*(?P<text>.+)$")


def _parse_meta_yaml(path: Path) -> dict:
    """Parse a simple key: value YAML (no nesting). META.yaml is flat."""
    out: dict = {}
    if not path.exists():
        return out
    try:
        for line in path.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or ":" not in line:
                continue
            k, _, v = line.partition(":")
            out[k.strip()] = v.strip()
    except Exception:
        pass
    return out


def _parse_prd_frontmatter(path: Path) -> dict:
    """Pull frontmatter as a flat dict. Tolerant of v1.6 and v3.7 schemas."""
    out: dict = {}
    if not path.exists():
        return out
    try:
        text = path.read_text()
    except Exception:
        return out
    m = FRONTMATTER_RE.search(text)
    if not m:
        return out
    for line in m.group(1).splitlines():
        line = line.rstrip()
        if not line or ":" not in line:
            continue
        k, _, v = line.partition(":")
        out[k.strip()] = v.strip().strip('"')
    return out


def _count_isc(path: Path) -> dict:
    """Count atomic ISC checkboxes in a PRD body."""
    counts = {"total": 0, "done": 0, "anti_total": 0, "anti_done": 0}
    if not path.exists():
        return counts
    try:
        for line in path.read_text().splitlines():
            m = ISC_LINE_RE.match(line)
            if not m:
                continue
            is_anti = bool(m.group("anti"))
            done = m.group("box").lower() == "x"
            if is_anti:
                counts["anti_total"] += 1
                if done:
                    counts["anti_done"] += 1
            else:
                counts["total"] += 1
                if done:
                    counts["done"] += 1
    except Exception:
        pass
    return counts


def _scan_session_dir(session_dir: Path) -> dict | None:
    """Build an index entry for one memory/work/{slug}/ directory."""
    if not session_dir.is_dir():
        return None
    meta = _parse_meta_yaml(session_dir / "META.yaml")
    if not meta:
        return None

    tasks: list[dict] = []
    tasks_dir = session_dir / "tasks"
    if tasks_dir.is_dir():
        for task_dir in sorted(tasks_dir.iterdir()):
            if not task_dir.is_dir() or task_dir.name == "current":
                continue
            prd_path = task_dir / "PRD.md"
            fm = _parse_prd_frontmatter(prd_path)
            isc = _count_isc(prd_path)
            tasks.append({
                "task_id": task_dir.name,
                "slug": fm.get("slug") or task_dir.name,
                "tier": fm.get("tier", "TBD"),
                "status": fm.get("status", "UNKNOWN"),
                "capabilities_used": fm.get("capabilities_used", "[]"),
                "isc_total": isc["total"],
                "isc_done": isc["done"],
                "isc_anti_total": isc["anti_total"],
                "isc_anti_done": isc["anti_done"],
            })

    return {
        "id": meta.get("id", session_dir.name),
        "title": meta.get("title", ""),
        "session_id": meta.get("session_id", ""),
        "status": meta.get("status", "UNKNOWN"),
        "created_at": meta.get("created_at", ""),
        "completed_at": meta.get("completed_at", ""),
        "tasks": tasks,
    }


def build_index() -> dict:
    """Scan memory/work/ and return the full index dict."""
    work_dir = get_work_dir()
    if not work_dir.exists():
        return {"sessions": [], "summary": {"sessions": 0, "tasks": 0}}

    sessions: list[dict] = []
    for entry in sorted(work_dir.iterdir()):
        item = _scan_session_dir(entry)
        if item:
            sessions.append(item)

    total_tasks = sum(len(s["tasks"]) for s in sessions)
    active = sum(1 for s in sessions if s["status"] == "ACTIVE")
    completed = sum(1 for s in sessions if s["status"] == "COMPLETED")

    return {
        "sessions": sessions,
        "summary": {
            "sessions": len(sessions),
            "tasks": total_tasks,
            "active": active,
            "completed": completed,
        },
    }


def write_index() -> Path:
    """Build the index and write to memory/state/work.json."""
    index = build_index()
    state_dir = get_state_dir()
    state_dir.mkdir(parents=True, exist_ok=True)
    out = state_dir / "work.json"
    out.write_text(json.dumps(index, indent=2))
    return out


if __name__ == "__main__":
    path = write_index()
    summary = json.loads(path.read_text()).get("summary", {})
    print(f"Wrote {path}")
    print(f"  sessions: {summary.get('sessions', 0)}")
    print(f"  tasks: {summary.get('tasks', 0)}")
    print(f"  active: {summary.get('active', 0)}")
    print(f"  completed: {summary.get('completed', 0)}")
