"""Shared session-name derivation for auto-work-creation + session-auto-name."""

import re

from .prd_template import slugify

NOISE_WORDS = {
    "a", "an", "and", "are", "at", "be", "but", "by", "can", "could",
    "did", "do", "does", "done", "for", "from", "had", "has", "have",
    "he", "her", "him", "his", "how", "i", "if", "in", "into", "is",
    "it", "its", "lets", "let", "make", "me", "my", "need", "no", "not",
    "of", "on", "one", "or", "our", "please", "should", "so", "some",
    "that", "the", "their", "them", "then", "there", "these", "they",
    "this", "those", "to", "us", "use", "want", "was", "we", "were",
    "what", "when", "where", "which", "who", "why", "will", "with",
    "would", "you", "your",
}


def _words(text: str) -> list[str]:
    cleaned = re.sub(r"[^\w\s-]", " ", text)
    return [w for w in cleaned.split() if w]


def short_name(prompt: str, word_count: int = 3) -> str:
    """Human-readable 2-3 word name with noise words filtered."""
    words = _words(prompt.lower())
    meaningful = [w for w in words if w not in NOISE_WORDS and len(w) > 2]
    if not meaningful:
        return "Session"
    return " ".join(w.capitalize() for w in meaningful[:word_count])


def work_slug(prompt: str, max_len: int = 40) -> str:
    """Kebab-case slug suitable for filesystem paths. Strips noise words first."""
    words = _words(prompt.lower())
    meaningful = [w for w in words if w not in NOISE_WORDS and len(w) > 2]
    if not meaningful:
        meaningful = words[:6] or ["untitled"]
    joined = " ".join(meaningful[:6])
    return slugify(joined, max_len)
