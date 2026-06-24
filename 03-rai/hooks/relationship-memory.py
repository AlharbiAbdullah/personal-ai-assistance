#!/usr/bin/env python3
"""
SessionEnd Hook: Relationship Memory.

Extracts relationship signals from user messages and appends to daily
log in memory/relationship/YYYY-MM/YYYY-MM-DD.md.

Tags:
  W = World fact (objective situation)
  B = Biographical (event this session)
  O = Opinion / preference / belief
"""

import json
import re
import signal
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from lib.hook_errors import log_error
from lib.hook_timer import hook_timer
from lib.paths import get_memory_dir
from lib.time_utils import get_date, get_year_month
from lib.transcript_parse import extract_user_messages


def timeout_handler(signum, frame):
    sys.exit(0)


signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(5)

REL_DIR = get_memory_dir() / "relationship"

PREF_PATTERNS = [
    re.compile(r"\bi (?:prefer|like|want|need|hate|dislike|love|enjoy|avoid)\b", re.I),
    re.compile(r"\b(?:always|never|usually|rarely|tend to) (?:do|use|want|go|work|write|prefer)\b", re.I),
    re.compile(r"\bmy (?:favorite|preferred|go-to|style|approach|rule)\b", re.I),
    re.compile(r"\bi'?m (?:a|an) (?:fan|believer|skeptic|huge|big)\b", re.I),
    re.compile(r"\bdon'?t (?:like|want|do|use|touch|mess with)\b", re.I),
]

FACT_PATTERNS = [
    re.compile(r"\bi (?:work|live|moved|started|joined|run|own|manage|lead)\b", re.I),
    re.compile(r"\bmy (?:team|company|project|job|role|family|partner|wife|husband)\b", re.I),
    re.compile(r"\bwe(?:'re| are) (?:using|building|migrating|running|shipping|on)\b", re.I),
    re.compile(r"\bi'?m (?:based|located|working|living)\s+(?:in|at|on)\b", re.I),
]

BIO_PATTERNS = [
    re.compile(r"\btoday i\b", re.I),
    re.compile(r"\byesterday\b", re.I),
    re.compile(r"\blast (?:night|week|month)\b", re.I),
    re.compile(r"\b(?:happened|experienced|went through)\b", re.I),
]


def _classify(text: str) -> str | None:
    for p in PREF_PATTERNS:
        if p.search(text):
            return "O"
    for p in FACT_PATTERNS:
        if p.search(text):
            return "W"
    for p in BIO_PATTERNS:
        if p.search(text):
            return "B"
    return None


def extract_relationship_signals(transcript_path: str) -> list[dict]:
    signals: list[dict] = []
    seen_prefixes: set[str] = set()
    for text in extract_user_messages(transcript_path):
        tag = _classify(text)
        if not tag:
            continue
        trimmed = text[:200]
        key = trimmed[:80]
        if key in seen_prefixes:
            continue
        seen_prefixes.add(key)
        entry: dict = {"type": tag, "text": trimmed}
        if tag == "O":
            entry["confidence"] = "medium"
        signals.append(entry)
        if len(signals) >= 30:
            break
    return signals


def write_relationship_log(signals: list[dict], session_id: str):
    if not signals:
        return

    month_dir = REL_DIR / get_year_month()
    month_dir.mkdir(parents=True, exist_ok=True)
    log_file = month_dir / f"{get_date()}.md"

    entries = []
    for sig in signals:
        tag = sig["type"]
        text = sig["text"].replace("\n", " ").strip()
        conf = f" [{sig['confidence']}]" if "confidence" in sig else ""
        entries.append(f"- [{tag}]{conf} {text}")

    header = f"\n### Session {session_id[:8]} ({datetime.now().strftime('%H:%M')})\n"
    with log_file.open("a") as f:
        f.write(header + "\n".join(entries) + "\n")


def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw)
    except Exception as e:
        log_error("relationship-memory", e, "stdin decode")
        sys.exit(0)

    session_id = data.get("session_id", "unknown")
    transcript_path = data.get("transcript_path", "")

    try:
        signals = extract_relationship_signals(transcript_path)
        write_relationship_log(signals, session_id)
    except Exception as e:
        log_error("relationship-memory", e, f"session={session_id}")


if __name__ == "__main__":
    with hook_timer("relationship-memory"):
        main()
