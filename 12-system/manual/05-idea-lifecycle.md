# 05 — Idea Lifecycle

How ideas are born, grown, and shipped. Four states. One folder. Four skills.

> Last updated: 2026-06-14. The idea-lifecycle *mechanism* (folders, skills, templates, rules) is unchanged since the 2026-04-22 manual baseline — no commits touched `03-rai/skills/ideas/*` or `09-ideas/CLAUDE.md` in this window. What changed is the *data* (the live idea inventory) plus a rename/dedup pass and a new kitchen project. This rewrite also corrects several facts the prior chapter got wrong (a fabricated idea listing, an invented running example, and inaccurate `graduate`/`derive` descriptions). The live source of truth is `09-ideas/CLAUDE.md` and the four skill files in `03-rai/skills/ideas/` — when this chapter and those disagree, those win.

## The pipeline

```
                    /ideas start-seed
External thought  ──────────────────▶  09-ideas/{name}.md (status: seed)
                                                  │
                                                  │  /ideas promote
                                                  ▼
                                       09-ideas/{name}.md (status: plant)
                                                  │
                                                  │  /ideas promote
                                                  ▼
                                       09-ideas/{name}.md (status: tree)
                                                  │
                                                  │  /ideas graduate
                                                  ▼
                  ┌──────────────────────────────────────────────────────┐
                  │  09-ideas/{name}.md (status: graduated)               │
                  │                       +                              │
                  │  05-projects/kitchen/{name}/  (README, PRD, ARCH)    │
                  └──────────────────────────────────────────────────────┘
                                                  │
                                                  │  start coding
                                                  ▼
                  ┌──────────────────────────────────────────────────────┐
                  │  ~/projects/{name}/  (code lives outside vault)       │
                  │                       +                              │
                  │  05-projects/active/{name}/  (non-code work)         │
                  └──────────────────────────────────────────────────────┘
                                                  │
                                                  │  ship
                                                  ▼
                  ┌──────────────────────────────────────────────────────┐
                  │  05-projects/completed/{name}/  (retrospective)      │
                  └──────────────────────────────────────────────────────┘
```

The idea pipeline owns the first three states inside `09-ideas/` plus the graduation hand-off into `05-projects/kitchen/`. Everything past graduation is the project lifecycle — see [./14-work-and-projects.md](./14-work-and-projects.md).

## The four states

| State | What it is | Where it lives | Frontmatter |
|-------|------------|----------------|-------------|
| **Seed** | Raw idea, minimal effort to capture | `09-ideas/{name}.md` | `status: seed` |
| **Plant** | Researched, shaped, direction clear | `09-ideas/{name}.md` (same file, frontmatter updated) | `status: plant` |
| **Tree** | Fully planned, requirements + schedule defined | `09-ideas/{name}.md` (same file) | `status: tree` |
| **Graduated** | Tree handed off to `05-projects/kitchen/`, project prep begins | `09-ideas/{name}.md` (frontmatter only) + `05-projects/kitchen/{name}/` | `status: graduated` |

The same file in `09-ideas/` carries the idea through all four states. Only the frontmatter `status` field changes (and the body grows as research deepens). The `promote` skill enforces the order — it refuses to skip a stage.

## Folder layout — 09-ideas

Flat. All ideas at root. Kebab-case names. No subfolders. Status lives in frontmatter, never in folder structure.

### Live inventory (as of 2026-06-14)

There are six idea files at root (plus `CLAUDE.md`):

| File | status | domain (as written) | created | spawned |
|------|--------|---------------------|---------|---------|
| `ai-native-data-solutions.md` | seed | `data-engineering` | 2026-02-02 | `[]` |
| `enterprise-data-solution-reference.md` | seed | `data-engineering` | 2026-02-02 | `[]` |
| `k8s-mlops-platform.md` | tree | `devops, ai` | 2026-01-05 | `[[cloud-lab]]` |
| `dataforge.md` | tree | `data-eng, ai, business` | 2026-01-07 | `[]` |
| `geocontext.md` | tree | `data-eng, ai, business` | 2026-01 | `[]` |
| `open-kit.md` | graduated | `business` | 2026-01-28 | `[[open-kit]]` |

Status distribution: 2 seed, 0 plant, 3 tree, 1 graduated. There are currently no Plant-state ideas — that is normal, not a gap; ideas frequently move Seed → Plant → Tree across one or two working sessions and do not linger in Plant.

Because status is in frontmatter, you find ideas by state with a grep, not by listing folders:

```
grep -l 'status: tree' ~/helm/09-ideas/*.md
```

## Frontmatter schema

The required fields, per `09-ideas/CLAUDE.md`:

```yaml
---
status: seed | plant | tree | graduated
domain: ai | data | business | personal | ...
derived_from: [[parent-idea-1]], [[parent-idea-2]]    # ideas this came from
spawned: [[child-idea-1]], [[graduated-project-1]]    # ideas/projects this created
created: YYYY-MM-DD
---
```

The `12-system/templates/` Seed/Plant/Tree files add two more frontmatter keys — `type: idea` and `tags: [idea, <state>]` — plus stage-specific date markers (`grown:` on Plant and Tree, `ready:` and `scheduled_start:` on Tree). See "Templates summary" below for the exact shapes.

Two reality notes that the schema does not enforce:

- **`domain` is advisory, not an enum.** The CLAUDE.md writes it as `ai | data | business | personal | ...`, but real files use free comma-joined strings: `data-engineering`, `devops, ai`, `data-eng, ai, business`. Treat `domain` as a tag string, not a validated single value.
- **Graduated ideas accrue extra keys.** `open-kit.md` carries non-template keys `grown:` and `graduated:` (a date) on top of `type: idea`. There is no schema police; the lineage fields are what matter.

The wiki-link fields (`derived_from`, `spawned`) form the lineage graph. `/ideas derive` reads them to find connections.

## State 1 — Seed

The cheapest possible capture. A name + a one-line spark.

### Template — Seed.md

Located at `12-system/templates/Seed.md` (a Templater template):

```markdown
---
type: idea
status: seed
domain:
derived_from: []
spawned: []
created: <% tp.date.now("YYYY-MM-DD") %>
tags: [idea, seed]
---

# <% tp.file.title %>

## Spark
> [One sentence - the raw idea]

## What Is It?
[Brief explanation. What problem? What solution? Keep it rough.]

## Trigger
What sparked this? Conversation, article, frustration, observation?
```

### Skill — /ideas start-seed

Creates a new Seed from a name and a spark line. Allowed tools: `Write, AskUserQuestion, Bash`. Capture effort: low.

```
/ideas start-seed "ai native data solutions"
```

This:
1. Gets the spark in one sentence.
2. Classifies domain — single-select `ai | data | business | personal | other`.
3. Proposes a kebab-case slug, confirms or overrides.
4. Writes `09-ideas/{slug}.md` with Spark / What Is It? / Trigger.
5. Reports and points at `/ideas promote {slug}` for when it is time to research.

> The skill writes a **leaner** Seed than the template: it omits `type: idea` and `tags: [idea, seed]`. Two slightly different Seed shapes therefore exist — the skill's inline version and the `12-system/templates/Seed.md` version. The skill is what actually runs when you say `/ideas start-seed`.

### When to create a Seed

- A thought worth capturing but not yet worth thinking about deeply.
- An item from `08-bawaba/` that reads like a project, not just news (provenance noted in `Trigger`).
- A research outcome from `01-inbox/` triage that `process-inbox` routes to `09-ideas/` as a Seed. (`09-ideas/` is one of the six capture-pipeline destinations — see [./04-capture-pipeline.md](./04-capture-pipeline.md).)
- A conversation moment captured fast.

### What a Seed is NOT

- Not a project plan. A project plan is a Tree (or already graduated).
- Not a research note. Research lives in `10-knowledge/` once it has a topic.
- Not a todo. Todos live in `02-ana/todos/`.

## State 2 — Plant

A Seed that has been researched and shaped. Direction is clearer; risks are surfaced; questions are answered.

### Template — Plant.md

Located at `12-system/templates/Plant.md`. Adds `grown:` to the frontmatter and these body sections:

```markdown
---
type: idea
status: plant
domain:
derived_from: []
spawned: []
created: <% tp.date.now("YYYY-MM-DD") %>
grown: <% tp.date.now("YYYY-MM-DD") %>
tags: [idea, plant]
---

# {Name}

## Spark
> [Refined one-sentence core insight]

## Problem
Who has this problem? How painful is it? How do they solve it today?

## Insight
The deeper aha moment. Why does this matter? What's the unique angle?

## Vault Connections
How does this connect to your knowledge, projects, and experience?

## Market Landscape
What exists? Who's doing this? What's missing?

## Dialogue Summary
Key clarifications from Q&A.

## Potential
What could this become? Product? Tool? Business? Side project?

## Open Questions
What still needs answering before this becomes a Tree?
```

### Skill — /ideas promote (Seed → Plant)

Promotes an idea to the next state. Reads current `status:`, determines the next state, runs the right process, rewrites the file. Allowed tools: `Read, Write, Edit, WebSearch, WebFetch, AskUserQuestion, Bash`.

```
/ideas promote ai-native-data-solutions
```

The Seed → Plant process:
1. Re-reads the Seed.
2. Researches the vault — `05-projects/`, `10-knowledge/`, `06-learning/`, `02-ana/identity/`.
3. Runs `AskUserQuestion` clarifying rounds: what problem, who is the target user, the unique angle (why-you-why-now), the riskiest assumptions.
4. Runs `WebSearch` + `WebFetch` for market/competitor context.
5. Rewrites the file as a Plant with the skill's section set — Spark, The Problem, The Idea, Research (What others are doing / What's missing / Internal context), Q&A, Open assumptions, Next steps — and adds `updated:` to the frontmatter.

> The skill's Plant section names differ slightly from the `12-system/templates/Plant.md` headings (e.g. the skill writes "Research / What's missing / Internal context" where the template has "Market Landscape / Vault Connections"). The skill version is what actually gets written; the template is the canonical reference shape. A core rule: the skill **always writes from fresh research, not prior knowledge** (it must use WebSearch), and it **preserves the original Spark verbatim** across every stage.

### When to promote to Plant

- The Seed has sat for a few days and is still interesting.
- Research has surfaced enough context to ask informed questions.
- A short conversation (with someone, or with Rai) has clarified direction.

## State 3 — Tree

A Plant that has been fully planned. Requirements are defined, a schedule is allocated, dependencies and risks are known.

### Template — Tree.md

Located at `12-system/templates/Tree.md`. Adds `grown:`, `ready:`, and `scheduled_start:` to the frontmatter and these body sections:

```markdown
---
type: idea
status: tree
domain:
derived_from: []
spawned: []
created: <% tp.date.now("YYYY-MM-DD") %>
grown:
ready: <% tp.date.now("YYYY-MM-DD") %>
scheduled_start:
tags: [idea, tree]
---

# {Name}

## Spark
> [The crystallized core insight]

## Problem & Solution
**Problem** / **Solution** / **Target User**

## Requirements
What must this have to be viable?

## Plan
High-level roadmap to first milestone (Phase 1 / 2 / 3).

## First Steps
Smallest actions to start.

## Success Criteria
How will you know this worked?

## Schedule
- Start Date / First Milestone / Review Date

## Resources Needed
Time, tools, skills, people?

## Risks
What could go wrong? How to mitigate?
```

### Skill — /ideas promote (Plant → Tree)

Same skill, Plant → Tree branch:
1. Re-reads the Plant.
2. Gathers requirements (must-haves, the first milestone, what "done" means for v1).
3. Names the risks.
4. Sets a schedule.
5. Rewrites as a Tree with sections: Spark/Problem/Idea, Requirements, Plan (Milestone 1/2 + First actions), Schedule (Start / M1 target / v1 target / Review cadence), Risks, and a **Graduation readiness checklist** (Requirements clear / Plan realistic / Risks named / John committed).

`promote` refuses to advance a Tree. When status is already `tree`, it stops and tells you to run `/ideas graduate` instead. When status is `graduated`, there is nothing further to do.

### When to promote to Tree

- The Plant has been validated. The riskiest assumptions have been pressure-tested.
- John is ready to commit some real time.
- The schedule fits the near-term planning horizon.

## State 4 — Graduated

The Tree has earned a project. It moves into `05-projects/kitchen/{name}/`. The idea file stays in `09-ideas/` — graduation copies the idea's substance into a new project folder; it never deletes or relocates the idea.

### Skill — /ideas graduate

Allowed tools: `Read, Write, Bash, AskUserQuestion`.

```
/ideas graduate k8s-mlops-platform
```

This:
1. Reads `09-ideas/{slug}.md` and **verifies `status: tree`**. If it is not a Tree, it stops and tells John to `/ideas promote` it first.
2. Confirms the project folder name (default = the idea slug; may differ if the name has been refined).
3. Collision-checks `05-projects/kitchen/{project-name}/` — if it already exists, it stops and asks whether to overwrite, merge, or rename.
4. `mkdir -p ~/helm/05-projects/kitchen/{project-name}`.
5. Scaffolds **three docs** from the Tree content, using its own inline templates:
   - `README.md` — Spark + Problem + Idea condensed, a "Kitchen phase — planning" status line, and a `Related: [[09-ideas/{slug}]]` back-link.
   - `PRD.md` — Problem / Goals / Non-goals / Users-stakeholders / Success criteria / Open questions.
   - `ARCHITECTURE.md` — a stub, to be filled during kitchen iteration.
6. Updates the idea frontmatter to `status: graduated` and adds `spawned: [[05-projects/kitchen/{project-name}]]`.
7. Reports.

> Correction to the prior chapter: graduate does **not** "write an initial PRD using the `12-system/templates/PRD.md` template." It scaffolds **three** files (`README.md`, `PRD.md`, `ARCHITECTURE.md` stub) from its **own inline templates**. The skill's inline PRD shape (Problem / Goals / Non-goals / Users / Success criteria / Open questions) is deliberately rougher than the formal `12-system/templates/PRD.md` (which carries an ISC table, Anti-Criteria, Phases, a Decisions table, and a Log). The kitchen PRD gets refined in the kitchen, not at graduation.

### What lives in 05-projects/kitchen/{name}/ at graduation time

Exactly what the skill scaffolds — three files:

```
kitchen/{name}/
├── README.md          ← condensed spark/problem/idea + status + idea back-link
├── PRD.md             ← rough: problem, goals, non-goals, users, success, open Qs
└── ARCHITECTURE.md    ← stub, filled later
```

A kitchen folder grows from there as a project matures, but that growth is hand-driven project work, not graduate-skill output. The live `open-kit` kitchen folder is the richest example: 24 files including `SPEC.md`, `PROPOSAL.md`, `BRAINSTORM.md`, bilingual MEMOs, two PDFs, and 12 diagrams under `docs/diagrams/`. None of that was generated by `graduate` — it accumulated as John developed the project. See [./14-work-and-projects.md](./14-work-and-projects.md) for the full kitchen state.

### Why "graduated" instead of just "promoted"

Promotion within `09-ideas/` is cheap. Graduation is significant: it changes folders, scaffolds a project structure, and commits real time. That is why it is a separate skill with its own confirmation and collision checks, and why `promote` deliberately stops at Tree.

## Lineage tracking

Two frontmatter fields form the idea graph:

- `derived_from:` — what this idea came from (parent ideas).
- `spawned:` — what this idea created (child ideas, graduated projects).

Both are wiki-link arrays. They are bidirectional by convention: when you graduate idea A and it spawns project B, you write `spawned: [[B]]` in A's frontmatter and `derived_from: [[A]]` on B's side. The `derive` skill enforces this — it updates both sides of every new link.

Two live examples:

- `k8s-mlops-platform.md` (a Tree) carries `spawned: [[cloud-lab]]`. Its 2026-05-30 update repositions it as "Project 3 of cloud-lab" — the `cloud-lab` kitchen project is the umbrella, and the MLOps idea graduates into it rather than into a standalone folder.
- `open-kit.md` (graduated 2026-04-08) carries `spawned: [[open-kit]]`, pointing at `05-projects/kitchen/open-kit/`.

### Why this matters

Graduated ideas do not get pruned — `09-ideas/CLAUDE.md` is explicit: "Ideas never die. Graduated ideas stay — they seed future ideas via lineage. No pruning." The lineage graph lets you trace:

- "What did this current project come from?"
- "What ideas did that project spawn that I haven't built yet?"
- "Which ideas keep recurring under different names?"

## /ideas derive — finding connections

```
/ideas derive
```

Allowed tools: `Read, Bash, AskUserQuestion`. This is **proactive lineage building**, not a graph-health audit. It:

1. Lists `09-ideas/*.md` (skipping `CLAUDE.md`), reads every file, and captures slug / status / domain / spark / core concept.
2. Looks for four kinds of connection:
   - **Combinations** — two ideas that solve related problems, better together than apart.
   - **Spin-offs** — one idea's research reveals a new angle that deserves its own Seed.
   - **Cross-stage connections** — a Plant's research that applies to a separate Seed.
   - **Domain crossovers** — an AI idea that could plug into a data idea.
3. Proposes the top 3-5 connections (it does not flood), each as: From `[[slug-a]]` + `[[slug-b]]`, what they share, the combined angle, and a suggested action (create a new Seed / add `derived_from` / note in a Related section).
4. Asks per proposal via `AskUserQuestion`: Create new Seed / Update lineage / Skip.
5. Acts — new Seeds reuse `start-seed` logic with `derived_from: [[slug-a]], [[slug-b]]`; lineage updates edit frontmatter on both sides.
6. Reports: "Found N connections. Created M new Seeds. Updated P lineage links."

> Correction to the prior chapter: `derive` does **not** compute "orphan ideas / hub ideas / stale plants-and-trees (>60 days) / cross-domain mismatch" metrics. That framing was invented. The real skill proposes hybrid Seeds and spin-offs from genuine connections, and its rule is quality over quantity — it never fabricates a connection to force a link.

Run cadence: monthly, or before a planning ritual.

## Relationship to 02-ana/identity/ideas.md

The vault has two idea repositories. They serve different roles.

| Repo | Role | Contents |
|------|------|----------|
| `09-ideas/` | Nursery | Every idea, all states, all domains. Includes rejected and abandoned. |
| `02-ana/identity/ideas.md` | Top-ideas shortlist | Curated list of graduated ideas John is committed to pursuing. One of the 13 auto-loaded `02-ana/identity/*.md` files. |

A graduated idea in `09-ideas/` does not automatically appear in `02-ana/identity/ideas.md`. It goes there only if John explicitly commits to pursuing it; that commitment is what makes it identity-level (always-on context for Rai). Many ideas graduate and live in `05-projects/kitchen/` for a long time without being top-ideas. That is fine — the shortlist is for active focus.

## Templates summary

| State | Template | Path | Syntax |
|-------|----------|------|--------|
| Seed | Seed.md | `12-system/templates/Seed.md` | Templater (`<% %>`) |
| Plant | Plant.md | `12-system/templates/Plant.md` | Templater |
| Tree | Tree.md | `12-system/templates/Tree.md` | Templater |
| Graduated → kitchen | (inline, in `graduate.md`) | scaffolds README + PRD + ARCHITECTURE | n/a |

Three slightly different idea shapes coexist, and it is worth knowing which is which:

1. **Template versions** (`12-system/templates/`) — the formal Templater files with `type: idea`, `tags:`, and the `grown:`/`ready:` date markers. This is the documentation-of-record shape.
2. **Skill inline versions** (`start-seed.md`, `promote.md`) — leaner, omit `type:`/`tags:`, and use slightly different section names. This is what actually gets written when you run the skills.
3. **Real files in `09-ideas/`** — a mix of the above, with extra keys (`grown:`, `graduated:`) and free-form comma `domain:` strings.

Graduation does **not** use `12-system/templates/PRD.md`; the formal PRD template is for project kitchens that you populate by hand, not for the rough scaffold `graduate` writes.

## What the lifecycle does NOT do

- It does not auto-prune. Even abandoned Seeds stay in `09-ideas/` for lineage history.
- It does not enforce a time gate between states. You can go Seed → Plant in one sitting if the research is already in your head — but `promote` will not let you **skip** a state (no Seed → Tree jump).
- It does not require all sections to be filled. The template is a guide; partial-but-honest beats full-but-fluff.
- It does not graduate without intent. The user always invokes `/ideas graduate`, and graduate refuses any idea that is not `status: tree`. There is no auto-graduation.
- It does not validate the `domain` value. Domain is a free string set on creation; if the idea drifts to a different domain, that is a useful signal (consider whether it is two ideas, or whether the original framing was wrong).

## When to retire an idea (without deleting)

Sometimes an idea is no longer worth pursuing. The lifecycle has no "killed" state because:

- Killed ideas are still useful for lineage.
- Future John might revisit.
- Pruning loses information.

To mark an idea as no-longer-active, leave the `status` as-is and add a section to the body:

```markdown
## Why I stopped pursuing
[Date and reason. 2-3 sentences.]
```

The frontmatter `status` keeps the historical record; the body explains the decision. (Note: ideas can also leave the nursery by being **renamed/dedup'd** rather than retired — in May 2026 the `matchbox` idea was dropped entirely and `OpenKit.md` was canonicalized to `open-kit.md` in commit `abc1234`. That was a deliberate cleanup, not an automated prune.)

## Cadence

| Cadence | Action |
|---------|--------|
| Daily | Capture Seeds as they appear |
| Weekly | Review Seeds for promotion candidates |
| Monthly | `/ideas derive` to surface connections |
| Quarterly | Consider graduating Trees that have matured |
| Yearly | Audit `02-ana/identity/ideas.md` shortlist for what is still committed |

The cadence is loose. The idea pipeline runs at the speed of John's thinking, not on a fixed schedule.
