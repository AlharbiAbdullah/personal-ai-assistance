# 11 — Templates and Conventions

Last updated: 2026-06-14.

Every template, every naming rule, every frontmatter schema. The structural backbone of the vault.

The live source of truth for the inventory is `12-system/CLAUDE.md` (its "Templates Inventory" table). This chapter is a derived snapshot — when it disagrees with that file or with the actual template files, those win.

> NOTE: As of 2026-06-14 the templates subsystem is byte-frozen — there have been zero commits to `12-system/templates/` or `12-system/CLAUDE.md` since 2026-04-21 (commit `abc1234`, the brain-to-helm rename and folder renumber). The schemas below are quoted from the actual files, not paraphrased. Several earlier paraphrases were wrong; they are corrected here and flagged.

## The cardinal rule

> CRITICAL RULE: Always use existing templates. Never invent note structures.

Quoted from `12-system/CLAUDE.md`. There are 16 template files (15 note `.md` + `ISC.json`). Every note type John uses has one. Inventing structure fragments the vault.

## Where templates live

```
12-system/templates/
├── Capture.md
├── Concept Note.md
├── Insight Note.md
├── ISC.json
├── Learning.md
├── MOC.md
├── Personal Chapter.md
├── Plant.md
├── PRD.md
├── Project Retrospective.md
├── Quote.md
├── Seed.md
├── Soul Note.md
├── Tool Note.md
├── Topic Note.md
└── Tree.md
```

All `.md` except `ISC.json`. The template files are NOT uniform in placeholder syntax — this is a real, undocumented inconsistency:

- **Templater (`<% tp.date.now("YYYY-MM-DD") %>`)** — 8 files: Capture, Insight Note, Learning, MOC, Plant, Project Retrospective, Seed, Tree.
- **Mustache (`{{date}}` / `{{title}}`)** — 7 files: Concept Note, Personal Chapter, PRD, Quote, Soul Note, Tool Note, Topic Note.
- **Static (no placeholders)** — `ISC.json`.

Two templates carry NO `type:` frontmatter field at all: `Personal Chapter.md` and `Quote.md`. Three templates (Seed, Plant, Tree) all share `type: idea` and are distinguished only by `status:`.

## Templates by destination

| Template | Destination folder | Triggered by | Syntax |
|----------|--------------------|--------------|--------|
| Topic Note | `10-knowledge/{domain}/` | `/knowledge new-topic-note` | Mustache |
| Insight Note | `10-knowledge/` | `/knowledge insight` | Templater |
| Concept Note | `10-knowledge/` | Manual | Mustache |
| Tool Note | `10-knowledge/` | Manual (often folded into Topic Note Toolbox) | Mustache |
| MOC | `10-knowledge/_mocs/` | Manual or `/knowledge audit-moc` | Templater |
| Seed | `09-ideas/` | `/ideas start-seed` | Templater |
| Plant | `09-ideas/` | `/ideas promote` (Seed→Plant) | Templater |
| Tree | `09-ideas/` | `/ideas promote` (Plant→Tree) | Templater |
| Capture | `01-inbox/` | `/triage process-inbox` | Templater |
| PRD | `05-projects/kitchen/{name}/` or `03-rai/memory/work/{slug}/` | `/ideas graduate` or Algorithm | Mustache |
| Project Retrospective | `05-projects/completed/{name}/` | Manual on project completion | Templater |
| Learning | `06-learning/` or `07-reading/` | `/learning start-topic`, `/reading start-book` | Templater |
| Soul Note | `02-ana/soul/` | Manual | Mustache |
| Quote | `02-ana/quotes/` | `/life quote` | Mustache |
| Personal Chapter | `02-ana/soul/` | Manual | Mustache |
| ISC.json | Used in PRDs (not standalone) | Algorithm internal | Static JSON |

> STALE INTERNAL PATHS: Three template files (`Capture.md`, `Learning.md`, `Project Retrospective.md`) still embed pre-renumber folder numbers in their internal DESTINATION comments — `02_projects/`, `03_knowledge/`, `06_learning/`. Those folders no longer exist (now `05-projects`, `10-knowledge`, `06-learning`). The destinations above and the `12-system/CLAUDE.md` inventory use CURRENT numbering and are correct; only the comments inside those three files are stale. They have never been fixed in a commit.

---

## Template details

### Topic Note

**Path:** `12-system/templates/Topic Note.md`
**Destination:** `10-knowledge/{domain}/`

```markdown
---
type: topic
domain: data-engineering | ai | devops | system-design
created: {{date}}
tags: [tag1, tag2, tag3, tag4, tag5, tag6]
tools: [tool1, tool2]
---

# [Topic Name]

## Simplicity Theorem
> [One sentence — the "aha" that captures why this exists]

[2-3 sentences max; no jargon; a 12-year-old could understand]

## Simplicity Diagram
[Minimal ASCII — 3-5 lines]

---

## Why It Matters

## [Section 1..N]

## Toolbox
- [Tool 1] — [one-line] + table (Use for / Strengths / Limitations / Docs)

## Connections
- Builds on [[other-note-1]]
- Enables [[other-note-2]]
- Contrasts with [[other-note-3]]

## Trade-offs
| For | Against |
|-----|---------|
| ... | ... |
```

**Required:** Simplicity Theorem, Simplicity Diagram, separator (`---`), Why It Matters, Toolbox, Connections, Trade-offs. The body holds 1-8 sections depending on topic breadth.

**Uses Mustache `{{date}}`, not Templater.** The `domain` enum in the actual file is `data-engineering | ai | devops | system-design` — there is NO `meta` value (an earlier manual listed it; that was wrong). `tags:` has 6 slots; `tools:` has 2.

### Insight Note

**Path:** `12-system/templates/Insight Note.md`
**Destination:** `10-knowledge/`

```markdown
---
type: insight
created: <% tp.date.now("YYYY-MM-DD") %>
emerged_from:
  - "[[]]"
  - "[[]]"
---

# [Insight Title — what the connection IS]

## The Insight
[2-3 sentences: what surfaces when you put A and B together that neither has alone]

## How They Connect
[The mechanism of the connection]

## Implications
[The new understanding]

## Source Notes
- [[]]
- [[]]
```

**Note on frontmatter:** `emerged_from:` is a YAML **block list** of two `"[[]]"` items in the actual file — NOT the inline `[[a]], [[b]]` form an earlier manual showed. Uses Templater. There are **0 Insight Notes on disk** — the type is designed and templated but has never been instantiated.

**Rule:** Insight Notes are *proposed* before being created. The `/knowledge insight` skill prompts the user to confirm before writing.

### Concept Note

**Path:** `12-system/templates/Concept Note.md`
**Destination:** `10-knowledge/`. Mustache.

A focused single-concept note (smaller than a Topic Note). Frontmatter: `type: concept`, `domain` (data-engineering/ai/devops), `created: {{date}}`, `tags:` (6 slots). Body: Simplicity Theorem → Simplicity Diagram → Why It Matters → Core Idea → Diagram → How It Connects (Builds on / Enables / Contrasts with / Combines with) → Trade-offs (table) → Tools (table: Tool/Purpose/Complexity). Used when a concept is too small to warrant a Topic Note and there is no existing Topic Note that could absorb it. **0 Concept Notes on disk** at survey.

### Tool Note

**Path:** `12-system/templates/Tool Note.md`
**Destination:** `10-knowledge/` (rare standalone; usually folded into Topic Note's Toolbox section). **0 Tool Notes on disk** — they fold into Topic Note Toolbox sections in practice.

The actual file is a full Simplicity-Theorem note, not the small stub an earlier manual showed. Uses Mustache.

```markdown
---
type: tool
domain: data-engineering | ai | devops
created: {{date}}
tags: [tool, category1, category2, category3, category4, category5]
official_docs: [URL]
---

# [Tool Name]

## Simplicity Theorem
## Simplicity Diagram
## Why This Tool
## Core Capability
## Key Concepts
| Concept | ... |
## When to Use
| Use Case | Good Fit | Poor Fit |
## Alternatives
| Tool | ... |
## Related Concepts
- [[topic-note]]
```

**Frontmatter has an `official_docs:` field** (an earlier manual omitted it). `domain` enum = `data-engineering | ai | devops`.

### MOC (Map of Content)

**Path:** `12-system/templates/MOC.md`
**Destination:** `10-knowledge/_mocs/`

```markdown
---
type: moc
created: <% tp.date.now("YYYY-MM-DD") %>
updated: <% tp.date.now("YYYY-MM-DD") %>
---

# [Domain] MOC

## Overview

## Core Notes
- [[note-1]]
- [[note-2]]

## Learning Path
- Start here: [[note-foundations]]
- Then: [[note-mid]]
- Advanced: [[note-advanced]]

## Agent Breadcrumbs
<!-- Claude leaves notes here for future sessions -->

### YYYY-MM-DD
[Discovery or preference noted for future sessions, e.g.,
 "Start with [[note-foundations]] before [[note-advanced]]"]

## External Resources
```

**Frontmatter is `type / created / updated` only** — there is NO `domain:` field in the actual file (an earlier manual added one; that was wrong). Uses Templater for both dates.

**Required:** Agent Breadcrumbs section. This is where Rai (or future-John) leaves navigation hints. The body sections are Overview, Core Notes, Learning Path (Start here / Then / Advanced), Agent Breadcrumbs, External Resources.

### Seed

**Path:** `12-system/templates/Seed.md`
**Destination:** `09-ideas/`

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
> [One sentence — the raw idea]

## What Is It?
[Brief explanation, 1-3 sentences]

## Trigger
[What sparked this? Where did it come from?]
```

### Plant

**Path:** `12-system/templates/Plant.md`
**Destination:** `09-ideas/` (frontmatter `status: plant`). Templater.

Frontmatter adds a `grown:` date over Seed (so Plant has both `created` and `grown`). Body sections: Spark → Problem → Insight → Vault Connections → Market Landscape → Dialogue Summary (Q&A) → Potential → Open Questions. Adds Q&A, market validation, and connection-mapping beyond Seed.

### Tree

**Path:** `12-system/templates/Tree.md`
**Destination:** `09-ideas/` (frontmatter `status: tree`). Templater.

Frontmatter adds `ready` and `scheduled_start:` over Plant (Tree also carries an empty `grown:`). Body sections: Spark → Problem & Solution (Problem/Solution/Target User) → Requirements (checkboxes) → Plan (Phase 1/2/3) → First Steps (checkboxes) → Success Criteria → Schedule (Start/First Milestone/Review) → Resources Needed → Risks. Adds requirements, phased plan, schedule, and decision-to-graduate beyond Plant.

### Capture

**Path:** `12-system/templates/Capture.md`
**Destination:** `01-inbox/`. Templater.

The actual `Capture.md` is an **idea-capture form**, not the `/triage` rating shape an earlier manual showed (that rating shape — What is it / Why care / Rating A|B|C|D / Suggested destination — is the `/triage process-inbox` *research output*, not this template).

Frontmatter: `type: capture`, `created`, `source` (suggester: twitter / linkedin / github / blog / youtube / podcast / paper / conversation / idea / other), `action` (suggester: to-read / to-try / to-learn / to-build), `status: inbox`.

Body sections: `**Tags:**` line → `# title` → DESTINATION comment → `## What Is It?` → `## Link / Source` → `## What Problem Does It Solve?` → `## How Is It Relevant To Me?` → `## Related To` → `## Next Action` (checkbox) → `## Notes`.

> STALE: the DESTINATION comment inside the file still routes by old numbering — `to-read/to-try → 03_knowledge/`, `to-learn → 06_learning/`, `to-build → 02_projects/`. Current folders are `10-knowledge`, `06-learning`, `05-projects`.

### PRD

**Path:** `12-system/templates/PRD.md`
**Destination:** `05-projects/kitchen/{name}/PRD.md` or `03-rai/memory/work/{slug}/PRD.md`

```markdown
---
title: "{{title}}"
status: DRAFT
created: "{{date}}"
updated: "{{date}}"
type: prd
---

# {{title}}

## Problem
## Success Criteria       (3 checkboxes)
## Scope
  ### In Scope
  ### Out of Scope
## Ideal State Criteria (ISC)   (table: # / Criterion / Tag [E/I/R] / Status / Verify; "Import from ISC.json or define inline")
  ### Anti-Criteria
## Phases                 (Phase 1 / Phase 2)
## Decisions              (table: Decision / Options / Choice / Reason)
## Log                    (table: Date / Session / Action / Notes, seeded with "Created PRD")
```

**Frontmatter includes an `updated:` field** (an earlier manual omitted it). The ISC tag legend in PRD.md is **E/I/R** (Essential/Important/Refinement) — note ISC.json itself only shows tag "E". Uses Mustache.

There are TWO PRD types using this template (or a variant):
- **Project PRD** — durable; lives in `05-projects/kitchen/{name}/`. Edited by user.
- **Task PRD** — per-task; lives in `03-rai/memory/work/{slug}/`. Edited by Algorithm during execution. Has different frontmatter (8-field algorithm schema).

The Algorithm uses its own schema for task PRDs (see [06-algorithm-and-prd.md](./06-algorithm-and-prd.md)).

### Project Retrospective

**Path:** `12-system/templates/Project Retrospective.md`
**Destination:** `05-projects/completed/{name}/`. Templater.

> CORRECTION: the frontmatter `type:` is **`project-retrospective`** — NOT `retrospective` (an earlier manual claimed `retrospective` with a 3-field schema; that schema was fabricated). The real frontmatter is 11 fields and the body is a large multi-section narrative.

```markdown
---
type: project-retrospective
status: completed
started:
ended:
company:
role:
team_size:
domain: data-eng | ai | devops | full-stack   (suggester)
tech: []
impact_level: high | medium | low             (suggester)
growth_areas: []
---

# [Project] — Retrospective

## Simplicity Theorem
## Simplicity Diagram

## The Story
  ### Context & Origin
  ### My Role & Responsibilities

## The Work
  ### Problem Statement
  ### Solution
  ### Technical Architecture   (table)
  ### Key Technical Decisions
  ### Challenges Faced         (table)

## The Team
  ### Composition              (table)
  ### Team Dynamics
  ### My Leadership

## The Impact
  ### Business Outcomes
  ### Technical Outcomes
  ### My Contribution

## The Growth
  ### Technical Skills
  ### Soft Skills
  ### Mindset Shifts
  ### If I Did It Again

## Connections
  ### Related Knowledge Notes
  ### Patterns

## Timeline Highlights          (table)
```

> STALE: the DESTINATION comment inside the file still uses `02_projects/completed/` (old numbering). Current path is `05-projects/completed/`.

### Learning

**Path:** `12-system/templates/Learning.md`
**Destination:** `06-learning/{topic}/` or `07-reading/{book}/`. Templater.

A general lesson template. Frontmatter: `type: learning`, `created`, `category` (suggester: tool/framework/concept/book/course/language), `status` (suggester: queued/in-progress/completed/paused), `priority` (suggester: high/medium/low). Body: `**Tags:**` line → `# title` → DESTINATION comment → `## What Is It?` → `## Why Learn This?` → `## Learning Goals` → `## Resources` → `## Progress Log` (dated) → `## Key Takeaways`. Specifics depend on whether it is for a course (`06-learning`) or a book (`07-reading`). Each topic also has a `progress.md` (separate template, defined in the folder's CLAUDE.md).

> STALE: the DESTINATION comment uses `06_learning/` and "extract key insights to `03_knowledge/`" — old numbering (current: `06-learning`, `10-knowledge`).

### Soul Note

**Path:** `12-system/templates/Soul Note.md`
**Destination:** `02-ana/soul/`. Mustache.

Frontmatter: `type: soul`, `created: {{date}}`, `tags: []`. Body: `# <Title>` → one-line core blockquote → free-form writing ("No rules. Say what you mean.") → `## Connections`. Deliberately minimal — personal writing on beliefs, worldview, reflections.

### Quote

**Path:** `12-system/templates/Quote.md`
**Destination:** `02-ana/quotes/`. Mustache.

> CORRECTION: the actual file is minimal. There is NO `type:`, NO `source:`, NO author line, and NO "Why this resonates" section (an earlier manual invented all of those).

```markdown
---
captured: {{date}}
tags: []
---

> "[Quote text]"
```

### Personal Chapter

**Path:** `12-system/templates/Personal Chapter.md`
**Destination:** `02-ana/soul/`. Mustache. NO `type:` field.

A full life-narrative scaffold (far richer than "long-form narrative"). Header `# {{title}}` + theme blockquote. Sections: Overview (Period/Age/Location/Theme) → The Setup → Key Events (Event 1/2/3) → People (table Person/Role/Impact) → Lessons Learned (1/2/3) → How I Changed (Before/After) → Artifacts → What I'd Tell Myself Then (blockquote) → Connection to [[values]] → Related ([[my-story]], Previous/Next chapter links). A chapter in John's life story.

### ISC.json

**Path:** `12-system/templates/ISC.json`
**Used by:** Algorithm internal — the JSON schema for ISC (Ideal State Criteria) tracking, version `1.0`.

Not a note template. Not directly used by humans. The Algorithm uses it for the ISC tables inside PRDs. Structure: `criteria[]` (each: id, criterion "8-12 word state description", tag "E", status "PENDING", verify method, evidence, notes), `antiCriteria[]` (id, criterion "What must NOT happen", status "CLEAR"), `satisfaction` {satisfied, partial, failed, total}. The seven verify methods are **CLI, Test, Static, Browser, Grep, Read, Custom**. See [06-algorithm-and-prd.md](./06-algorithm-and-prd.md).

---

## Naming conventions

Different folders, different rules. The vault is opinionated about names.

### Folder naming (Universal)

- Numbered top-level folders: `NN-name/` where NN is fixed (00-13).
- All other folders: kebab-case (`my-folder-name/`).

### File naming per folder

| Folder | Naming convention |
|--------|-------------------|
| `00-landing/` | Any descriptive name (manual; no constraint) |
| `01-inbox/` | Filename = topic |
| `02-ana/identity/*.md` | Lowercase kebab-case (`who-i-am.md`, `goals.md`) |
| `02-ana/journal/*.md` | `YYYY-MM-DD.md` |
| `02-ana/quotes/*.md` | Author-name kebab-case or topic |
| `02-ana/todos/today-plans/*.md` | `YYYY-MM-DD.md` |
| `02-ana/todos/tomorrow-plans/*.md` | `YYYY-MM-DD.md` |
| `02-ana/soul/*.md` | Date-prefix or topic |
| `03-rai/skills/{router}/SKILL.md` | Always `SKILL.md` for router |
| `03-rai/skills/{router}/{sub-skill}.md` | Kebab-case sub-skill name |
| `03-rai/agents/{name}.md` | Kebab-case agent name |
| `03-rai/hooks/*.py` | Kebab-case hook name |
| `03-rai/memory/work/{slug}/` | Slug = `YYYYMMDD-HHMMSS_kebab-task-description` |
| `03-rai/memory/relationship/{YYYY-MM}/{YYYY-MM-DD}.md` | Date-based |
| `03-rai/memory/security/{YYYY}/{MM}.jsonl` | Year/month |
| `04-work/{engagement}/` | Short, obvious engagement name (kebab-case) |
| `04-work/work-plans/*.md` | `YYYY-WNN.md` (ISO week) |
| `05-projects/kitchen/{name}/` | Kebab-case project name |
| `05-projects/active/{name}/` | Kebab-case (matches kitchen) |
| `05-projects/completed/{name}/` | Kebab-case (matches active) |
| `06-learning/{topic}/` | Kebab-case topic |
| `06-learning/{topic}/Lesson NNN - [Subtopic].md` | "Lesson NNN - " prefix |
| `07-reading/{book}/` | Kebab-case book |
| `07-reading/{book}/Lesson NNN - [Topic].md` | "Lesson NNN - " prefix |
| `08-bawaba/daily/*.md`, `08-bawaba/weekly/*.md` | `daily/YYYY-MM-DD.md`, `weekly/YYYY-WWW.md` |
| `09-ideas/*.md` | Kebab-case idea name |
| `10-knowledge/{domain}/*.md` | Descriptive topic names (Title Case allowed for clarity) |
| `10-knowledge/_mocs/*.md` | "Topic MOC.md" or "Domain MOC.md" |
| `11-workflows/*.md` | `NN-workflow-name.md` (numbered prefix) |
| `12-system/templates/*.md` | Title Case template name |
| `12-system/manual/*.md` | `NN-chapter-name.md` |
| `13-archive/historical-sessions/*.json` | Auto-generated UUIDs |

### Code naming (when writing code)

From `03-rai/identity/coding-format.md`:

| Style | Used for |
|-------|----------|
| Framework files (as-is) | `CLAUDE.md`, camelCase for JS/TS |
| kebab-case | Repos, directories, docs, configs, branches |
| snake_case | Python files, functions, variables |
| PascalCase | Python classes |
| SCREAMING_SNAKE_CASE | Constants, env vars |
| snake_case | SQL, dbt |
| kebab-case | Docker services |

---

## Frontmatter schemas

Different note types have different frontmatter requirements.

### Idea (Seed/Plant/Tree)

All three share `type: idea` and differ by `status:`. Fields accrete as the idea matures: Seed has `created`; Plant adds `grown`; Tree adds `ready` + `scheduled_start`. (The 4th pipeline stage "graduated" has no template — graduation moves the idea into `05-projects/kitchen/` and uses PRD.md there.)

```yaml
---
type: idea
status: seed | plant | tree
domain:
derived_from: []
spawned: []
created: YYYY-MM-DD
grown:            # Plant + Tree only
ready:            # Tree only
scheduled_start:  # Tree only
tags: [idea, seed | plant | tree]
---
```

### Topic Note

```yaml
---
type: topic
domain: data-engineering | ai | devops | system-design
created: YYYY-MM-DD
tags: [tag1, ... tag6]
tools: [tool1, tool2]
---
```

No `meta` domain value. `tags:` has 6 slots.

### Insight Note

`emerged_from:` is a YAML block list, not inline. No `tags:` field in the actual file.

```yaml
---
type: insight
created: YYYY-MM-DD
emerged_from:
  - "[[]]"
  - "[[]]"
---
```

### MOC

No `domain:` field; has `updated:` instead.

```yaml
---
type: moc
created: YYYY-MM-DD
updated: YYYY-MM-DD
---
```

### Progress tracker (06-learning, 07-reading)

```yaml
---
type: progress-tracker
created: YYYY-MM-DD
mode: beginner | mid | expert
---
```

### Project PRD

```yaml
---
title: "Project Name"
status: DRAFT | ACTIVE | COMPLETE
created: YYYY-MM-DD
updated: YYYY-MM-DD
type: prd
---
```

### Task PRD (Algorithm)

```yaml
---
task: 8-word task description
slug: YYYYMMDD-HHMMSS_kebab-task-description
effort: standard | extended | advanced | deep | comprehensive
phase: observe | think | plan | build | execute | verify | learn | complete
progress: N/M
mode: interactive | background
started: ISO timestamp
updated: ISO timestamp
iteration: N (optional)
---
```

### Project Retrospective

`type: project-retrospective` (not `retrospective`). 11 frontmatter fields:

```yaml
---
type: project-retrospective
status: completed
started:
ended:
company:
role:
team_size:
domain: data-eng | ai | devops | full-stack
tech: []
impact_level: high | medium | low
growth_areas: []
---
```

### Quote

No `type:`, no `source:`. Minimal.

```yaml
---
captured: YYYY-MM-DD
tags: []
---
```

---

## File-creation workflow

When creating a new note:

1. **Identify the type.** Topic? Idea? Quote? PRD?
2. **Find the template.** `ls 12-system/templates/`.
3. **Read the template** to understand structure.
4. **Use Templater** (Obsidian) or copy-paste; replace `<% ... %>` (Templater) or `{{ ... }}` (Mustache) placeholders with actual values — check which syntax the file uses.
5. **Place in the right folder** per the destination table.
6. **Apply correct naming** per the convention table.
7. **Verify frontmatter** matches the schema for that type.

The relevant skill (e.g., `/knowledge new-topic-note`) automates steps 2-5.

## Wiki-links — vault-wide

Wiki-links (`[[note-name]]`) form the connection graph. They appear in:

- Topic Note `## Connections` section (Builds on / Enables / Contrasts with).
- Insight Note `emerged_from:` frontmatter block list + `## Source Notes`.
- Idea `derived_from:` and `spawned:` frontmatter; Plant `## Vault Connections`.
- Project Retrospective `## Connections` section (Related Knowledge Notes / Patterns).
- MOC body (`## Core Notes` and `## Learning Path` are wiki-linked).
- Personal Chapter `## Connection to [[values]]` and `## Related`.

**Rules:**
- Wiki-links are woven into prose, not footnoted.
- They are semantic connections, not citations.
- For tags (categorization), use `tags:` frontmatter, not wiki-links.

---

## Templates that are read-only

> Templates are read-only. Copy via Templater, never modify originals during a normal session.

From `12-system/CLAUDE.md`. Templates are infrastructure. They change deliberately, not as a side-effect of writing a note. If a template needs revising, that is its own task with its own intent.

## Adding a new template

When a new note type emerges:

1. **Confirm it is genuinely new.** Can you fold it into an existing template? If yes, do that instead.
2. **Create the template** at `12-system/templates/[Title Case].md`.
3. **Add to inventory** in `12-system/CLAUDE.md`.
4. **Add to inventory** in this manual chapter.
5. **Consider creating a skill** to scaffold it (e.g., `/knowledge new-topic-note` for Topic Notes).

Adding templates is rare. The 16 cover most note needs, and the subsystem has been unchanged since 2026-04-21.

## What NOT to template

- Single-use notes that will never be repeated.
- Notes that are deeply personal or context-dependent.
- One-off content that fits an existing template loosely (use the existing one).
- Anything for which the template would have only 1-2 fixed sections.

Templates are for recurring patterns, not one-shots.

## References (12-system/references/)

Different from templates. References are *snapshots* of system state at a point in time. `12-system/references/` holds exactly ONE file as of 2026-06-14.

| Reference | Purpose |
|-----------|---------|
| `rai-current.md` | Snapshot of Rai's current state (skills counts, agents counts, etc.). Itself last touched 2026-04-21 — already drifted (it predates the writing/ask-model/investment/ubuntu routers). |

**Rule:** When a reference doc drifts from reality, update it but flag it as `snapshot from {date}`. The live source of truth is always the actual file (e.g., `skills/MANIFEST.md` is the truth; `references/rai-current.md` is a derived snapshot).

> Live source of truth lives in CLAUDE.md files. When references contradict CLAUDE.md, CLAUDE.md wins.

## Common mistakes to avoid

| Mistake | Fix |
|---------|-----|
| Inventing a new note structure on the fly | Use an existing template; if none fit, ask |
| Putting the wrong frontmatter on a Topic Note | Re-read template; match exactly |
| Naming a Lesson without "Lesson NNN -" prefix | Rename per convention |
| Capitalizing a kebab-case file | Rename to lowercase |
| Wiki-linking to a non-existent note | Create the note or remove the link |
| Skipping the Simplicity Theorem on a Topic Note | Add it before saving |
| Putting a soul note in `02-ana/quotes/` | Move to `02-ana/soul/` |
| Creating a Brief.md or Kanban.md in a project | Those patterns are retired; just write what's needed in PRD.md |
