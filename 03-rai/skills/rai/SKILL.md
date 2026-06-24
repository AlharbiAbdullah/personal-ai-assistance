---
name: rai
description: >
  Rai brain maintenance router. USE WHEN the user wants to healthcheck
  the brain, ingest sessions to memory, compose specialized agents,
  create or validate skills, or extract upgrade opportunities. Routes
  between sanity, process-sessions, compose-agents, create-skill, upgrade.
---

# Rai

Maintain the brain itself. Meta-skills that operate on Rai's own
structure (skills, memory, agents, config).

## Routing table

| Task | Sub-skill | File to Read |
|------|-----------|--------------|
| End-to-end healthcheck (hooks, skills, memory, vault, symlinks, config) | sanity | `sanity.md` |
| Drain `semantic-memory/pending/` into ChromaDB | process-sessions | `process-sessions.md` |
| Spawn specialized custom agents; orchestrate parallel runs | compose-agents | `compose-agents.md` |
| Create a new skill (naming, folder layout, SKILL.md validation) | create-skill | `create-skill.md` |
| Extract improvement opportunities for the Rai system | upgrade | `upgrade.md` |

## How to use

1. Pick the sub-skill by maintenance task.
2. `Read` the file in this directory.
3. Follow that file's instructions.

## When two could fit

- **sanity vs create-skill:** sanity verifies the whole brain is healthy; create-skill validates ONE skill's structure.
- **sanity vs process-sessions:** sanity reports on state; process-sessions changes state (writes to memory).
- **compose-agents vs create-skill:** agents are persona+capability specs; skills are workflow definitions.
- **upgrade vs sanity:** upgrade identifies what to improve; sanity identifies what is broken.

## Cross-references

- Memory retrieval → `/recall/history`
- Skill gaps inbox → `skills/GAPS.md`
- Skill ownership map → `skills/MANIFEST.md`
