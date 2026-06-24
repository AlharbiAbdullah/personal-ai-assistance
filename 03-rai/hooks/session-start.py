#!/usr/bin/env python3
"""
SessionStart Hook - Load Rai identity files + memories.

Reads identity files (with mtime cache) and memories from ChromaDB.
CWD-aware:
- Inside ~/helm/... : ALL memories (full document text)
- Elsewhere         : last 7 rolling days only

Emits a compact status line at the end so slow hooks / pending backlog are visible.
Graceful: missing files are skipped. Timeout: 8s.
"""

import json
import os
import re
import signal
import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from lib.hook_errors import log_error
from lib.hook_timer import hook_timer


def timeout_handler(signum, frame):
    print("Rai identity load timed out (8s)")
    sys.exit(0)


signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(8)

PAI_DIR = Path(os.environ.get("PAI_DIR") or Path.home() / "helm" / "03-rai")
IDENTITY_DIR = PAI_DIR / "identity"
SKILLS_DIR = PAI_DIR / "skills"
BRAIN_DIR = Path.home() / "helm"
TELOS_DIR = BRAIN_DIR / "02-ana"
CHROMADB_PATH = BRAIN_DIR / "03-rai" / "semantic-memory" / "chromadb"
PENDING_DIR = BRAIN_DIR / "03-rai" / "semantic-memory" / "pending"
IDENTITY_CACHE = PAI_DIR / "memory" / "state" / "identity-cache.json"

PENDING_WARN = 20
CODEMAP_MAX_BYTES = 20_000
CODEMAP_MAX_WALKS = 3
HELM_INDEX_PATH = BRAIN_DIR / ".helm-index" / "helm-index.md"
HELM_INDEX_MAX_BYTES = 20_000

IDENTITY_DIRS = [IDENTITY_DIR, TELOS_DIR / "identity"]


def _label_from_path(path: Path) -> str:
    return path.stem.replace("-", " ").replace("_", " ").title()


def _discover_identity_files() -> list[tuple[str, Path]]:
    """Scan identity directories for *.md files. Returns sorted (label, path) pairs.

    Contract: anything in `03-rai/identity/` and `02-ana/identity/` auto-loads.
    Non-.md files (e.g., security-patterns.yaml) are intentionally skipped.
    """
    files: list[tuple[str, Path]] = []
    for d in IDENTITY_DIRS:
        if not d.exists():
            continue
        for path in sorted(d.glob("*.md")):
            files.append((_label_from_path(path), path))
    return files


def _sweep_orphans_safe() -> dict:
    """Clean orphan state files from crashed sessions. Never fail identity load."""
    try:
        from lib.paths import get_state_dir
        from lib.state_sweep import sweep_orphans

        session_id = ""
        try:
            raw = sys.stdin.read() if not sys.stdin.isatty() else ""
            if raw:
                session_id = json.loads(raw).get("session_id", "")
        except (json.JSONDecodeError, OSError):
            pass
        return sweep_orphans(session_id, get_state_dir())
    except Exception as e:
        log_error("session-start", e, "orphan sweep")
        return {}


def _sources_max_mtime(files: list[tuple[str, Path]]) -> float:
    m = 0.0
    for _, path in files:
        try:
            if path.exists():
                m = max(m, path.stat().st_mtime)
        except OSError:
            pass
    return m


def _load_identity_cached() -> tuple[list[str], bool]:
    """Return (sections, was_cached). mtime-invalidated."""
    files = _discover_identity_files()
    max_mtime = _sources_max_mtime(files)
    cache_key = [str(p) for _, p in files]
    try:
        if IDENTITY_CACHE.exists():
            cache = json.loads(IDENTITY_CACHE.read_text())
            if (
                isinstance(cache, dict)
                and cache.get("max_mtime", 0.0) >= max_mtime
                and cache.get("files") == cache_key
                and isinstance(cache.get("sections"), list)
            ):
                return cache["sections"], True
    except Exception:
        pass

    sections: list[str] = []
    for label, path in files:
        try:
            text = path.read_text().strip()
        except Exception:
            text = ""
        if text:
            sections.append(f"## {label}\n{text}")

    try:
        IDENTITY_CACHE.parent.mkdir(parents=True, exist_ok=True)
        IDENTITY_CACHE.write_text(json.dumps({
            "max_mtime": max_mtime,
            "files": cache_key,
            "sections": sections,
        }))
    except Exception as e:
        log_error("session-start", e, "identity cache write")

    return sections, False


def _validate_skills() -> list[str]:
    """Return list of malformed-skill issues. Empty = all clean.

    Lightweight regex check (no yaml dep): each skill folder must hold a
    SKILL.md with --- frontmatter containing name: and description: fields.
    Catches the failure mode where a stricter Claude Code skill loader would
    reject the file and surface a transient "N skills didn't load" at launch.
    """
    issues: list[str] = []
    if not SKILLS_DIR.exists():
        return issues
    for skill_dir in sorted(SKILLS_DIR.iterdir()):
        if not skill_dir.is_dir() or skill_dir.name.startswith("."):
            continue
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.is_file():
            issues.append(f"{skill_dir.name}: missing SKILL.md")
            continue
        try:
            txt = skill_md.read_text()
        except OSError:
            issues.append(f"{skill_dir.name}: unreadable SKILL.md")
            continue
        m = re.match(r"^---\n(.*?)\n---", txt, re.DOTALL)
        if not m:
            issues.append(f"{skill_dir.name}: no frontmatter")
            continue
        fm = m.group(1)
        if not re.search(r"^name:\s*\S", fm, re.MULTILINE):
            issues.append(f"{skill_dir.name}: missing 'name' field")
        if not re.search(r"^description:\s*[\|>]?\s*\S", fm, re.MULTILINE):
            issues.append(f"{skill_dir.name}: missing 'description' field")
    return issues


def _count_pending() -> int:
    if not PENDING_DIR.exists():
        return 0
    try:
        return sum(1 for _ in PENDING_DIR.glob("session_*.json"))
    except OSError:
        return 0


def in_brain_vault(cwd: Path) -> bool:
    try:
        cwd.resolve().relative_to(BRAIN_DIR.resolve())
        return True
    except ValueError:
        return False


def find_codemap(cwd: Path) -> Path | None:
    """Walk up from cwd looking for .codemap/codemap.md. Checks cwd + up to CODEMAP_MAX_WALKS parents."""
    try:
        cur = cwd.resolve()
    except OSError:
        return None
    for _ in range(CODEMAP_MAX_WALKS + 1):
        candidate = cur / ".codemap" / "codemap.md"
        try:
            if candidate.is_file() and candidate.stat().st_size <= CODEMAP_MAX_BYTES:
                return candidate
        except OSError:
            pass
        if cur.parent == cur:
            return None
        cur = cur.parent
    return None


def find_helm_index() -> Path | None:
    try:
        if HELM_INDEX_PATH.is_file() and HELM_INDEX_PATH.stat().st_size <= HELM_INDEX_MAX_BYTES:
            return HELM_INDEX_PATH
    except OSError:
        pass
    return None


def load_memories(full: bool) -> tuple[list[str], int]:
    try:
        import chromadb

        client = chromadb.PersistentClient(path=str(CHROMADB_PATH))
        collection = client.get_collection("memories")
        result = collection.get(include=["metadatas", "documents"])

        if not result.get("documents"):
            return [], 0

        memories = [
            {"doc": doc, "meta": result["metadatas"][i]}
            for i, doc in enumerate(result.get("documents", []))
        ]
        memories.sort(key=lambda x: x["meta"].get("date", ""), reverse=True)

        if not full:
            cutoff = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
            memories = [m for m in memories if m["meta"].get("date", "") >= cutoff]

        lines = []
        for m in memories:
            meta = m["meta"]
            doc = m["doc"]
            date = meta.get("date", "?")
            ctx = meta.get("context", "") or meta.get("type", "")
            prefix = f"[{date}]"
            if ctx:
                prefix += f" {ctx}:"
            body = doc.strip() if full else doc[:200].replace("\n", " ").strip()
            lines.append(f"{prefix} {body}")
        return lines, len(memories)
    except Exception as e:
        log_error("session-start", e, "load memories")
        return [], 0


def main():
    sweep_counts = _sweep_orphans_safe()

    if not PAI_DIR.exists():
        sys.exit(0)

    sections, was_cached = _load_identity_cached()

    cwd = Path(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd())
    full = in_brain_vault(cwd)

    helm_index_path = find_helm_index()
    if helm_index_path:
        try:
            helm_index_text = helm_index_path.read_text().strip()
            if helm_index_text:
                sections.append(f"## Helm Index\n{helm_index_text}")
        except OSError as e:
            log_error("session-start", e, "helm-index load")

    codemap_path = find_codemap(cwd)
    if codemap_path:
        try:
            codemap_text = codemap_path.read_text().strip()
            if codemap_text:
                sections.append(f"## Codemap ({codemap_path.parent.parent})\n{codemap_text}")
        except OSError as e:
            log_error("session-start", e, "codemap load")

    mem_lines, mem_count = load_memories(full=full)
    if mem_lines:
        header = (
            f"## Memory (FULL vault scope, {mem_count} memories)"
            if full
            else f"## Memory (last 7 days, {mem_count} memories)"
        )
        sections.append(header + "\n" + "\n\n".join(mem_lines))

    pending = _count_pending()

    if sections:
        tag = "cached" if was_cached else "fresh"
        print(f"=== Rai Identity Loaded ({tag}) ===\n")
        print("\n\n".join(sections))
        print("\n=== End Rai Identity ===")

    skill_issues = _validate_skills()
    if skill_issues:
        print("\n[skill-validator] Malformed SKILL.md files:")
        for issue in skill_issues:
            print(f"  - {issue}")

    swept = sum(sweep_counts.values()) if sweep_counts else 0
    status_bits = [f"memories={mem_count}", f"identity={tag if sections else 'none'}"]
    if swept:
        status_bits.append(f"orphans_swept={swept}")
    if pending:
        status_bits.append(f"pending={pending}")
        if pending >= PENDING_WARN:
            status_bits.append("WARN: run /process-sessions")
    if skill_issues:
        status_bits.append(f"skills_bad={len(skill_issues)}")
    print(f"[rai] {' '.join(status_bits)}")


if __name__ == "__main__":
    with hook_timer("session-start"):
        try:
            main()
        except Exception as e:
            log_error("session-start", e, "main")
