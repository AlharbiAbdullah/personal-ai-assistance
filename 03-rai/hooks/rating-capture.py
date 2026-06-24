#!/usr/bin/env python3
"""
UserPromptSubmit Hook: Rating Capture.

Detects explicit numeric ratings (1-10) in user prompts.
Writes to memory/learning/SIGNALS/ratings.jsonl.
Low ratings (<6) trigger a learning file in memory/learning/SYSTEM/.

Rejects false positives like "3 items", "5th element", ordinals.
Timeout: 5s. Always exits 0.
"""

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


def timeout_handler(signum, frame):
    sys.exit(0)


signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(5)

PAI_DIR = Path(os.environ.get("PAI_DIR") or Path.home() / "helm" / "03-rai")
SIGNALS_DIR = PAI_DIR / "memory" / "learning" / "signals"
SYSTEM_DIR = PAI_DIR / "memory" / "learning" / "system"

# Pattern: line starts with a number 1-10, optionally followed
# by separator and comment. Must be the primary content, not
# embedded in a longer sentence.
RATING_RE = re.compile(
    r"^\s*(10|[1-9])\s*(?:[-:/]\s*|\s+)(.*)$",
    re.IGNORECASE,
)

# False positive indicators: the number is part of a count,
# ordinal, list reference, or other non-rating context.
FALSE_POSITIVE_RE = re.compile(
    r"(?:"
    r"\d+\s*(?:items?|things?|files?|steps?|times?|ways?|points?|"
    r"minutes?|hours?|days?|pages?|lines?|errors?|bugs?|tests?|"
    r"results?|options?|examples?|commits?|PRs?|issues?)"
    r"|"
    r"\d+(?:st|nd|rd|th)\b"
    r"|"
    r"(?:top|first|last|next|step|item|number|#|no\.?)\s*\d+"
    r"|"
    r"\d+\.\d+"  # decimals like 3.14
    r"|"
    r"\d+\s*(?:am|pm|gb|mb|kb|ms|px|em|rem|vh|vw|%)"
    r")",
    re.IGNORECASE,
)


def is_rating(prompt: str) -> tuple[int, str] | None:
    """
    Check if prompt is an explicit rating.
    Returns (score, comment) or None.
    """
    prompt = prompt.strip()

    # Skip long messages (ratings are short)
    if len(prompt) > 200:
        return None

    # Skip if it looks like a false positive
    if FALSE_POSITIVE_RE.search(prompt):
        return None

    match = RATING_RE.match(prompt)
    if not match:
        return None

    score = int(match.group(1))
    comment = match.group(2).strip() if match.group(2) else ""

    # Extra guard: if there's no comment and the prompt has
    # more words after the number, it's probably not a rating
    remaining = prompt[match.end(1):].strip()
    if remaining and not comment:
        # Check if the rest looks like a sentence (not a rating)
        words = remaining.split()
        if len(words) > 10:
            return None

    return (score, comment)


def write_rating(
    score: int,
    comment: str,
    session_id: str,
    prompt: str,
):
    """Append rating to ratings.jsonl."""
    SIGNALS_DIR.mkdir(parents=True, exist_ok=True)

    entry = {
        "timestamp": datetime.now().isoformat(),
        "session_id": session_id,
        "score": score,
        "comment": comment,
        "raw_prompt": prompt[:200],
    }

    ratings_file = SIGNALS_DIR / "ratings.jsonl"
    with open(ratings_file, "a") as f:
        f.write(json.dumps(entry) + "\n")


def write_low_rating_learning(
    score: int,
    comment: str,
    session_id: str,
):
    """For scores <6, write a learning file for review."""
    now = datetime.now()
    month_dir = SYSTEM_DIR / now.strftime("%Y-%m")
    month_dir.mkdir(parents=True, exist_ok=True)

    learning = {
        "timestamp": now.isoformat(),
        "session_id": session_id,
        "type": "low_rating",
        "score": score,
        "comment": comment,
        "action_needed": "Review session for improvement patterns",
    }

    filename = f"low-rating-{score}-{now.strftime('%Y%m%d_%H%M%S')}.json"
    filepath = month_dir / filename
    filepath.write_text(json.dumps(learning, indent=2))


def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw)
    except Exception as e:
        log_error("rating-capture", e, "stdin decode")
        sys.exit(0)

    prompt = data.get("prompt", "")
    session_id = data.get("session_id", "unknown")

    if not prompt:
        sys.exit(0)

    try:
        result = is_rating(prompt)
        if result is None:
            return
        score, comment = result
        write_rating(score, comment, session_id, prompt)
        if score < 6:
            write_low_rating_learning(score, comment, session_id)
    except Exception as e:
        log_error("rating-capture", e, f"session={session_id}")


if __name__ == "__main__":
    with hook_timer("rating-capture"):
        main()
