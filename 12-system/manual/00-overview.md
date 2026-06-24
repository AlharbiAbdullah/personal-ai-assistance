# 00 — Overview

The vault is a brain folder. It is one principal's externalized cognition, paired with one AI assistant who runs against it every session.

> Last updated: 2026-06-14. This manual is a compiled overview; the live source of truth is the CLAUDE.md files and the source under `03-rai/`.

## Two principals

| Principal | Identity folder | Role |
|-----------|----------------|------|
| **John** (the human) | `02-ana/identity/` | Owns the brain. Drops captures, makes decisions, runs the rituals. |
| **Rai** (the AI) | `03-rai/identity/` | Operates the brain. Loads identity at session start. Executes skills, runs the Algorithm, writes PRDs, manages memory. |

The two identity folders are auto-loaded into every session. That is the contract: anything Rai needs to know about John lives in `02-ana/identity/`. Anything John needs to configure about Rai lives in `03-rai/identity/`. Both folders, both directions, every session. Today that is 13 `.md` files on John's side and 4 on Rai's side — 17 files total.

## What "brain folder" means

This is not a notes app. It is a working operating system for one person:

- **Capture in** — fleeting thoughts, articles, ideas, news, courses, books, projects all enter through a defined pipeline (00-landing → 01-inbox → destination).
- **Compounding knowledge** — topic notes consolidate everything understood about a domain. Maps of Content (MOCs) hub them.
- **Idea pipeline** — every promising idea enters as a Seed, gets researched into a Plant, planned as a Tree, and graduates into a Project.
- **Project lifecycle** — kitchen (planning) → active (in progress) → completed (retrospective). Code lives in `~/projects/`, planning lives here.
- **Personal OS** — journal, todos, goals, vision, mindset, family, health, financial, admin, travel, quotes, shopping — all in `02-ana/`.
- **Investing practice** — a values-based paper-trading sandbox in `02-ana/financial/investment/`, operated by `/investment` and run on a cloud droplet. Strictly spot, no leverage; real money is deferred.
- **Work footprint** — paid engagements get their own subfolder. ISO-week plans aggregate across them.
- **Daily and weekly news** — `/news-digest` produces a curated gem feed from HN, Reddit, X, Substack, Medium, and GitHub Trending. The weekly run is the "Bawaba Weekly" magazine.
- **Reflective writing** — soul notes and personal chapters in `02-ana/soul/`.

The vault holds all of this. Rai operates against all of this. The Algorithm makes Rai do it well.

## The 14 top-level folders

Numbered 00 through 13 plus dotfiles and a few root working files. Numbers are stable — they imply a rough lifecycle order from "raw capture" (00) to "preserved sessions" (13). Reordering is not allowed; numbers are part of the contract.

```
00-landing/      Parking lot for manual drops
01-inbox/        Research queue (Rai enriches and routes)
02-ana/          John's life OS (identity auto-loads)
03-rai/          Rai's brain (skills, agents, hooks, memory, algorithm)
04-work/         Work footprint (engagements + ISO-week plans)
05-projects/     Project lifecycle (kitchen → active → completed)
06-learning/     Courses and tutorials (curriculum format)
07-reading/      Books through Claude Code (full coverage)
08-bawaba/       News digest output (daily/ + weekly/)
09-ideas/        Idea pipeline (Seed → Plant → Tree → Graduated)
10-knowledge/    Topic notes, MOCs, Insight Notes
11-workflows/    Numbered playbooks (humans follow these)
12-system/       Templates, references, snippets, diagrams, manual
13-archive/      Session JSONs (+ two standing exceptions: news/, learning/)
```

Plus, at the vault root:

```
CLAUDE.md        Root navigation + the two pipelines + auto-load contract
north-star.md    Live Kanban board (Obsidian kanban-plugin)
scratch-board.md Root-level working scratch space
Excalidraw/      Tracked Excalidraw drawing files
.helm-index/     Auto-maintained navigation index (helm-index.md)
.obsidian/       Editor config (not a system concern)
.gitattributes   `03-rai/memory/**/*.jsonl merge=union` (append-only logs union-merge)
.gitignore       Brain-repo policy: secrets + machine droppings only
.git / .claude   Git repo and local harness overrides (settings.local.json)
```

Note: `.codemap/` does NOT exist in the helm vault. `/map-updater` only creates `.codemap/codemap.md` inside a code project under `~/projects/{name}/`, never here.

Full per-folder reference is in [01-folder-map.md](./01-folder-map.md).

## The five governing rules

These are not opinions. They are the rules that keep the vault from drifting.

### Rule 1 — Identity auto-load is the contract

Every `*.md` file inside `02-ana/identity/` (13 files) and `03-rai/identity/` (4 files) is loaded into every session at SessionStart. This is the only mechanism for "always-on context." To add a fact to context, drop the `.md` file in identity/. To remove, move it out. No code change required.

Non-`.md` files in identity/ (like `security-patterns.yaml`) are NOT auto-loaded. They are read by specific hooks at runtime.

### Rule 2 — Delete over archive

> **Archive only session JSONs** (`/process-sessions` drains them to `13-archive/historical-sessions/`). Sessions are cheap to store and the forensic/wisdom-mining value compounds. **Delete everything else** once it's no longer live. Git log is the archive for text content.

This is from the root CLAUDE.md and is non-negotiable. There is no `archive/` folder for stale notes. There is no `_done/` folder. If something is no longer useful, it gets deleted. Git history is the archive.

Two standing exceptions (John-approved 2026-06-10) live in `13-archive/`: `news/` (prior digests + full raw dumps, moved automatically by the news skill after each run) and `learning/` (retired curricula, frozen reference). Never purge these — a 2026-06-11 maintenance run deleted them plus a live digest by following the delete rule without the exceptions, and it all had to be restored. Deleting content is never part of a commit run's job; commit what exists.

### Rule 3 — CLAUDE.md is the live source of truth

Every numbered folder owns a CLAUDE.md with its own rules. The vault root has a CLAUDE.md too. When you need to know how a folder behaves, read its CLAUDE.md. When references in this manual contradict a folder's CLAUDE.md, CLAUDE.md wins.

### Rule 4 — Always use existing templates

> Always use existing templates from `12-system/templates/`. Never invent note structures.

There are 16 templates (15 note `.md` files plus `ISC.json`). Every note type John uses has a template. Inventing structure is a failure mode that fragments the vault. Read the template, copy it, fill it in.

### Rule 5 — Min Capabilities is binding (Algorithm rule)

If an Algorithm tier requires N capabilities and you list one, you MUST invoke it via the `Skill` or `Task` tool. Writing prose that resembles the skill's output does not count. Listing without invoking is a CRITICAL FAILURE. This is the rule that keeps the Algorithm honest.

Full algorithm rules in [06-algorithm-and-prd.md](./06-algorithm-and-prd.md).

## How content flows through the vault

Two main pipelines, both governed by skills.

**Capture pipeline** — anything from outside the vault enters via 00-landing or directly into a relevant folder. The triage path is:

```
00-landing/  ──/triage process-landing──▶  01-inbox/  ──/triage process-inbox──▶  destination
(manual drops)                            (research + rate)                       (07, 06, 10, 09, 05, 04)
```

**Idea pipeline** — promising ideas grow inside `09-ideas/` and graduate into projects:

```
09-ideas/                              05-projects/                  ~/projects/
Seed → Plant → Tree → Graduated   ──▶  kitchen/{name}/   ──▶   active/{name}/ + ~/projects/{name}/
                                       (PRD, arch, design)         (non-code + code)
                                              │
                                              ▼
                                       completed/{name}/
                                       (retrospective + diagrams)
```

Both pipelines are documented in detail: [04-capture-pipeline.md](./04-capture-pipeline.md) and [05-idea-lifecycle.md](./05-idea-lifecycle.md).

## How Rai operates

When a session starts, the SessionStart hooks (`session-start.py` then `check-version.py`) load identity, sweep orphan state files, and read recent ChromaDB memories. Rai now has full context.

When the user asks for something non-trivial, Rai enters the Algorithm. The Algorithm (v3.7.0) has 7 phases — OBSERVE, THINK, PLAN, BUILD, EXECUTE, VERIFY, LEARN. Each phase has rules. An effort tier (Standard / Extended / Advanced / Deep / Comprehensive) fixes the time budget, the ISC floor, and the minimum number of capabilities. The Algorithm writes a PRD as it goes. The PRD is the system of record.

When the user asks for something trivial (a greeting, a quick lookup, a simple fix), Rai skips the Algorithm and answers directly.

When Rai needs a specialized capability, it invokes a skill (`/research`, `/news-digest`, `/triage`, `/ideas`, `/investment`, etc.) or spawns an agent (`Task(subagent_type: "engineer")`, `architect`, `pentester`, etc.). There are 35 top-level skills (30 routers plus 5 leaves — `ask-model`, `map-updater`, `project-init`, `visual-plan`, `workflow`) covering roughly 128 sub-skills, and 12 agents (10 specialists plus the `algorithm` and `researcher` methodology agents).

When the session ends, SessionEnd runs 7 hooks in order — `save-memory`, `work-completion-learning`, `session-summary`, `relationship-memory`, `update-counts`, `integrity-check`, `algorithm-scan` — saving the transcript to `semantic-memory/pending/`, logging learnings, saving relationship signals, running integrity checks, and cleaning up state files. The pending session waits there until `/rai process-sessions` drains it into ChromaDB. ChromaDB is a single-writer store: only the Linux coordinator box ("pc") embeds into it; the Mac is a read-only replica (see the sync note below).

Full session walkthrough: [03-session-lifecycle.md](./03-session-lifecycle.md).

## A note on sync

Since 2026-06-13 the vault is synced under a single-coordinator model. The Linux box "pc" is the sole maintenance coordinator and the only writer to GitHub and to ChromaDB. The Mac is a passive replica that refreshes from Linux over Tailscale SSH and never touches GitHub. The authoritative document is `03-rai/SYNC-ARCHITECTURE.md`. The brain's internal design still has "no remote sync" as a principle — sync lives at the ops layer, outside the brain itself.

## Where things live (one-line locator)

| Thing | Location |
|-------|----------|
| Vault root | `~/helm/` |
| Rai brain | `~/helm/03-rai/` |
| John's identity | `~/helm/02-ana/identity/` |
| Rai's identity | `~/helm/03-rai/identity/` |
| Algorithm spec | `~/helm/03-rai/algorithm/v3.7.0.md` (pointer: `algorithm/latest`) |
| Skills | `~/helm/03-rai/skills/{router}/SKILL.md` |
| Agents | `~/helm/03-rai/agents/{name}.md` |
| Hooks | `~/helm/03-rai/hooks/*.py` |
| Hooks wired to events (canonical) | `~/helm/03-rai/config/settings.json` (via symlink `~/.claude/settings.json`) |
| File memory | `~/helm/03-rai/memory/{state,work,learning,relationship,security}/` |
| ChromaDB (single-writer) | `~/helm/03-rai/semantic-memory/chromadb/` |
| Pending sessions | `~/helm/03-rai/semantic-memory/pending/` |
| Sync contract | `~/helm/03-rai/SYNC-ARCHITECTURE.md` |
| Investing sandbox | `~/helm/02-ana/financial/investment/` |
| Templates | `~/helm/12-system/templates/` |
| Workflows | `~/helm/11-workflows/` |
| Manual (this folder) | `~/helm/12-system/manual/` |
| Archived sessions | `~/helm/13-archive/historical-sessions/` |
| Code (outside vault) | `~/projects/{name}/` |

## Audience for this manual

| Reader | Path |
|--------|------|
| New human operator | 00 → 01 → 02 → 06 → 21 |
| AI session looking up a rule | jump to relevant chapter via README |
| Debugging a hook or skill | 09 → 17 → 20 |
| Adding a new skill | 07 → 11 |
| Adding a new agent | 08 |
| Writing a new note | 11 → 12 |
| Managing the idea/project pipeline | 05 → 14 |
| Running the Algorithm well | 06 → 21 |

## What this manual does not replace

- **CLAUDE.md files** — those are the live rules. Always check the relevant CLAUDE.md when you need certainty.
- **The Algorithm spec** — `03-rai/algorithm/v3.7.0.md` is the canonical algorithm definition. This manual summarizes it; the spec is final.
- **Skill SKILL.md files** — each skill's detailed steps live in its own SKILL.md. This manual catalogs and points; the SKILL.md executes.
- **Agent definitions** — each agent's detailed scope lives in `03-rai/agents/{name}.md`. This manual catalogs; the file defines.
- **`03-rai/SYNC-ARCHITECTURE.md`** — the live sync contract. This manual only acknowledges it; that file is the source of truth.

The manual is a compiled overview. The source files in `03-rai/` and the CLAUDE.md files are the truth.
