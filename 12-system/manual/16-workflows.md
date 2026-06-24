# 16 — Workflows

`11-workflows/` — eight numbered playbooks for recurring work. Different from skills.

Last updated: 2026-06-14.

The live source of truth for this folder is `~/helm/11-workflows/CLAUDE.md`. The folder's `README.md` was deleted on 2026-04-22 (commit `abc1234`, "drop redundant README.md") — one structural-guidance file per folder, and `CLAUDE.md` is it. If an older version of this chapter referenced a `11-workflows/README.md`, that file no longer exists.

## Purpose

From `~/helm/11-workflows/CLAUDE.md`:

> Step-by-step playbooks for recurring work. When the user says "let's do a code review" or "ship this" or "run the weekly review," look here for the playbook.

The root `~/helm/CLAUDE.md` lists this folder as "Repeatable playbooks (independent from skills)." That independence is the whole point: a playbook is read and followed; a skill is invoked and executes.

## The 8 playbooks

The folder holds exactly 9 files: 8 numbered playbooks (`01`–`08`) plus `CLAUDE.md`. No subfolders, no README. The playbook set, numbers, names, and ordering are unchanged and current.

| # | File | When to use |
|---|------|-------------|
| 01 | `01-project.md` | Starting a new project (full lifecycle, spark to ship) |
| 02 | `02-task.md` | Standalone task execution (one feature, fix, or spike) |
| 03 | `03-kitchen.md` | Working on a project in `05-projects/kitchen/` (planning phase) |
| 04 | `04-debugging.md` | Diagnosing a bug or system issue |
| 05 | `05-code-review.md` | Reviewing code (PR or local diff) |
| 06 | `06-shipping.md` | Releasing or deploying |
| 07 | `07-learning-tech.md` | Learning a new technology systematically |
| 08 | `08-weekly-review.md` | Saturday processing and reflection |

The folder is structurally frozen — zero commits have touched `11-workflows/` since the 2026-04-22 README-drop. The last content commit before that was the brain-to-helm rename and folder renumber (`abc1234`, 2026-04-21).

## Known drift — playbook bodies vs current vault

This is the most important thing to know before following any playbook. The folder did not change, but the rest of the vault moved underneath it: skills were renamed to kebab-case and grouped under router skills, folders were renumbered, and the templates directory was lowercased. The playbook bodies were never updated to match. Several skill names and paths they cite are now stale.

`CLAUDE.md`'s own rule applies here: "If a playbook gets out of sync with reality (a step references a deleted skill or moved path), flag it and propose an update." Until a cleanup pass lands, translate as you read.

### Stale skill names (underscore/flat → kebab-case router sub-skills)

| Playbook reference (stale) | Current reality |
|----------------------------|-----------------|
| `/project_init` | `project-init` (kebab; a top-level leaf skill) |
| `/solution_architect` | `/architecture` → `solution-architect` |
| `/data_architect` | `/architecture` → `data-architect` |
| `/tdd` | `/testing` → `tdd` |
| `/e2e` | `/testing` → `e2e` |
| `/refactor-clean` | `/git` → `refactor-clean` |
| `/explain-simply` | `/think` → `explain-simply` |
| `/security-review` | `security-review` (built-in CLI command/skill — verify routing) |
| `/commit` | `/git` → `commit` |
| `/docker` | `/devops` → `docker` |
| `/process-sessions` | `/rai` → `process-sessions` |
| `/news review` | `news-digest` skill (v5.6); the "review" wording maps to the graduated-gems review step |

None of the underscore/flat names the playbooks cite exist at the top level anymore. The skills catalog is router-based now — 35 top-level entries (30 routers + 5 leaves). See [07-skills-catalog.md](./07-skills-catalog.md).

### Stale paths

| Playbook reference (stale) | Current reality |
|----------------------------|-----------------|
| `projects_kitchen/`, `05-projects/projects_kitchen/` | `05-projects/kitchen/` (currently holds `cloud-lab/`, `open-kit/`) |
| `05-projects/active/Projects.md` | `05-projects/active/` does not currently exist; the master index is `05-projects/projects-moc.md` |
| `12-system/Templates/Learning.md` (capital T) | Lowercase `12-system/templates/Learning.md` |
| `.codemap/codemap.md` (used for vault-index updates) | The vault index is `.helm-index/helm-index.md` (refreshed by `/map-updater`). `.codemap/codemap.md` is the per-code-project map and does not exist in the vault. The playbooks conflate the two. |

Note that `CLAUDE.md`'s own internal "Current playbooks" table still carries the stale `projects_kitchen/` path on row 03 — the per-folder governance file has the same drift as the bodies.

## Workflows vs skills

This is the most common confusion. Both live in the brain. Both describe how to do something. But they are different.

| | Workflow | Skill |
|---|----------|-------|
| Where it lives | `11-workflows/` | `03-rai/skills/` |
| Format | Markdown playbook | Skill folder with SKILL.md |
| Invocation | Read by humans (or by Rai when referenced) | `Skill("name")` or `/name` |
| Style | Step-by-step prose | Programmatic with named steps |
| Tools | None inherent | Has access to all tools |
| Audience | Human reads and follows | Claude executes |
| Examples | "Saturday weekly review", "Ship a release" | `/news-digest`, `/triage process-inbox`, `/git commit` |

A workflow is a recipe. A skill is a tool. Some skills implement parts of workflows (e.g., `/work weekly-planner` is invoked from `08-weekly-review.md`). The playbook is prose and checkboxes; the skill it references is the executable part.

## Rules (verbatim from CLAUDE.md)

> Playbooks are stable. Update only when the workflow itself changes, not for one-off variations.

> Each playbook is self-contained. No cross-references that force the reader to chase another playbook to understand this one.

> Numbered prefix is fixed. When adding a new playbook, give it the next number.

### Why stable

If playbooks change every time, they are not playbooks — they are notes. The point is that you can read `06-shipping.md` and it will be the same shape as it was last month. Predictability is the value.

### Why self-contained

A playbook should run end-to-end without forcing the reader to open another playbook mid-flow. References to skills are fine (`Run /git commit at this point`). References to other playbooks are not — copy the relevant content if needed. (In practice the playbooks do use `[[wiki-link]]` cross-references between each other, e.g., `01-project.md` delegating the kitchen phase to `[[03-kitchen]]`; the self-contained rule is the aspiration, not perfectly enforced.)

### Why numbered prefix

The numbering imposes order. New playbooks go at the end. Reordering is rare. The numbers are also part of the file name, so `ls` shows them in order.

## What each playbook covers

Each playbook opens with a one-line purpose, a single-line ASCII pipeline arrow, then `## Steps` with decision-point blockquotes, then a `## Connections` section of wiki-links. Several carry an auxiliary table (Common Traps, Review Mindset, Time Limits, Cadence). The step lists below describe the current intent; where a step cites a stale skill or path, apply the translation tables above.

### 01-project.md — Starting a new project

Full lifecycle from first spark to shipped product.

Pipeline: `Idea → Kitchen → Architecture → Init → Build (phases) → Ship → Retro`

Typical phases:
1. Crystallize the idea (Seed → Plant → Tree → Graduate in `09-ideas/`).
2. Kitchen (planning) — delegates to `03-kitchen.md`; write PRD + SPEC.
3. Architecture review — run `/architecture solution-architect` and `/architecture data-architect`.
4. Project setup — create `~/projects/{name}/`, move planning docs out of `05-projects/kitchen/{name}/`, run `project-init`, add to `05-projects/projects-moc.md`, initial `/git commit`.
5. Build in phases — 3–7 phases, each task via `02-task.md`, a git worktree per phase, `/testing e2e` after each merge.
6. Ship — `06-shipping.md`.
7. Retrospective — write to `05-projects/completed/{name}/`, refresh the vault index with `/map-updater`, `/git commit`.

### 02-task.md — Standalone task execution

A single unit of work (feature, fix, or spike) using git worktrees. The smallest playbook.

Pipeline: `Worktree → Goal → Done criteria → TDD → Verify → Review → Merge → Clean`

Typical steps:
1. Setup — create a git worktree for the task.
2. Define — state the Goal and the Done criteria.
3. Build — TDD via `/testing tdd` (RED-GREEN-REFACTOR).
4. Verify — unit tests, `/testing e2e`, `security-review`.
5. Review — `05-code-review.md`, full diff, `/git refactor-clean`.
6. Merge — `/git commit`, merge to main, `git worktree remove`, delete branch.

Whether a task warrants the Algorithm is a per-task call: non-trivial work enters the 7-phase loop (OBSERVE → THINK → PLAN → BUILD → EXECUTE → VERIFY → LEARN); trivial work skips it. See [06-algorithm-and-prd.md](./06-algorithm-and-prd.md).

### 03-kitchen.md — Working in kitchen phase

The gap between a graduated idea and writing code — plan thoroughly so building is fast.

Pipeline: `PRD → SPEC → Iterate → Zero open questions → Exit kitchen`

Typical steps:
1. Entry — create `05-projects/kitchen/{name}/` with a README.
2. PRD — problem, scope, success metrics, user stories, constraints.
3. SPEC — architecture, components, data models, tech stack, APIs, security; run `/architecture solution-architect` and `/architecture data-architect`.
4. Iterate — read PRD and SPEC back-to-back, resolve open questions.
5. Exit kitchen — create `~/projects/{name}/`, run `project-init`, continue to `01-project.md` phase 5.

Carries a "Kitchen Contents" ASCII tree (`README.md / PRD.md / SPEC.md / ARCHITECTURE.md (optional) / TASKS.md (optional)`). The current kitchen holds `cloud-lab/` and `open-kit/`.

### 04-debugging.md — Diagnosing a bug

Systematic diagnosis and fix. Resist changing random things.

Pipeline: `Symptom → Reproduce → Isolate → Diagnose → Fix → Verify → Document`

Typical steps:
1. Describe the symptom.
2. Reproduce — capture exact reproduction steps.
3. Isolate — narrow the surface; bisect which change introduced this (`git bisect` or manual).
4. Diagnose — confirm the cause with a minimal reproduction.
5. Fix — write the regression test FIRST, then fix.
6. Verify — `/testing e2e`.
7. Document — `/git commit`.

Auxiliary table "Common Traps" (5 rows): changing random things, fixing symptom not cause, fix too large, no regression test, not checking recent changes.

### 05-code-review.md — Reviewing code

Self-review gate before merging. Every merge passes this checklist.

Pipeline: `Diff → Architecture → Logic → Security → Tests → Clean → Merge`

Typical steps:
1. Read the full diff.
2. Architecture check.
3. Logic check.
4. Security check — `security-review`.
5. Test check.
6. Clean up — `/git refactor-clean`.
7. Merge.

The deeper review work routes to `/testing code-review` or the `reviewer` agent (`Task(subagent_type: "reviewer")`, an opus agent — see [08-agents-catalog.md](./08-agents-catalog.md)). Auxiliary table "Review Mindset" (4 self-questions).

### 06-shipping.md — Releasing/deploying

From "works locally" to deployed and verified in production.

Pipeline: `Checklist → Build → Containerize → Deploy → Verify → Tag → Rollback plan`

Typical steps:
1. Pre-ship checklist — tests pass, security review done.
2. Clean build.
3. Containerize — `/devops docker`.
4. Deploy — decision tree (rolling / blue-green / canary).
5. Post-deploy verification — `/testing e2e`.
6. Tag release — `git tag`, `git push --tags`.
7. Rollback plan — documented BEFORE deploy.

If this completes a project: move to `05-projects/completed/{name}/` and write a retrospective; update `02-ana/identity/projects.md` if status changed.

### 07-learning-tech.md — Learning a new technology

Evaluate before committing; prove value fast or move on.

Pipeline: `Discover → Evaluate (30 min) → Spike (2-4 hrs) → Decide → Learn deep → Integrate`

Typical steps:
1. Discover.
2. Evaluate — 30 min max.
3. Spike — 2–4 hrs max, throwaway project.
4. Decision — write a decision record.
5. Learn deep — scaffold a curriculum in `06-learning/{topic}/` (`/learning start-topic`, then `/learning teach`, `/learning quiz`, `/learning audit-coverage`), Learning template from `12-system/templates/Learning.md`, `/think explain-simply`.
6. Integrate — apply via `02-task.md`, consolidate into a Topic Note in `10-knowledge/`.

Auxiliary table "Time Limits" (Evaluate 30 min / Spike 4 hrs / Decide 15 min).

### 08-weekly-review.md — Saturday review

The weekly processing ritual — process the week, maintain the vault, plan next week. The largest playbook.

Pipeline: `Sessions → Inbox → Graduated Gems → Projects → Ideas → Vault → Plan → Commit`

Typical steps:
1. Process sessions — `/rai process-sessions` (drains the pending queue into ChromaDB; runs only on the Linux coordinator, see below).
2. Process inbox — route `00-landing/` then `01-inbox/` via `/triage process-landing` and `/triage process-inbox`.
3. Review graduated gems — `news-digest` review; Archive / Promote / Keep. (Step added 2026-04-13, which renumbered the old steps 3–7 to 4–8.)
4. Review active projects — via `05-projects/projects-moc.md` (the playbook still cites `05-projects/active/Projects.md`, which no longer exists).
5. Review the ideas pipeline.
6. Update the vault — notes, MOCs, refresh the index with `/map-updater` (the playbook still cites `.codemap/codemap.md`).
7. Plan next week — ONE priority; `/work weekly-planner`. (Note: `04-work/work-plans/` is referenced by the skill but does not currently exist on disk.)
8. Commit — `/git commit`.

Auxiliary table "Cadence" (Weekly Saturday / Daily optional / Monthly). Also relevant to the weekly rhythm: `/routine weekly-retro` for personal reflection.

A real caveat on step 1: ChromaDB is single-writer. The drain into the vector store happens only on the Linux coordinator ("pc"), which runs `/process-sessions` at 04/10/16/22:00. The Mac is a passive replica. See [03-rai/SYNC-ARCHITECTURE.md](../../03-rai/SYNC-ARCHITECTURE.md) and the memory chapter for the full model.

---

## What Claude should do

From `~/helm/11-workflows/CLAUDE.md`:

1. When the user invokes a workflow by name: read the playbook, follow it step by step.
2. If a step needs adapting to the current context: propose the adaptation rather than silently skipping.
3. When the user is mid-work and the situation matches a playbook: suggest it by name. Do not auto-invoke without confirmation.
4. If a playbook is out of sync (references a deleted skill or moved path): flag it and propose an update. (As documented above, this is currently true of every playbook — they predate the kebab-case router migration and the folder renumber.)

## Adding a new workflow

1. Confirm the workflow is genuinely repeatable. A one-off is not a playbook.
2. Confirm no existing playbook covers it.
3. Create `11-workflows/NN-name.md` with the next available number.
4. Write the playbook self-contained (no forced cross-references to other playbooks).
5. Update `11-workflows/CLAUDE.md` to add the entry to the inventory.
6. Update this manual chapter.

Adding workflows is rare. The 8 cover most recurring work.

## Removing a workflow

If a playbook is no longer used, delete it. Update the CLAUDE.md inventory. Per the vault rule, do not archive — git log preserves the history.

The numbered prefix means deleting `04-debugging.md` would leave a gap (no 04). That is fine. Do not renumber surviving playbooks. The numbers are stable, even with gaps.

## Cross-references to other manual chapters

- Skills (the tools workflows invoke, now router-based): [07-skills-catalog.md](./07-skills-catalog.md)
- Agents (e.g., the `reviewer` agent for `05-code-review.md`): [08-agents-catalog.md](./08-agents-catalog.md)
- Algorithm (when a workflow involves it): [06-algorithm-and-prd.md](./06-algorithm-and-prd.md)
- Project lifecycle (what `01-project.md`, `03-kitchen.md`, `06-shipping.md` operate on): [14-work-and-projects.md](./14-work-and-projects.md)
- Capture pipeline (used in `08-weekly-review.md`): [04-capture-pipeline.md](./04-capture-pipeline.md)

## When to read which playbook

| Situation | Playbook |
|-----------|----------|
| "I want to start working on this idea" | 01-project.md |
| "I have one specific task to do" | 02-task.md |
| "I'm planning a project, no code yet" | 03-kitchen.md |
| "Something is broken, I need to find why" | 04-debugging.md |
| "Review this PR" | 05-code-review.md |
| "Ship this release" | 06-shipping.md |
| "I want to learn X" | 07-learning-tech.md |
| "It's Saturday, time for the review" | 08-weekly-review.md |

## When to NOT use a playbook

- The work is genuinely novel (not recurring).
- The work is small enough to skip the playbook overhead.
- The playbook is out of date and needs updating before use (currently relevant — translate stale skill/path references as you go).
- A skill covers the entire workflow more directly.

## The relationship between playbooks and the Algorithm

A playbook is a high-level sequence. The Algorithm (v3.7.0) is a per-task framework. Some playbook steps invoke the Algorithm. For example:

- `06-shipping.md` step "deploy per project's deploy procedure" might invoke the Algorithm if the deploy is non-trivial.
- `04-debugging.md` step "fix and verify" almost always invokes the Algorithm for non-trivial bugs.

The playbook is the macro structure. The Algorithm is the micro discipline within complex steps. Trivial steps skip the Algorithm entirely.
