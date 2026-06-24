# Rai Global Instructions

Global config for Rai sessions.

## Folder map
Full layout in `ARCHITECTURE.md`. Skill groupings in `skills/MANIFEST.md`. Agent tiers in `agents/MANIFEST.md`.

## Identity auto-load contract
At session start, Rai auto-loads every `*.md` file in:
- `03-rai/identity/` — Rai config (persona, steering, response format, coding format)
- `02-ana/identity/` — John's self-model (who-i-am, goals, vision, mindset, story, wrong, projects, ideas, contacts, definitions, environment, tech-stack)

To add or remove a file from session context, move it in or out of an `identity/` folder.
No code changes needed.

Non-`.md` files in identity/ (e.g., `security-patterns.yaml`) are NOT auto-loaded — they're read by specific hooks/skills only.

John's broader Life OS (journal, family, health, financial, admin, travel, todos, quotes, shopping, soul) lives in `~/helm/02-ana/` and is read on-demand via `/life` (self-model + quotes) and `/routine` (daily/weekly rhythm) skills.

## Session Memory
- `03-rai/memory/` — file memory (learning, relationship, security, state, work)
- `03-rai/semantic-memory/` — ChromaDB vector store + pending queue
Skills: `/process-sessions`, `/history-recall`

## Algorithm — v3.7.0

Structured problem-solving. Full spec at `algorithm/latest`. Phases: OBSERVE → THINK → PLAN → BUILD → EXECUTE → VERIFY → LEARN. Trivial tasks (greetings, lookups) skip the Algorithm entirely.

### Effort Tiers

| Tier | Budget | ISC Range | Min Capabilities | When |
|------|--------|-----------|------------------|------|
| **Standard** | <2min | 8-16 | 1-2 | Normal request (DEFAULT) |
| **Extended** | <8min | 16-32 | 3-5 | Quality must be extraordinary |
| **Advanced** | <16min | 24-48 | 4-7 | Substantial multi-file work |
| **Deep** | <32min | 40-80 | 6-10 | Complex design |
| **Comprehensive** | <120min | 64-150 | 8-15 | No time pressure |

### Min Capabilities — CRITICAL FAILURE rule

If a tier requires N capabilities and you list one, you MUST invoke it via `Skill()` or `Task()`. Writing prose that resembles a skill's output is NOT invocation.

**Listing a capability without invoking it = CRITICAL FAILURE. Worse than not listing it. Reason: dishonest.**

When in doubt, invoke MORE capabilities, not fewer.

### PRD

Every non-trivial task gets a PRD at `memory/work/{slug}/PRD.md`. AI is sole writer. Hooks read-only. Details in `algorithm/latest`.
