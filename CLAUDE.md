# Helm Vault — Claude Instructions

This is John's vault root. Each subfolder owns its own rules in its own `CLAUDE.md`. This file holds only vault-wide navigation and workflow. When in doubt about a folder's conventions, read that folder's CLAUDE.md.

## Quick Orientation

1. Check the relevant MOC in `10-knowledge/_mocs/` for topic navigation.
2. Follow `[[wiki-links]]` to build understanding.
3. Read the subfolder's CLAUDE.md before writing there. Folder-specific rules live there, not here.

## Folder Structure

| Folder          | Purpose                                                                 | Rules                    |
| --------------- | ----------------------------------------------------------------------- | ------------------------ |
| `00-landing/`   | Parking lot. Manual captures only. Exits: promote to inbox OR delete.   | `00-landing/CLAUDE.md`   |
| `01-inbox/`     | Research queue. Rai enriches each item + rates A/B/C/D + routes.        | `01-inbox/CLAUDE.md`     |
| `02-ana/`       | John's Life OS. `identity/` auto-loads every session.               | `02-ana/CLAUDE.md`       |
| `03-rai/`       | Rai's brain: skills, agents, algorithm, hooks, memory, semantic-memory. | `03-rai/CLAUDE.md`       |
| `04-work/`      | Work footprint. Engagement subfolders + `work-plans/` (ISO week).       | `04-work/CLAUDE.md`      |
| `05-projects/`  | `kitchen/` → `active/` → `completed/`. Code lives in `~/projects/`.     | `05-projects/CLAUDE.md`  |
| `06-learning/`  | Courses & tutorials. Kebab-case topics, Phase/Module allowed.           | `06-learning/CLAUDE.md`  |
| `07-reading/`   | Books through Claude Code. Full coverage, not summaries.                | `07-reading/CLAUDE.md`   |
| `08-bawaba/`    | News digest output (`/news-digest`). LIVE — never delete `daily/` files. | `08-bawaba/CLAUDE.md`    |
| `09-ideas/`     | Seed → Plant → Tree → Graduated. Flat, status in frontmatter.           | `09-ideas/CLAUDE.md`     |
| `10-knowledge/` | Topic notes, MOCs, Insights. Simplicity Theorem on every note.          | `10-knowledge/CLAUDE.md` |
| `11-workflows/` | Repeatable playbooks (independent from skills).                         | `11-workflows/CLAUDE.md` |
| `12-system/`    | Templates (`templates/`), references, snippets, diagrams.               | `12-system/CLAUDE.md`    |
| `13-archive/`   | Session JSONs + frozen exceptions (`news/`, `learning/`). See its CLAUDE.md. | `13-archive/CLAUDE.md`   |

## Archive vs Delete

**Archive only session JSONs** (`/process-sessions` drains them to `13-archive/historical-sessions/`). Sessions are cheap to store and the forensic/wisdom-mining value compounds.

**Delete everything else** once it's no longer live. Git log is the archive for text content.

**Two standing exceptions** (John-approved 2026-06-10, detailed in `13-archive/CLAUDE.md`): `13-archive/news/` (prior digests, moved there automatically by the news skill after each run) and `13-archive/learning/` (retired curricula, frozen reference). Never purge these — a 2026-06-11 maintenance run deleted both plus the live `08-bawaba/daily/` digest by following this section without the exceptions, and it all had to be restored. Deleting content is never part of a commit run's job; commit what exists.

## Capture pipeline

```
00-landing/              01-inbox/                 destination
(manual drops)  ─────▶   (research + rating)  ───▶ 07-reading, 06-learning,
                                                    10-knowledge, 09-ideas,
                                                    05-projects, 04-work
```

Triggered via the `/triage` skill group: `process-landing` for landing triage, `process-inbox` for inbox research.

## Idea pipeline

```
09-ideas/                         05-projects/                  ~/projects/
Seed → Plant → Tree → Graduated ──▶ kitchen/{name}/ ──▶ active/{name}/ + ~/projects/{name}/
                                    (PRD, arch, design)  (non-code + code)
                                           │
                                           ▼
                                    completed/{name}/
                                    (retrospective + diagrams)
```

Triggered via the `/ideas` skill group: `start-seed`, `promote`, `graduate`, `derive`.

## Identity auto-load

At session start, Rai auto-loads every `*.md` file in:
- `03-rai/identity/` — Rai config (persona, steering, response, coding format)
- `02-ana/identity/` — John's self-model (who-i-am, goals, vision, mindset, story, wrong, projects, ideas, contacts, definitions, environment, tech-stack)

To add or remove a file from session context, move it in or out of an `identity/` folder.

Non-`.md` files in identity/ are NOT auto-loaded (they're for specific hooks/skills).

## Skill groups (routers in `03-rai/skills/`)

Life, work, and vault rhythm:
- `/life` — telos, quote (self-model + wisdom capture)
- `/routine` — journal, today-prep, tomorrow-prep, weekly-retro (daily/weekly rhythm)
- `/work` — weekly-planner, meeting-prep
- `/triage` — process-landing, process-inbox

Learning & knowledge:
- `/learning` — start-topic, teach, quiz, audit-coverage
- `/reading` — start-book, teach, audit-coverage
- `/knowledge` — new-topic-note, insight, audit-moc, find-connections
- `/ideas` — start-seed, promote, graduate, derive

Plus: `/news-digest`, `/research`, `/investigation`, `/security`, `/mac`, `/ubuntu`, `/devops`, `/architecture`, `/git`, `/testing`, `/coding-standards`, `/ai`, `/data`, `/business`, `/content-analysis`, `/media`, `/scraping`, `/recall`, `/rai`, `/think`, `/map-updater`.

## Templates

Always use existing templates from `12-system/templates/`. Never invent note structures. Full inventory in `12-system/CLAUDE.md`.
