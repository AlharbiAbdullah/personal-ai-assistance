"""Validation for tab titles and output text."""

import re

GERUND_RE = re.compile(r"^[A-Z][a-z]+ing\b")
PAST_TENSE_MAP = {
    "fixing": "Fixed",
    "adding": "Added",
    "updating": "Updated",
    "creating": "Created",
    "building": "Built",
    "implementing": "Implemented",
    "refactoring": "Refactored",
    "testing": "Tested",
    "deploying": "Deployed",
    "configuring": "Configured",
    "reviewing": "Reviewed",
    "writing": "Wrote",
    "reading": "Read",
    "setting": "Set",
    "running": "Ran",
    "debugging": "Debugged",
    "analyzing": "Analyzed",
    "designing": "Designed",
    "migrating": "Migrated",
    "installing": "Installed",
    "removing": "Removed",
    "deleting": "Deleted",
    "moving": "Moved",
    "renaming": "Renamed",
    "merging": "Merged",
    "resolving": "Resolved",
    "optimizing": "Optimized",
    "researching": "Researched",
    "investigating": "Investigated",
    "planning": "Planned",
}


def is_valid_working_title(title: str) -> bool:
    """Validate working title: gerund verb, 2-4 words."""
    if not title:
        return False
    words = title.rstrip(".").split()
    if len(words) < 2 or len(words) > 5:
        return False
    return bool(GERUND_RE.match(title))


def gerund_to_past_tense(title: str) -> str:
    """Convert gerund title to past tense."""
    words = title.rstrip(".").split()
    if not words:
        return title
    first = words[0].lower()
    past = PAST_TENSE_MAP.get(first)
    if past:
        words[0] = past
        return " ".join(words) + "."
    # Generic: strip "ing", add "ed"
    if first.endswith("ing"):
        stem = first[:-3]
        words[0] = stem.capitalize() + "ed"
        return " ".join(words) + "."
    return title
