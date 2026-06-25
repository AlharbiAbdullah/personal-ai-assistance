# 01 — Folder Map

Every folder in the helm vault, with rules quoted from each CLAUDE.md. The numbered folders 00-13 are the canonical structure. Numbers are stable. Reordering is not allowed.

> **Last updated:** 2026-06-14. The live source of truth for any folder's rules is that folder's `CLAUDE.md`; this chapter is a snapshot and points to it.

## Quick reference

| # | Folder | Purpose | Auto-loaded |
|---|--------|---------|-------------|
| 00 | `00-landing/` | Parking lot for manual drops | No |
| 01 | `01-inbox/` | Research queue (Rai enriches and routes) | No |
| 02 | `02-ana/` | John's Life OS | `identity/*.md` only |
| 03 | `03-rai/` | Rai's brain (skills, agents, hooks, memory, algorithm) | `identity/*.md` only |
| 04 | `04-work/` | Work footprint (engagements + ISO-week plans) | No |
| 05 | `05-projects/` | Project lifecycle (kitchen → active → completed) | No |
| 06 | `06-learning/` | Courses and tutorials | No |
| 07 | `07-reading/` | Books through Claude Code | No |
| 08 | `08-bawaba/` | News digest output (daily/ + weekly/) | No |
| 09 | `09-ideas/` | Idea pipeline (Seed → Plant → Tree → Graduated) | No |
| 10 | `10-knowledge/` | Topic notes, MOCs, Insight Notes | No |
| 11 | `11-workflows/` | Numbered playbooks (humans follow these) | No |
| 12 | `12-system/` | Templates, references, snippets, diagrams, manual | No |
| 13 | `13-archive/` | Session JSONs + two standing exceptions (news/, learning/) | No |

Plus the dotfiles and root-extras section at the bottom.

---

## Vault root

**Path:** `~/helm/`
**CLAUDE.md:** `~/helm/CLAUDE.md`

Quoted rules:

> Each subfolder owns its own rules in its own `CLAUDE.md`. This file holds only vault-wide navigation and workflow. When in doubt about a folder's conventions, read that folder's CLAUDE.md.

> **Archive only session JSONs** (`/process-sessions` drains them to `13-archive/historical-sessions/`). Sessions are cheap to store and the forensic/wisdom-mining value compounds.
>
> **Delete everything else** once it's no longer live. Git log is the archive for text content.

The Archive-vs-Delete section was materially expanded since 2026-04-22 with two standing exceptions:

> **Two standing exceptions** (John-approved 2026-06-10, detailed in `13-archive/CLAUDE.md`): `13-archive/news/` (prior digests, moved there automatically by the news skill after each run) and `13-archive/learning/` (retired curricula, frozen reference). Never purge these — a 2026-06-11 maintenance run deleted both plus the live `08-bawaba/daily/` digest by following this section without the exceptions, and it all had to be restored. Deleting content is never part of a commit run's job; commit what exists.

> Always use existing templates from `12-system/templates/`. Never invent note structures.

The root CLAUDE.md is loaded into every Claude Code session. It is the navigational table of contents and the source of the two pipelines (capture, ideas), the auto-load contract, and the skill-group listing.

### Root-extra files NOT covered by a numbered folder

These tracked root files are live working surfaces. They are not in any `NN-` folder and the old manual never listed them:

| File / folder | What it is |
|---------------|-----------|
| `north-star.md` | An Obsidian Kanban board (`kanban-plugin: board` frontmatter; To Do / etc. columns). A live working board at root. |
| `scratch-board.md` | A working scratch doc (root-level scratch space). |
| `Excalidraw/` | Excalidraw drawing files (e.g. `Drawing 2026-04-20 19.34.48.excalidraw.md`). Tracked. |

The dotfolders (`.helm-index/`, `.obsidian/`, `.git/`, `.claude/`) and dotfiles (`.gitignore`, `.gitattributes`) are covered in the Dotfiles section below.

---

## 00-landing

**Path:** `~/helm/00-landing/`
**CLAUDE.md:** `~/helm/00-landing/CLAUDE.md`
**Purpose:** A place for thoughts to land. No research, no organization, no processing required. Pre-triage.

### Rules

> Writers: manual editor drops only. **Claude must not create, move, or edit files here.**

Strict flat structure. No subfolders. Two exits only: move to `01-inbox/` OR delete. No archive path.

> Ignore by default. Do not scan for context unless John explicitly references a file.

> Treat referenced content as low-confidence fragments.

### Entry / exit

```
Manual drops (user only) → Stay flat until triaged → Move to 01-inbox/  OR  delete
```

### How to process

`/triage process-landing` — walks each file interactively. For each file the options are Promote (move to `01-inbox/`), Delete, Skip, or Stop. (The skill is the only channel allowed to move or delete files here.)

### File examples

- `7-questions-for-sam.md`
- `employment-study.md`

---

## 01-inbox

**Path:** `~/helm/01-inbox/`
**CLAUDE.md:** `~/helm/01-inbox/CLAUDE.md`
**Purpose:** Items John has promoted from `00-landing/` because they deserve effort. Rai researches each item on request.

### Rules

- Strict flat. No subfolders.
- One concept per file. Filename is the topic.
- Writers: John (file moves from landing), Claude (research, via the `/triage process-inbox` skill only).
- No autonomous enrichment. Rai never enriches an inbox item without being asked.

### Lifecycle

1. John manually moves a file from `00-landing/` to `01-inbox/`.
2. `/triage process-inbox` is invoked.
3. Rai applies the research template in place. Step 0 reads three identity files: `02-ana/identity/goals.md`, `who-i-am.md`, and `vision.md`.
4. The enriched file is moved to its destination.

### Research template (applied by Rai)

```markdown
## What is it
[1-2 sentences]

## Why I should care
[Tie to identity/goals from 02-ana/identity/]

## Why it matters
[Urgency, leverage, uniqueness]

## Rating
A | B | C | D — relevance to John

## Suggested destination
[07-reading | 06-learning | 10-knowledge | 09-ideas | 05-projects | 04-work]
```

The rating is relevance to John, not generic importance; anything below D is proposed for deletion.

### Routing table

| Content type | Destination |
|--------------|-------------|
| Reading material (book, article, paper) | `07-reading/` |
| Curriculum / course | `06-learning/` |
| Tool / library / concept | `10-knowledge/` |
| Idea seed | `09-ideas/` (as Seed) |
| Project | `05-projects/kitchen/` |
| Work item | `04-work/{engagement}/` |

---

## 02-ana

**Path:** `~/helm/02-ana/`
**CLAUDE.md:** `~/helm/02-ana/CLAUDE.md`
**Purpose:** Everything about John lives here: identity, family, health, finances, admin, travel, journal, todos, quotes, shopping, soul, and a voice-samples writing corpus.

### Auto-load contract

> `02-ana/identity/` is auto-loaded at session start.

Thirteen `.md` files in `identity/` load into every session. Adding a file to `identity/` adds it to context. Removing a file removes it. Non-`.md` files in `identity/` are NOT auto-loaded.

### Subfolder map

| Subfolder | Contents | Auto-loaded |
|-----------|----------|-------------|
| `identity/` | Self-model + reference (13 files) | Yes |
| `soul/` | Reflective writing (own CLAUDE.md) | No |
| `journal/` | Daily journal entries (managed by `/routine journal`) | No |
| `todos/` | `today-plans/` and `tomorrow-plans/` (managed by `/routine today-prep`, `/routine tomorrow-prep`) | No |
| `quotes/` | Captured quotes (managed by `/life quote`) | No |
| `family/` | People closest to John | No |
| `health/` | Overview, medications, recovery, specialists, supplements, quit-tracker | No |
| `financial/` | Assets, budget, bills, subscriptions, debt-plan, `investment/` | No |
| `admin/` | Documents, maintenance | No |
| `travel/` | Trips, bookings | No |
| `shopping/` | Lists and reminders | No |
| `voice-samples/` | Arabic writing corpus (NEW) — feeds `/writing/arabic` | No |

`voice-samples/arabic/` holds `CORPUS.md` plus `formal--*.md` reference pieces (Lumen, columnist-a, columnist-d, columnist-b, columnist-c) used as voice anchors.

`financial/investment/` is the home of the values-based paper-trading practice operated by the `/investment` skill — strategy, branches, the cloud paper-run config, and the advisory-council framework all live there.

### identity/ files (auto-loaded, 13)

| File | Contents |
|------|----------|
| `who-i-am.md` | Self-definition |
| `goals.md` | Current goals (read by inbox triage and weekly planner) |
| `vision.md` | Long-term vision |
| `mindset.md` | Values and mindset |
| `story.md` | Personal narrative |
| `wrong.md` | Things John believes are commonly misunderstood |
| `projects.md` | Active and committed projects |
| `ideas.md` | Top-ideas shortlist (graduated, committed-to-pursuit) |
| `contacts.md` | Key relationships |
| `definitions.md` | Domain-specific definitions |
| `environment.md` | Living and work environment |
| `tech-stack.md` | Tools and technologies |
| `rai-public.md` | Public-facing persona for `johndoe.dev` (NEW) |

### Rules (verbatim)

- Write in English. Never Arabic.
- One source of truth per fact — update in place, do not duplicate.
- Before creating a new file, check if it fits in an existing one.

### Cross-references

- `/triage process-inbox` reads `02-ana/identity/{goals,who-i-am,vision}.md` during research.
- `/work weekly-planner` reads `02-ana/identity/goals.md`.
- `/life` (telos, quote) and `/routine` (journal, today/tomorrow-prep, weekly-retro, monthly bills) skill groups read/write everything in this folder.
- `/investment` reads/writes `02-ana/financial/investment/`.

Full personal-OS chapter: [13-personal-os.md](./13-personal-os.md).

---

## 03-rai

**Path:** `~/helm/03-rai/`
**CLAUDE.md:** `~/helm/03-rai/CLAUDE.md`
**ARCHITECTURE.md:** `~/helm/03-rai/ARCHITECTURE.md`
**SYNC-ARCHITECTURE.md:** `~/helm/03-rai/SYNC-ARCHITECTURE.md`
**Purpose:** Rai's brain. Skills, agents, algorithm, hooks, memory, semantic-memory, identity, config.

### Auto-load contract

> `03-rai/identity/` is auto-loaded at session start.

Four `.md` files plus one YAML (not auto-loaded but read at runtime by hooks).

### Subfolder map

| Subfolder | Contents |
|-----------|----------|
| `identity/` | Rai config (4 .md files: `ai-steering-rules.md`, `coding-format.md`, `dai-identity.md`, `response-format.md`) + `security-patterns.yaml` (not auto-loaded) |
| `algorithm/` | v3.7.0 spec + `latest` pointer |
| `config/` | `settings.json`, `mcp.json`, `.skill-lock.json`, `statusline.sh` |
| `memory/` | `learning/`, `relationship/`, `security/`, `state/`, `work/` (+ `ai-calls/` external-LLM telemetry) |
| `semantic-memory/` | `chromadb/` vector store + `pending/` queue + scripts |
| `hooks/` | 19 .py hooks + `lib/` + `scripts/` |
| `skills/` | 35 routers/leaves + `MANIFEST.md` + `GAPS.md` (= 37 entries) |
| `agents/` | 10 agent .md files + `MANIFEST.md` (= 11 files) |

### Critical files

- `algorithm/v3.7.0.md` — canonical algorithm spec
- `SYNC-ARCHITECTURE.md` — authoritative Mac↔Ubuntu single-coordinator sync contract (NEW)
- `skills/MANIFEST.md` — skill grouping ownership map
- `skills/GAPS.md` — open backlog and tombstones
- `agents/MANIFEST.md` — agent tier spec
- `.pai-protected.json` — secret redaction patterns (388 lines of regex)
- `identity/security-patterns.yaml` — security validator runtime patterns
- `config/settings.json` — Claude Code harness contract (hooks wired here, reached via the symlink `~/.claude/settings.json`)

### Skills (35 top-level entries)

31 routers + 4 leaves (`ask-model`, `map-updater`, `project-init`, `workflow`), with ~134 sub-skill files beneath the routers. Routers new since 2026-04-22: `writing`, `ask-model`, `investment`, `ubuntu`. (The old manual's "22 routers/leaves" count is stale.)

### Algorithm — v3.7.0

Phases: OBSERVE → THINK → PLAN → BUILD → EXECUTE → VERIFY → LEARN (the hook-level state machine bookends these with IDLE and COMPLETE). Five effort tiers: Standard / Extended / Advanced / Deep / Comprehensive. PRDs land at `memory/work/{slug}/PRD.md`.

Full Rai architecture: [02-architecture.md](./02-architecture.md).
Skills catalog: [07-skills-catalog.md](./07-skills-catalog.md).
Agents catalog: [08-agents-catalog.md](./08-agents-catalog.md).
Hooks reference: [09-hooks-reference.md](./09-hooks-reference.md).
Memory systems: [10-memory-systems.md](./10-memory-systems.md).
Config, security, and sync: [17-config-and-security.md](./17-config-and-security.md).

---

## 04-work

**Path:** `~/helm/04-work/`
**CLAUDE.md:** `~/helm/04-work/CLAUDE.md`
**Purpose:** Daily-job artifacts: projects, meetings, tasks, proposals, diagrams. Anything tied to a paid engagement.

### Structure

```
04-work/
├── {engagement}/      One subfolder per engagement (client-alpha/, helios/, tableau/)
└── work-plans/        Weekly plans named by ISO week (2026-W17.md) — documented in CLAUDE.md
```

Current live engagements on disk: `client-alpha/`, `helios/` (NEW — peer to client-alpha, not nested under it), `tableau/`. The `work-plans/` directory is documented in CLAUDE.md and produced by `/work weekly-planner`, but is created on demand and is not currently present on disk.

### Rules

- **Confidentiality first.** Contains client/employer details. Never share externally without explicit authorization.
- **No AI/Claude mentions** in any output that lands here.
- Diagrams: Excalidraw for editable, PDFs for finalized.
- New engagement → new subfolder. Short, obvious name.

### Skills

- `/work weekly-planner` — Monday ritual. Reads last week's plan + `02-ana/identity/goals.md` + open tasks.
- `/work meeting-prep` — Pre-meeting briefing and agenda.

Full work + projects chapter: [14-work-and-projects.md](./14-work-and-projects.md).

---

## 05-projects

**Path:** `~/helm/05-projects/`
**CLAUDE.md:** `~/helm/05-projects/CLAUDE.md`
**Purpose:** Three lifecycle stages for project management.

### Lifecycle

| Stage | Folder | Purpose | Code location |
|-------|--------|---------|---------------|
| Planning | `kitchen/{name}/` | PRDs, architecture, design. No code yet. | None; inside helm |
| Active | `active/{name}/` | Non-code artifacts (design iterations, decisions, research, meeting notes) | Code in `~/projects/{name}/` (outside helm) |
| Completed | `completed/{name}/` | Retrospective + diagrams | N/A |

Current contents: `kitchen/` holds `cloud-lab/` and `open-kit/`; `completed/` holds 8 retrospectives (`cortex/`, `data-lakehouse/`, `data-orchestrator/`, `dsc-self-service-platform/`, `helios/`, `niic-data-platform/`, `Globex-tark/`, `national-census/`); plus `projects-moc.md` at root. The `active/` directory does NOT currently exist — it is created on demand when a project goes active.

### Naming

Lowercase with dashes: `my-project-name`. Short, descriptive, no spaces.

### Lifecycle flow

1. Idea graduates from `09-ideas/` (Tree → Graduated).
2. Create `kitchen/{name}/` and iterate: PRD, architecture, design.
3. When ready: create `~/projects/{name}/` (outside helm), move planning docs alongside the code, create `active/{name}/` for ongoing non-code work.
4. When done: create `completed/{name}/` with retrospective + diagrams. Remove the active folder.

### Rules

- No auto-generated `Brief.md`, `Kanban.md`, or master board. Those patterns are retired.
- One inventory file at root: `projects-moc.md`.

### Cross-references

- Receives ideas from `09-ideas/` via `/ideas graduate`.
- Code lives separately in `~/projects/`.

Full work + projects chapter: [14-work-and-projects.md](./14-work-and-projects.md).

---

## 06-learning

**Path:** `~/helm/06-learning/`
**CLAUDE.md:** `~/helm/06-learning/CLAUDE.md`
**Purpose:** Courses and tutorials. Full curriculum for self-directed learning.

### Structure

- One folder per topic, kebab-case (e.g. `master-data-path/`, `claude-code-mastery/`).
- Each topic has `progress.md` (required).
- Large curricula allow Phase or Module subfolders:
  - `master-data-path/Phase N - [Name]/Lesson NNN - [Subtopic].md`
  - `claude-code-mastery/Module N - [Name]/Lesson NNN - [Subtopic].md`
- Small topics stay flat: `Lesson NNN - [Subtopic].md`.

### Retirement (NEW rule)

> Retired topics live in `13-archive/learning/` (moved whole, frozen).

The archive path is now part of this folder's contract. Five retired curricula were moved there 2026-06-10 (`adapting-pai`, `claude-code-mastery`, `omarchy`, `opencode-cli`, `personal-ai-infrastructure`).

### progress.md (required per topic)

```yaml
---
type: progress-tracker
created: YYYY-MM-DD
mode: beginner | mid | expert
---

current lesson: ...
last session date: ...
stuck-on: ...

| Lesson | Status |
|--------|--------|
| Lesson 001 - Intro | ✅ done |
| Lesson 002 - Basics | 🔄 in progress |
| Lesson 003 - Next | ⬜ not started |
| Lesson 004 - Other | ⏸️ paused |
```

> **Emoji carve-out:** the four status icons above (`✅ done`, `🔄 in progress`, `⬜ not started`, `⏸️ paused`) are reproduced verbatim from the live `06-learning` `progress.md` convention defined in that folder's `CLAUDE.md`. They are an explicit exception to the manual's "No emojis" rule because they document an on-disk pictographic convention rather than the manual's own prose. The named-token equivalents are **done / in-progress / not-started / paused**. Same treatment as the `06-learning` chapter.

### Skills

| Skill | Purpose |
|-------|---------|
| `/learning start-topic` | Create topic + progress.md |
| `/learning teach` | Generate mode-aware lesson |
| `/learning quiz` | Retrieval practice on recent lessons |
| `/learning audit-coverage` | Verify topic has full coverage before declaring done |

---

## 07-reading

**Path:** `~/helm/07-reading/`
**CLAUDE.md:** `~/helm/07-reading/CLAUDE.md`
**Purpose:** Books read interactively through Claude Code. Complete coverage, not summaries.

Philosophy from CLAUDE.md:

> I don't have time to read books. So I read them through you.

### Structure

- One folder per book or author-curriculum, kebab-case (e.g. `robert-greene-curriculum/`, `thinking-fast-and-slow/`).
- Each curriculum has `progress.md` (required, same schema as `06-learning/`).
- Lessons flat: `Lesson NNN - [Topic].md`.
- Tier organization allowed for multi-book or multi-phase curricula.

### Skills

| Skill | Purpose |
|-------|---------|
| `/reading start-book` | Scaffold curriculum + progress.md + tier plan |
| `/reading teach` | Generate a lesson (Chapter / Law / Practice / Synthesis types) |
| `/reading audit-coverage` | Verify full book coverage before declaring done |

### Rules

> Lesson shapes, pacing, named-framework preservation, stories-sacred, per-chapter treatment standard, quality bar — all live INSIDE the `teach` skill.

The CLAUDE.md is short on purpose; the rules live in the skill.

---

## 08-bawaba

**Path:** `~/helm/08-bawaba/`
**CLAUDE.md:** `~/helm/08-bawaba/CLAUDE.md`
**Purpose:** Personalized news digests generated by the `news-digest` skill (`/news`), now at v5.6.

Sources (6, all mandatory): Hacker News, Reddit, X (For You + Following), Substack, Medium, GitHub Trending.

### Structure (restructured since 2026-04-22)

The flat `YYYY-MM-DD.md` / `YYYY-MM-DD-weekly.md` layout is gone. The folder now has dedicated subfolders:

| Path | Purpose |
|------|---------|
| `daily/YYYY-MM-DD.md` | Daily digests (auto-generated 3am via Ubuntu systemd) |
| `weekly/YYYY-WWW.md` | **Bawaba Weekly** magazine issue, ISO-week named (auto-generated Saturday 7am) |
| `scraping/` | Python scraping toolkit (`.venv/`, per-source collectors, `run_all.py`, `setup.sh`) |
| `.scratch/` | Scratch collectors + JSON dumps (debug artifacts) |
| `story-arcs.md` | Multi-day / multi-week narrative threads |
| `_graduated.md` | Items promoted out of news into `09-ideas/` or `10-knowledge/` (recreated on first graduation) |

The weekly magazine is the most important output of the news system: department-structured (Editor's Letter, Cover Story, Model State, The Lesson, The Stack, The Workshop, Reading Shelf, Closing Wisdom), mined from `13-archive/news/dumps/` and web-enriched. It never opens a browser.

### Rules

- Generated content only. This folder is the output target of the `/news` skill.
- Digests are immutable after creation. Do not retroactively edit.
- Gaps are okay. If a day was skipped, leave the gap. Do not backfill.
- Scratch JSONs are debug artifacts. Safe to delete after a run.
- **NEVER delete `daily/` files** (root CLAUDE.md emphasis after a 2026-06-11 mishap).

### Automation

Scheduled on the Ubuntu box via systemd user timers running headless `claude -p` (`03-rai/skills/news-digest/scheduled/run-news-ubuntu.sh`):
- `news-daily.timer` at 03:00 — drives the local logged-in Chrome.
- `news-weekly.timer` Saturday 07:00 — no browser; runs `weekly_mine.py` over the week's dumps, web-enriches, writes the magazine.

The Mac launchd / WezTerm runner was retired during this migration (kept in-repo as rollback only). Prior digests are archived automatically after each run to `13-archive/news/` (`daily/` + `weekly/` subfolders).

### What Claude should do

- "What's happening" / "/news" / "give me a digest" → invoke `/news` skill.
- User references a past digest by date → read file directly.
- User wants to "promote" a news item → append to `_graduated.md` and move content to `09-ideas/` (Seed) or `10-knowledge/`.

Full news digest chapter: [15-news-digest.md](./15-news-digest.md).

---

## 09-ideas

**Path:** `~/helm/09-ideas/`
**CLAUDE.md:** `~/helm/09-ideas/CLAUDE.md`
**Purpose:** Where ideas grow or die. Pipeline: Seed → Plant → Tree → Graduated.

### Layout

Flat. All idea files at root. Kebab-case filenames. Status tracked in frontmatter.

### Frontmatter

```yaml
---
status: seed | plant | tree | graduated
domain: ai | data | business | personal | ...
derived_from: [[parent-ideas]]
spawned: [[ideas-or-projects]]
created: YYYY-MM-DD
tags: [idea, seed]
---
```

### Templates

| Stage | Template |
|-------|----------|
| Seed | `12-system/templates/Seed.md` |
| Plant | `12-system/templates/Plant.md` |
| Tree | `12-system/templates/Tree.md` |

### Skills

| Skill | Purpose |
|-------|---------|
| `/ideas start-seed` | Create a new Seed |
| `/ideas promote` | Advance to next stage (Seed→Plant→Tree) |
| `/ideas graduate` | Tree → `05-projects/kitchen/{name}/` (scaffolds README + PRD + ARCHITECTURE stub) |
| `/ideas derive` | Find cross-idea connections |

### Retention

> Ideas never die. Graduated ideas stay — they seed future ideas via lineage. No pruning.

### Relationship to identity/ideas.md

- `09-ideas/` is the nursery (all seeds, including rejected or abandoned).
- `02-ana/identity/ideas.md` is the top-ideas shortlist (graduated, committed to pursuit).

Full lifecycle chapter: [05-idea-lifecycle.md](./05-idea-lifecycle.md).

---

## 10-knowledge

**Path:** `~/helm/10-knowledge/`
**CLAUDE.md:** `~/helm/10-knowledge/CLAUDE.md`
**Purpose:** The compounding knowledge base. Where understanding lives long-term. Built around Topic Notes (deep dives) and MOCs (Maps of Content — navigation hubs). Quality over quantity.

### Subfolder structure

| Subfolder | Contents |
|-----------|----------|
| `_mocs/` | Maps of Content (topic hubs, navigation) |
| `data-engineering/` | ETL, warehouses, pipelines, tools |
| `ai/` | LLMs, RAG, embeddings, ML tools |
| `devops/` | CI/CD, containers, infrastructure |
| `system-design/` | Patterns, architecture, decisions |
| `meta/` | Cross-domain, retention, vault-related |

### Note types

| Type | Purpose | Frontmatter |
|------|---------|-------------|
| **Topic Note** | Comprehensive coverage of an entire topic area | `type: topic`, `domain`, `tags`, `tools` |
| **MOC** | Map of Content — topic hub with navigation | (Agent Breadcrumbs section required) |
| **Insight Note** | Emergent connection between two existing notes | `type: insight`, `emerged_from: [[a]], [[b]]` |

Note: on disk every Topic Note uses `type: topic` (not `topic-note`); Insight, Concept, and Tool notes are templated but currently have zero instances — tools fold into Topic Note Toolbox sections.

### Required Topic Note structure

1. Simplicity Theorem (one-sentence "aha")
2. Simplicity Diagram (3-5 line ASCII)
3. Why It Matters
4. Sections (1-8 depending on topic breadth)
5. Toolbox (tools folded in, not separate notes)
6. Connections (wiki-links to other notes)
7. Trade-offs

### Rules

- Wiki-links woven into prose, not footnoted.
- Every note must stand on its own.
- Use templates from `12-system/templates/`. (Note: this folder's CLAUDE.md writes `12-system/Templates/` with a capital T; the folder on disk is lowercase `templates/` — known casing drift.)
- MOC drift is the failure mode.

### Skills

| Skill | Purpose |
|-------|---------|
| `/knowledge new-topic-note` | Scaffold a compliant note |
| `/knowledge insight` | Propose an Insight Note from two existing notes |
| `/knowledge audit-moc` | Check a MOC for drift |
| `/knowledge find-connections` | Scan notes for emergent-insight opportunities |

Full knowledge chapter: [12-knowledge-system.md](./12-knowledge-system.md).

---

## 11-workflows

**Path:** `~/helm/11-workflows/`
**CLAUDE.md:** `~/helm/11-workflows/CLAUDE.md`
**Purpose:** Step-by-step playbooks for recurring work.

> When the user says "let's do a code review" or "ship this" or "run the weekly review," look here for the playbook.

The folder's `README.md` was deleted on 2026-04-22; `CLAUDE.md` is now the sole guidance file.

### The 8 playbooks

| # | File | When to use |
|---|------|-------------|
| 01 | `01-project.md` | Starting a new project |
| 02 | `02-task.md` | Standalone task execution |
| 03 | `03-kitchen.md` | Working on a project in `05-projects/kitchen/` (planning phase) |
| 04 | `04-debugging.md` | Diagnosing a bug or system issue |
| 05 | `05-code-review.md` | Reviewing code (PR or local diff) |
| 06 | `06-shipping.md` | Releasing or deploying |
| 07 | `07-learning-tech.md` | Learning a new technology systematically |
| 08 | `08-weekly-review.md` | Saturday processing and reflection |

### Rules

- Playbooks are stable. Update only when the workflow itself changes, not for one-off variations.
- Each playbook is self-contained. No cross-references that force the reader to chase another playbook.
- Numbered prefix is fixed. When adding a new playbook, give it the next number.

### Workflows vs skills

- **Skills** are routers Claude invokes via `/skill-name`. Programmatic.
- **Workflows** are documented playbooks humans follow. Markdown-based, no invocation.

The folder is structurally frozen since 2026-04-22, but several playbook bodies cite stale skill names (underscore-style, pre-kebab) and stale paths (`projects_kitchen/`, `12-system/Templates/`); the surrounding vault moved underneath them.

Full workflows chapter: [16-workflows.md](./16-workflows.md).

---

## 12-system

**Path:** `~/helm/12-system/`
**CLAUDE.md:** `~/helm/12-system/CLAUDE.md`
**Purpose:** Reusable system components for the vault. Templates for new notes, reference docs (snapshots, manuals), snippets, diagrams, media, translations.

### Subfolders

| Folder | Contents |
|--------|----------|
| `templates/` | 16 template files (15 .md + ISC.json) |
| `references/` | Documentation snapshots, current-state pointers (e.g. `rai-current.md`) |
| `snippets/` | Reusable code snippets |
| `diagrams/` | Diagram source files |
| `media/` | Embedded images, audio, etc. |
| `translations/` | Translation work |
| `manual/` | This manual (you are here) — 22 chapters (00-21) + README |

### Templates inventory

| Template | Purpose | Destination |
|----------|---------|-------------|
| Topic Note | Comprehensive topic coverage | `10-knowledge/` |
| Insight Note | Emergent connections between notes | `10-knowledge/` |
| Concept Note | Focused concept capture | `10-knowledge/` |
| Tool Note | Tool / library / CLI reference | `10-knowledge/` |
| MOC | Map of content (topic hub) | `10-knowledge/_mocs/` |
| Seed | Raw idea capture | `09-ideas/` |
| Plant | Researched idea | `09-ideas/` |
| Tree | Planned idea | `09-ideas/` |
| Capture | Quick inbox items | `01-inbox/` |
| PRD | Product Requirements Document | `05-projects/kitchen/{name}/` or `03-rai/memory/work/{slug}/` |
| Project Retrospective | Completed project reflection (`type: project-retrospective`) | `05-projects/completed/{name}/` |
| Learning | Courses, books, tutorials | `06-learning/` or `07-reading/` |
| Soul Note | Personal writing: beliefs, worldview, reflections | `02-ana/soul/` |
| Quote | Captured quote | `02-ana/quotes/` |
| Personal Chapter | Long-form personal narrative | `02-ana/soul/` |
| ISC.json | Ideal State Criteria template | Used in PRDs |

### Rules

> **Templates are read-only.** Copy via Templater, never modify originals during a normal session.

> **References are snapshots.** When you find drift between a reference doc and reality, update the reference doc — but flag it as "snapshot from {date}".

> **Live source of truth lives in CLAUDE.md files.** When references contradict CLAUDE.md, CLAUDE.md wins.

### Critical rule (verbatim from CLAUDE.md)

> CRITICAL RULE: Always use existing templates. Never invent note structures.

Full templates and conventions chapter: [11-templates-and-conventions.md](./11-templates-and-conventions.md).

---

## 13-archive

**Path:** `~/helm/13-archive/`
**CLAUDE.md:** `~/helm/13-archive/CLAUDE.md`
**Purpose:** Preserves session JSONs forever, plus two John-approved standing exceptions.

### Contents

```
13-archive/
├── historical-sessions/   Session JSONs from /process-sessions drain
├── learning/              5 retired curricula (frozen reference)        [exception]
└── news/                  Prior digests + raw collection dumps          [exception]
    ├── daily/             Archived dailies
    ├── weekly/            Archived weekly magazines
    └── dumps/YYYY-MM-DD/  Full raw collections (~2k items/day)
```

### Rules (verbatim)

> Archive is sessions-only, plus the `learning/` exception. Other content (plans, snapshots, stale docs) gets deleted, not archived.

> Read-only by default. Do not modify archived session JSONs.

> No new content authored here. If something needs to be written, it belongs in a live folder.

### The two standing exceptions

- **`learning/`** — retired learning topics moved here whole at John's explicit request (2026-06-10: `adapting-pai`, `claude-code-mastery`, `omarchy`, `opencode-cli`, `personal-ai-infrastructure`). Frozen reference, not active curricula.
- **`news/`** — prior digests (`daily/`, `weekly/`) moved here automatically by the `/news` skill after each run (exception added 2026-06-10), plus `dumps/YYYY-MM-DD/` — the FULL raw collection dumps of every run (exception added 2026-06-13). Git-tracked, synced Mac↔Ubuntu, NEVER purged.

New exceptions require John's explicit request.

### What Claude should do

- When asked about a past session: treat `historical-sessions/` as authoritative record.
- Never move non-session content into `13-archive` except via the two standing exceptions.
- If user asks to "archive" a note: ask whether they mean delete (default) or keep in live folders with "archived" status.
- Never edit archived session JSONs unless explicitly asked.
- Never purge `news/` or `learning/`.

### Cross-references

- Receives session JSONs from `/rai process-sessions` skill (via the drain step).
- Receives news digests + dumps automatically from `/news` and the scheduled runner.

---

## Dotfiles and special folders

### .helm-index/

**Path:** `~/helm/.helm-index/`
**Maintained by:** `/map-updater` skill.

Contains `helm-index.md` — the central navigation map for the entire vault. Auto-refreshed when the map-updater is invoked. Used by Claude when exploring the vault from cold.

### .codemap/

**Path:** `~/helm/.codemap/`
**Status:** Does NOT exist in the helm vault. Confirmed absent. Created by `/map-updater` only when run inside a code project.

When working in a code repo (e.g. `~/projects/{name}/`), the map-updater also writes a `.codemap/codemap.md` for that project. It is never created in helm.

### .obsidian/

**Path:** `~/helm/.obsidian/`
**Purpose:** Editor configuration for Obsidian (theme, plugins, hotkeys, workspace state).

Not a vault concern. Do not modify in normal sessions. The only file that changes regularly is `workspace.json` (window state), which is fine.

### .claude/

**Path:** `~/helm/.claude/`
**Status:** Untracked directory at vault root. Holds `settings.local.json` — local Claude Code harness overrides specific to this machine. The canonical, synced settings file is `03-rai/config/settings.json`, reached via the symlink `~/.claude/settings.json`.

### .gitignore

**Policy reversed 2026-06-13 (brain-repo policy):** information is NEVER ignored. "Helm is a brain, not a project." Only secrets (`twscrape.db`, `.env`) and machine droppings (`__pycache__/`, `*.pyc`, `.DS_Store`) are ignored. The old patterns (`08-bawaba/` scratch JSONs, `*.png`/`*.jpeg`, `.runs/`, `scheduled/logs/`, `ai-calls/`) were removed.

### .gitattributes

**Path:** `~/helm/.gitattributes`
**Status:** NEW. Single rule: `03-rai/memory/**/*.jsonl merge=union` — append-only memory logs union both sides on merge so sync never drops entries.

---

## Cross-folder dependency map

Strong dependencies (where one folder reads or writes another):

| From | To | Trigger |
|------|----|---------| 
| `01-inbox/` triage | `02-ana/identity/{goals,who-i-am,vision}.md` | Read during research |
| `04-work/` weekly-planner | `02-ana/identity/goals.md` | Read during weekly plan |
| All folders | `12-system/templates/` | Read for note structure |
| `09-ideas/` | `05-projects/kitchen/` | Write on graduate |
| `05-projects/active/` | `~/projects/{name}/` | Code lives outside helm |
| Session start | `02-ana/identity/`, `03-rai/identity/` | Auto-load all .md files |
| `/rai process-sessions` | `13-archive/historical-sessions/` | Drain pending sessions |
| `/news` | `08-bawaba/`, `13-archive/news/` | Write daily/weekly digest + archive prior runs |
| `/investment` | `02-ana/financial/investment/` | Read/write paper-trading state |

Skill orchestration dependencies:

| Skill | Folders touched |
|-------|----------------|
| `/triage process-landing` | `00-landing/` → `01-inbox/` or delete |
| `/triage process-inbox` | `01-inbox/` → 6 destinations |
| `/ideas start-seed` | `09-ideas/` |
| `/ideas promote` | `09-ideas/` (frontmatter status update) |
| `/ideas graduate` | `09-ideas/` → `05-projects/kitchen/` |
| `/ideas derive` | `09-ideas/` (cross-link discovery) |
| `/learning start-topic` | `06-learning/` |
| `/learning teach` | `06-learning/{topic}/` |
| `/reading start-book` | `07-reading/` |
| `/knowledge new-topic-note` | `10-knowledge/{domain}/` |
| `/knowledge audit-moc` | `10-knowledge/_mocs/` |
| `/news` | `08-bawaba/{daily,weekly}/` + `13-archive/news/` |
| `/work weekly-planner` | `04-work/work-plans/` + reads `02-ana/identity/goals.md` |
| `/routine journal` | `02-ana/journal/` |
| `/routine today-prep` | `02-ana/todos/today-plans/` |
| `/routine tomorrow-prep` | `02-ana/todos/tomorrow-plans/` |
| `/routine weekly-retro` | `02-ana/journal/` + writes summary |
| `/routine bills` | `02-ana/financial/{bills,subscriptions}.md` |
| `/life quote` | `02-ana/quotes/` |
| `/life telos` | `02-ana/identity/{goals,vision,mindset,who-i-am}.md` |
| `/investment` | `02-ana/financial/investment/` |
| `/rai sanity` | All of `03-rai/` (healthcheck) |
| `/rai process-sessions` | `03-rai/semantic-memory/pending/` → `chromadb/` + `13-archive/` |
| `/recall history` | `03-rai/semantic-memory/chromadb/` (read) |
| `/map-updater` | `.helm-index/helm-index.md` (write) |

---

## File-naming conventions per folder

| Folder | Naming | Frontmatter |
|--------|--------|-------------|
| `00-landing/` | Any descriptive name | Optional |
| `01-inbox/` | One concept per file, filename is topic | Optional |
| `02-ana/` | Subfolder-specific | Varies; identity/*.md plain |
| `03-rai/` | Category-based (skills/, memory/, agents/) | Frontmatter required for skills/agents |
| `04-work/` | ISO week dates, engagement names | Optional |
| `05-projects/` | Kebab-case project names | Optional; PRD has full schema |
| `06-learning/` | Kebab-case topics, `Lesson NNN - [Subtopic].md` | `type: progress-tracker` for progress.md |
| `07-reading/` | Kebab-case books, `Lesson NNN - [Topic].md` | `type: progress-tracker` for progress.md |
| `08-bawaba/` | `daily/YYYY-MM-DD.md`, `weekly/YYYY-WWW.md` | Generated; minimal |
| `09-ideas/` | Kebab-case idea names | `status`, `domain`, `derived_from`, `spawned` |
| `10-knowledge/` | Descriptive topic names; MOC files in `_mocs/` | `type: topic\|insight`, `domain`, `tags` |
| `11-workflows/` | `NN-workflow-name.md` | None (playbooks) |
| `12-system/` | Category-based | Varies by type |
| `13-archive/` | JSON session files (auto-generated); `news/`, `learning/` keep source names | N/A |

---

## What goes where (summary)

| Type of content | Folder | Entry | Exit |
|-----------------|--------|-------|------|
| Raw thoughts | `00-landing/` | Manual drop | Promote to inbox or delete |
| Research item | `01-inbox/` | From landing | To destination |
| Personal data | `02-ana/` | Manual or `/life` / `/routine` / `/investment` | Kept indefinitely |
| Rai config | `03-rai/` | Manual or hooks | Auto-loaded daily |
| Work artifacts | `04-work/` | Manual or `/work` | Historical (git log) |
| Project planning | `05-projects/kitchen/` | From ideas | Move to active or code |
| Active projects | `05-projects/active/` | Project starts | Move to completed |
| Learning curriculum | `06-learning/` | `/learning` | Completion (retire to `13-archive/learning/`) |
| Reading curriculum | `07-reading/` | `/reading` | Completion |
| News digest | `08-bawaba/` | `/news` | Promote to ideas/knowledge; prior runs → `13-archive/news/` |
| Raw ideas | `09-ideas/` | `/ideas start-seed` | Graduate or stay as reference |
| Topic knowledge | `10-knowledge/` | `/knowledge` | Permanent (compounding) |
| Repeatable playbooks | `11-workflows/` | Manual | Updated as workflows evolve |
| Templates and references | `12-system/` | Manual | Never modified (infrastructure) |
| Session records | `13-archive/` | `/rai process-sessions` | Read-only forever |
