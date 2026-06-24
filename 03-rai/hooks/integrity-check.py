#!/usr/bin/env python3
"""
SessionEnd Hook: Integrity Check.

Detects edits to Rai system files during a session. Writes a per-change
record under memory/learning/system/integrity/. Rotates old records by
mtime (not filename parsing).
"""

import json
import signal
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from lib.hook_errors import log_error
from lib.hook_timer import hook_timer
from lib.paths import get_pai_dir, get_settings_path
from lib.time_utils import get_filename_timestamp, get_iso_timestamp
from lib.transcript_parse import extract_modified_files

RETENTION_DAYS = 30
DEFAULT_EXCLUDE = ("memory/work", "memory/learning", "memory/state", "scratch")


def timeout_handler(signum, frame):
    sys.exit(0)


signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(5)

PAI_DIR = get_pai_dir()


def _load_exclude() -> tuple[str, ...]:
    """Allow settings.json to override the exclude list via integrityCheck.exclude."""
    try:
        settings = json.loads(get_settings_path().read_text())
        cfg = settings.get("integrityCheck", {}).get("exclude")
        if isinstance(cfg, list) and cfg:
            return tuple(str(x) for x in cfg)
    except Exception:
        pass
    return DEFAULT_EXCLUDE


def _rotate_old_logs(log_dir: Path) -> None:
    """Drop integrity records whose mtime is older than RETENTION_DAYS."""
    cutoff = time.time() - (RETENTION_DAYS * 86400)
    for p in log_dir.glob("change-*.json"):
        try:
            if p.stat().st_mtime < cutoff:
                p.unlink()
        except OSError:
            pass


def check_system_integrity(modified_files: list[str]) -> None:
    pai_str = str(PAI_DIR)
    exclude = _load_exclude()
    system_files = [
        f for f in modified_files
        if f.startswith(pai_str) and not any(skip in f for skip in exclude)
    ]

    if not system_files:
        return

    log_dir = PAI_DIR / "memory" / "learning" / "system" / "integrity"
    log_dir.mkdir(parents=True, exist_ok=True)
    _rotate_old_logs(log_dir)
    log_file = log_dir / f"change-{get_filename_timestamp()}.json"
    log_file.write_text(json.dumps({
        "timestamp": get_iso_timestamp(),
        "modified_system_files": system_files,
        "action": "review_recommended",
    }, indent=2))


def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw)
    except Exception as e:
        log_error("integrity-check", e, "stdin decode")
        sys.exit(0)

    transcript_path = data.get("transcript_path", "")
    try:
        modified = extract_modified_files(transcript_path)
        if modified:
            check_system_integrity(modified)
    except Exception as e:
        log_error("integrity-check", e, f"transcript={transcript_path}")


if __name__ == "__main__":
    with hook_timer("integrity-check"):
        main()
