---
name: telos
description: >
  Life OS and personal organizational analysis.
  USE WHEN the user wants to update life goals, extract wisdom from
  conversations, review their belief system, or generate life reports.
---

# Telos

Personal operating system for goals, beliefs, mental models, and wisdom.
Reads from and writes to `~/helm/02-ana/`. Provides structured introspection and narrative synthesis.

## Source of truth

All telos content lives in `~/helm/02-ana/`. Index: `telos.md`.

### Identity (`identity/`)

- `who-i-am.md` — current self-snapshot
- `story.md` — biographical arc, formative hardships
- `vision.md` — core purpose, time horizons, current blockers, problems being solved
- `mindset.md` — values, frames, beliefs, principles, mental models, external wisdom
- `goals.md` — this year's targets
- `projects.md` — active, completed, personal projects
- `wrong.md` — things I was wrong about

### Soul (`soul/`)

Timeless reflective writing. Authoring rules in `soul/CLAUDE.md`.

- `on-failure.md` and any future soul essays

### Living data

- `family/` — `jane.md`, `sam.md`, `zoe.md`, `calendar.md`
- `health/` — `health-overview.md`, `medications.md`, `supplements.md`, `recovery-plan.md`, `specialists.md`
- `financial/` — `budget.md`, `assets.md`, `debt-plan.md`
- `admin/` — `documents.md`, `maintenance.md`
- `travel/` — `bucket-list.md`, `log.md`
- `journal/` — daily entries (managed by `/journal`)
- `todos/` — `today-plans/`, `tomorrow-plans/` (managed by `/today-prep`, `/tomorrow-prep`)
- `quotes/` — external quotes, one file per quote
- `shopping/` — active purchase research

### Top-level reference

- `telos.md` — index of everything above
- `contacts.md` — people I know
- `environment.md` — digital assets (directories, accounts, hardware)
- `tech-stack.md` — technical preferences
- `definitions.md` — personal terminology
- `ideas.md` — ideas in exploration (full lifecycle in `09-ideas/`)

## Workflows

### Update
Modify any telos file based on new information.
Steps: read current state, identify what changed, update file, note the reason for the change.

### InterviewExtraction
Extract telos-relevant insights from a conversation or text.
Steps: scan content for beliefs, goals, principles, mental models, or narrative points.
Cross-reference with existing telos content. Present new findings for user approval before writing.

### CreateNarrativePoints
Generate a narrative summary of the user's current trajectory.
Steps: read `identity/` files and `soul/` essays, identify themes, synthesize into a coherent story about where the user is heading.

### WriteReport
Produce a structured life report.
Steps: compile goal progress from `identity/goals.md`, active work from `identity/projects.md`, belief or principle changes in `identity/mindset.md` since last report, new entries in `identity/wrong.md`.
Output as a dated report document.

## Guidelines

- Never modify telos files without user confirmation
- Track change history (what changed and why)
- Cross-reference new entries against existing beliefs for conflicts
- Flag goal-belief misalignment when detected
- Write in English. Never Arabic.

## Examples

- "Update my goals: I'm shifting focus to [new area]"
- "Extract principles from today's conversation"
- "Write a telos report for this month"
- "Review my beliefs for internal contradictions"
