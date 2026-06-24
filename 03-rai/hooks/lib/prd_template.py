"""PRD template generator for work system."""

import re
from .time_utils import get_date, get_filename_timestamp


def slugify(text: str, max_len: int = 40) -> str:
    """Convert text to kebab-case slug."""
    slug = text.lower().strip()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = re.sub(r"-+", "-", slug).strip("-")
    return slug[:max_len]


def generate_prd_filename(title: str) -> str:
    """Generate PRD filename: PRD-YYYYMMDD-slug.md."""
    ts = get_filename_timestamp()[:8]
    slug = slugify(title, 30)
    return f"PRD-{ts}-{slug}.md"


def generate_prd_template(title: str, description: str = "") -> str:
    """Generate a PRD markdown template aligned with Algorithm v3.7.0 schema."""
    date = get_date()
    slug = slugify(title, 40)
    return f"""---
type: prd
slug: "{slug}"
tier: TBD
status: DRAFT
created: "{date}"
updated: "{date}"
capabilities_used: []
---

# {title}

## Context

{description or "Filled during OBSERVE phase. What is the current state, what is the desired state, what constraints apply."}

## Criteria

Atomic ISC. Each is 8-12 words, state not action, YES/NO verifiable in <5 seconds.
Apply the Splitting Test: if a criterion can fail on A without B AND on B without A, split it.

- [ ] ISC: {{Criterion 1}}

### Anti-criteria

What must NOT happen. Prefix with `ISC-A`.

- [ ] ISC-A: {{Anti-criterion 1}}

## Decision Log

| Date | Decision | Why |
|------|----------|-----|
| {date} | PRD created | Auto-generated at session start |

## Verification

Walk every criterion at the end. Evidence required, not vibes.

| Criterion | Status | Evidence |
|-----------|--------|----------|

## Capability invocation log

If a capability is listed in PLAN, it MUST be invoked via `Skill()` or `Task()`.
Listing without invoking = CRITICAL FAILURE.

| Capability | Invoked via | When | Result |
|------------|-------------|------|--------|
"""
