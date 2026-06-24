"""Shared learning utilities for hook system."""

ALGORITHM_KEYWORDS = [
    "workflow", "process", "planning", "algorithm",
    "approach", "methodology", "strategy", "pattern",
    "decision", "architecture", "design", "refactor",
]

SYSTEM_KEYWORDS = [
    "tool", "config", "setup", "install", "deploy",
    "build", "test", "debug", "fix", "error",
    "hook", "script", "api", "database", "server",
]


def get_learning_category(description: str) -> str:
    """
    Categorize learning as SYSTEM or ALGORITHM.
    ALGORITHM: process improvements, workflow patterns.
    SYSTEM: technical learnings, code patterns, tool usage.
    """
    text = description.lower()
    algo_score = sum(1 for kw in ALGORITHM_KEYWORDS if kw in text)
    sys_score = sum(1 for kw in SYSTEM_KEYWORDS if kw in text)
    return "algorithm" if algo_score > sys_score else "system"


def is_learning_capture(text: str) -> bool:
    """Detect if text contains a learning moment."""
    indicators = [
        "learned", "realized", "discovered", "found that",
        "turns out", "mistake", "better way", "should have",
        "next time", "lesson", "insight", "pattern",
    ]
    lower = text.lower()
    return any(ind in lower for ind in indicators)
