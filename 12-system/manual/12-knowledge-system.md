# 12 — Knowledge System

How `10-knowledge/` works. Topic Notes, MOCs, Insight Notes. The Simplicity Theorem rule. The compounding knowledge base.

Last updated: 2026-06-14. The knowledge subsystem is the most stable part of the vault: it has had **zero commits since 2026-04-22** (the last commit, `abc1234`, created the `/knowledge` skill group on the manual's own baseline date). The corpus was authored in a burst between 2026-01-25 and 2026-02-23 and has been frozen since. So this chapter is about the **accurate current state of a stable subsystem**, not about churn. Live source of truth: `10-knowledge/CLAUDE.md` (this manual points to it; CLAUDE.md wins on any conflict).

## Philosophy

From `10-knowledge/CLAUDE.md`:

> The compounding knowledge base. Where understanding lives long-term. Built around topic notes (deep dives) and MOCs (Maps of Content — navigation hubs). Quality over quantity.

Knowledge is the long-term memory of *understood* concepts (different from raw notes or learning curricula). Things get into knowledge when they have been chewed on, simplified, and connected.

## Folder structure

```
10-knowledge/
├── CLAUDE.md               ← rules: Simplicity Theorem, note types, wiki-link weave
├── _mocs/                  ← Maps of Content (5 MOCs — navigation hubs)
│   ├── AI Engineering MOC.md
│   ├── Cross-Domain MOC.md
│   ├── Data Engineering MOC.md
│   ├── DevOps MOC.md
│   └── System Design MOC.md
├── ai/                     ← LLMs, RAG, embeddings, ML tools (9 notes)
├── data-engineering/       ← ETL, warehouses, pipelines, tools (30 notes)
├── devops/                 ← CI/CD, containers, infrastructure (13 notes)
├── meta/                   ← Python language + vault-meta (11 notes)
└── system-design/          ← patterns, architecture, decisions (23 notes)
```

Subfolders are the domain partitions. Notes live inside their domain. MOCs live in `_mocs/` and link across domains.

### Current inventory (as of 2026-06-14)

| Folder | `.md` content notes |
|--------|---------------------|
| `_mocs/` | 5 |
| `ai/` | 9 |
| `data-engineering/` | 30 |
| `devops/` | 13 |
| `meta/` | 11 |
| `system-design/` | 23 |
| **Total content notes (excludes CLAUDE.md)** | **91** |

By frontmatter `type:`: **86 `type: topic`**, **5 `type: moc`**, **0 `type: insight`**, **0 `type: concept`**, **0 `type: tool`**. In other words, every single note on disk is either a Topic Note or a MOC. The Insight, Concept, and Tool types are designed and templated but have **never been instantiated** — see "Three note types" below.

## Three note types

| Type | Purpose | Required structure | Frontmatter | On disk |
|------|---------|--------------------|-------------|---------|
| **Topic Note** | Comprehensive coverage of an entire topic area | Simplicity Theorem → Diagram → Why It Matters → Sections → Toolbox → Connections → Trade-offs | `type: topic`, `domain`, `created`, `tags`, often `tools` | 86 (the workhorse) |
| **MOC** | Topic hub with navigation | Title, grouped Topic-Note links, Concept Flow, Tools-by-Topic-Note, Related MOCs, Agent Breadcrumbs | `type: moc`, `domain`, `created`, `tags: [moc, ...]` (full, NOT minimal) | 5 |
| **Insight Note** | Emergent connection between two existing notes | Frontmatter pointers, "what surfaces" body | `type: insight`, `emerged_from: [[a]], [[b]]` | **0 — designed, never instantiated** |

There are also Concept Notes and Tool Notes (templates exist), but these have **never been created**:
- **Concept Note** (`type: concept`) — intended for a concept too small for a Topic Note with no existing Topic Note to absorb it. **0 on disk.**
- **Tool Note** (`type: tool`) — intended to document a specific tool standalone. In practice, tools are always folded into a Topic Note's Toolbox section instead. **0 on disk.**

The "main three" are Topic Note, MOC, Insight Note. Of those, only Topic Note and MOC are live; Insight Notes remain a designed-but-unused category (the system is deliberately conservative about creating them — see "The propose-first rule").

## The Topic Note format

This is the workhorse — 86 of the 91 notes. Every domain's knowledge is a set of Topic Notes plus one MOC.

### Required structure (in order)

```markdown
---
type: topic
domain: data-engineering | ai | devops | system-design | meta
created: YYYY-MM-DD
tags: [tag1, tag2]
tools: [tool1, tool2]
---

# [Topic Name]

## Simplicity Theorem
> [One sentence — the "aha" that captures why this exists]

[2-3 sentences of body, no jargon, a 12-year-old could understand]

## Simplicity Diagram
[3-5 line ASCII diagram, minimal]

---

## Why It Matters
[1-2 paragraphs — why does this exist, what problem does it solve, who benefits]

## [Section 1]
[Content]

## [Section 2]
[Content]

## [...1-8 sections depending on topic breadth...]

## Toolbox
- [Tool 1] — [one-line description]
- [Tool 2] — [one-line description]
- [Tool 3] — [one-line description]

## Connections
- [[other-note-1]] — [one-line on the connection]
- [[other-note-2]] — [one-line]

## Trade-offs
| For | Against |
|-----|---------|
| [Strength] | [Cost or limit] |
| [Strength] | [Cost or limit] |
```

Note on the canonical `type:` value: **all 86 topic notes on disk use `type: topic`.** The `Topic Note.md` template also uses `type: topic`. But the `new-topic-note` skill scaffolds `type: topic-note` — a latent inconsistency. `type: topic` is the de-facto standard; the skill scaffold is the outlier. If you run the skill, expect to correct the frontmatter to match the corpus.

### The Simplicity Theorem rule

This is the rule most often broken. The rule is grounded in **Jean-Louis Dessalles' cognitive-science research**: humans are drawn to ideas that are "unexpectedly simple," and complex ideas become memorable when reduced to their essence. The Simplicity Theorem must:

| Element | Rule |
|---------|------|
| Theorem quote | One sentence. Simple words. Captures the "why it exists" |
| Theorem body | 2-3 sentences max. No jargon. A 12-year-old could understand |
| Diagram | Minimal — if you can remove something, remove it |
| Separator | `---` after diagram to visually separate from deep content |

### Examples

**Good Simplicity Theorem:**

> Give the LLM a cheat sheet before it answers.

That is RAG explained in 9 words.

**Bad Simplicity Theorem:**

> RAG augments LLM generation by retrieving relevant documents from a vector store using semantic similarity search.

Too many jargon terms. Reads like a Wikipedia stub. Fails the 12-year-old test.

**Good Simplicity Diagram (the canonical example):**

```
Question ──▶ Search Docs ──▶ Paste + Ask ──▶ LLM ──▶ Answer
```

**Bad (too detailed):**

```
User Query → Embedding Model → Vector DB → Top-K Retrieval →
Reranking → Context Assembly → Prompt Template → LLM →
Output Parser → Response
```

### Why this rule is strict

The Simplicity Theorem is the recall surface. When future-John scans his notes, the Theorem is what he reads first. If it is dense, he won't recall it. If it is simple, the rest of the note is reachable.

## The MOC format

MOCs are topic hubs in `_mocs/`. There are exactly **5**: AI Engineering, Data Engineering, DevOps, System Design, and Cross-Domain. Each aggregates the notes within its domain (or, for Cross-Domain, across all domains).

### Real MOC anatomy (from the 5 live MOCs)

The live MOCs do **not** use a generic `Foundations / Patterns / Tools / Insights` layout. Their actual, consistent structure is:

```markdown
---
type: moc
domain: ai | data-engineering | devops | system-design | cross-domain
created: YYYY-MM-DD
tags: [moc, ...]
---

# [Domain] MOC

[One-line description]

## Topic Notes
### [Sub-grouping, e.g. "Foundation & Models"]
- [[parent-note]] — [one-line]
  - [[child-deep-dive]] — [one-line]   ← nested deep-dives as indented bullets

## Concept Flow
[ASCII flow diagram of the learning path through this domain]

## Tools (by Topic Note)
| Topic Note | Tools Covered |
|------------|---------------|
| [[note]]   | tool, tool    |

## Related MOCs
- [[Other MOC]] — [one-line on the relationship]

## Agent Breadcrumbs
<!-- Future-session pointers — Claude leaves notes here for future sessions -->

### YYYY-MM-DD
[Discovery or preference noted for future sessions]
```

MOC frontmatter is **full, not minimal** (`type`, `domain`, `created`, `tags: [moc, ...]`). The Cross-Domain MOC is the exception to the body layout: it uses `## Domain Overview` (a large ASCII map), `## Domain MOCs` (a parent/child table per domain), `## Python Language (meta/)`, `## Cross-Domain Intersections`, `## Navigation Guide`, and `## Agent Breadcrumbs`.

Note that the `MOC.md` template in `12-system/templates/` uses a different, idealized layout (Overview / Core Notes / Learning Path / Agent Breadcrumbs / External Resources) and Templater syntax. The live MOCs diverge from it. The live structure above is the de-facto standard.

### Agent Breadcrumbs section (required)

This is unique to MOCs and present in all 5. It is where Rai (or future-John) leaves navigation hints for future sessions, as dated `### YYYY-MM-DD` entries:

- "Start with [[note-foundations]] before [[note-advanced]]."
- "User prefers [Approach A] for this domain — see [[note-approach-a]]."
- "[[old-note]] was deprecated 2026-03 — use [[new-note]] instead."

These breadcrumbs are how the MOC becomes self-improving. Each session adds a crumb when it learns something worth preserving for next time. (Historical note: the Cross-Domain MOC's 2026-02-07 breadcrumb records "29 parent + 45 child + 5 MOCs = 79 knowledge notes" — a snapshot that is now superseded; the corpus grew to 91 by 2026-02-23, then froze.)

## The Insight Note format

Insight Notes capture *emergent* understanding — when two existing notes, taken together, reveal something neither has alone. **Important: zero Insight Notes exist on disk.** The category is designed and templated but has never been instantiated. The format below is the spec, not a description of live files.

### The canonical structure (the skill's version)

There are two conflicting Insight Note specs — the template and the skill diverge. Because no instance exists to settle it, **the `insight` skill's structure is canonical** (it is the active code path); the `Insight Note.md` template lags.

```markdown
---
type: insight
emerged_from: [[note-a]], [[note-b]]
created: YYYY-MM-DD
tags: [insight, {domain}]
---

# [Insight Title — what the connection IS]

## Simplicity Theorem
> [One sentence — what surfaces when A and B meet]

[2-3 sentence body]

## Simplicity Diagram
[Minimal ASCII]

---

## Why This Matters
[Why the connection is worth a note]

## The Sources
### From [[note-a]]
[1-2 sentence summary of A's relevant thread]

### From [[note-b]]
[1-2 sentence summary of B's relevant thread]

## The Synthesis
[The new understanding that neither note alone contains]

## Applies When
- [condition]

## Doesn't Apply When
- [condition]
```

(The `Insight Note.md` template's older, simpler sections — The Insight / How They Connect / Implications / Source Notes — should be brought into line with the above if either is ever updated.)

### The "propose first" rule

> Insight Notes are *proposed* before being created.

The `/knowledge insight` skill identifies a candidate connection, drafts the Insight Note, shows it to John as a "## Proposed Insight" block (yes/no/revise), and only writes it on confirm. On approval it also updates both source notes' Connections sections (a bidirectional link). This propose-first discipline is exactly why zero Insight Notes exist: the bar is high, and no candidate has cleared it. The system prefers an empty Insight category over Insight noise.

## Skills for the knowledge system

The `/knowledge` skill group lives at `03-rai/skills/knowledge/`. **5 files, last touched 2026-04-22 (commit `abc1234`), unchanged since.**

```
/knowledge
├── SKILL.md           ← router (name: knowledge)
├── new-topic-note     ← scaffold a Topic Note
├── insight            ← propose an Insight Note from two existing notes
├── audit-moc          ← check a MOC for drift
└── find-connections   ← scan notes for emergent-insight opportunities
```

All sub-skills operate on `~/helm/10-knowledge/`. Every sub-skill enforces the no-AI-typical-words rule (no leverage / utilize / seamless / robust / comprehensive / holistic / facilitate / empower / enhance / furthermore / moreover / delve).

### /knowledge new-topic-note

`allowed-tools`: Read, Write, AskUserQuestion, Bash. Six steps: (1) gather topic title + domain (ai / data-engineering / devops / system-design / meta, or propose a new domain); (2) grep the domain folder for overlap and propose a merge if a near-duplicate exists; (3) AskUserQuestion for the one-sentence Simplicity Theorem, pushing back on vague answers; (4) scaffold the note (currently writes `type: topic-note` — correct to `type: topic` to match the corpus); (5) add a wiki-link to the relevant MOC, or propose a new MOC; (6) report. Rules: never skip the theorem, never let a vague theorem through, never invent sections, always update the MOC.

### /knowledge insight

`allowed-tools`: Read, Write, AskUserQuestion, Bash. Two paths:
- User provides two-plus notes by name.
- User asks "what insights are available?" — skill scans recent notes for likely candidates.

In both cases the skill articulates the one-sentence insight, **proposes before creating** (shows a "## Proposed Insight" block; yes/no/revise), and only on approval writes the note (Simplicity Theorem structure) and updates both source notes' Connections sections bidirectionally. Rules: always propose first, never fabricate a thin insight, always link both ways.

### /knowledge audit-moc

`allowed-tools`: Read, Bash, AskUserQuestion. Seven steps: pick a MOC → find its topic cluster/folder → `ls` the folder → compare. It checks:

- **Topic drift (missing links)** — Topic Notes that exist in the domain folder but are not listed in the MOC.
- **Stale / broken entries** — MOC links that point to deleted or moved notes (no target).
- **Coverage gaps** — implied subtopics with no note (may WebSearch to confirm).
- **Breadcrumb staleness** — out-of-date `## Agent Breadcrumbs` entries.

It reports Missing / Broken / Gaps / Breadcrumbs / Overall, then offers to fix — never auto-adding or auto-deleting links without confirmation.

### /knowledge find-connections

`allowed-tools`: Read, Bash, AskUserQuestion. Seven steps: scope (full vault / one domain / one note) → load each note's Theorem + first section only → scan for candidate pairs (same-scenario / extension / tension / composition) → rank 1-3, surface only the score-3 pairs (top 3-5) → propose each via AskUserQuestion → execute (hand off to `insight`, or just cross-link, or skip) → report counts. Rule: don't flood — 3-5 strong candidates beat 20 weak ones; always show the "what emerges" sentence.

## Wiki-link weave rule

> Wiki-links woven into prose, not footnoted.

In a Topic Note, when you mention a related concept, you link it inline:

> Because [[Containers & Docker|containers are ephemeral]], we need volumes...

NOT:

> Because containers are ephemeral^1, we need volumes...
>
> [1] [[Containers & Docker]]

Wiki-links ARE the prose connections. The test: "Would a reader of note A benefit from note B?" Tags are the categorization metadata — different purpose, both apply. Don't conflate them.

Companion rule: **every note must stand on its own.** A note is broken if linking forces the reader to chase three other notes first. If it does, split the topic.

## When to create which note type

| You have | Create |
|----------|--------|
| A topic you understand and want to consolidate | Topic Note (`type: topic`) |
| Several notes in a domain that need navigation | MOC |
| Two notes that, together, reveal a new understanding | Insight Note (propose first) |
| A concept too small for a Topic Note | Concept Note (rare — none exist yet) |
| A tool that is significant on its own | Tool Note (rare — none exist; usually fold into Topic Note's Toolbox) |
| News from `08-bawaba/` to remember long-term | If pattern: Topic Note. If specific lead: 09-ideas/ Seed. |
| A research finding from `01-inbox/` | Topic Note (if topical) or fold into existing Topic Note |

## Quality bar

Quality over quantity. A domain's MOC should NOT have 50 entries — that means each entry is too small, and many should be merged into Topic Notes.

A healthy domain has:
- 1 MOC.
- 5-15 Topic Notes (the real domains run 9-30).
- 0-5 Insight Notes (insights are rare and earned — the whole corpus has 0).
- Few or no Concept/Tool Notes (most fold into Topic Notes — the whole corpus has 0 of each).

## Anti-patterns

| Anti-pattern | Why it is wrong | Fix |
|--------------|-----------------|-----|
| Atomic notes (one fact per file) | Fragments the vault; recall surface is too thin | Merge into Topic Notes |
| Footnoted wiki-links | Breaks the prose-as-graph model | Inline the link in prose |
| Skipping Simplicity Theorem | The recall surface is gone | Add a Theorem before saving |
| MOC without Agent Breadcrumbs | No navigation memory across sessions | Add the section even if empty initially |
| Insight Note without `emerged_from:` | Loses the lineage | Add the frontmatter pointers |
| Topic Note with 0 Connections | The note is orphaned | Add `## Connections` even if to a MOC |
| Topic Note with 20 Sections | Topic is too broad; should be split | Split into multiple Topic Notes + a MOC |
| Wrong `domain:` value in frontmatter | Breaks domain grouping / audit | Match the folder (see Data Mesh bug below) |

## Known live issues (current state)

The subsystem is frozen, but two real data drifts sit in the corpus right now. Both are good demonstrations of what the skills are designed to catch:

1. **Live MOC drift.** The AI Engineering MOC lists only **7** notes (3 parent + 4 child), but `ai/` has **9** `.md` files. `ai/AI Sandboxing.md` and `ai/Claude Code.md` (both created 2026-02-13, after the MOC's last breadcrumb on 2026-02-07) exist on disk but are unlinked from the MOC. This is the textbook MOC-drift failure mode that `/knowledge audit-moc` exists to fix. The other three domains are in sync (DevOps 13/13, System Design 23/23, Data Engineering 30/30).

2. **Frontmatter data bug.** `data-engineering/Data Mesh.md` carries `domain: orders` (a stray example value — Data Mesh's running example uses an "orders" data domain). It should be `domain: data-engineering`. This is the only malformed domain value in the corpus.

## The MOC drift failure mode

The most common failure in the knowledge base is **MOC drift**: notes get created in a domain but the MOC isn't updated. Over time, the MOC becomes a stale subset of the domain. Future-John uses the MOC for navigation and misses notes. The AI Engineering MOC above is a live instance.

`/knowledge audit-moc` exists to fix this. Run it periodically (monthly, or after a heavy week of note creation).

## Templates summary

All knowledge templates live at `12-system/templates/` (lowercase on disk; `10-knowledge/CLAUDE.md` still references `12-system/Templates/` with a capital T — a casing-only discrepancy). All 5 are unchanged since 2026-04-17.

| Template file | Use for | On disk | Note |
|---------------|---------|---------|------|
| `Topic Note.md` | Topic Notes | 86 | `type: topic`; matches the corpus |
| `MOC.md` | MOCs | 5 | `type: moc`; Templater syntax; layout diverges from the live MOCs |
| `Insight Note.md` | Insight Notes | 0 | `type: insight`; structure lags the `insight` skill (skill is canonical) |
| `Concept Note.md` | Concept Notes (rare) | 0 | `type: concept`; never instantiated |
| `Tool Note.md` | Tool Notes (rare) | 0 | `type: tool`; never instantiated (tools fold into Toolbox) |

## Cross-references to other manual chapters

- [01-folder-map.md#10-knowledge](./01-folder-map.md#10-knowledge) — folder structure
- [07-skills-catalog.md](./07-skills-catalog.md) — the `/knowledge` skill group in the full catalog
- [11-templates-and-conventions.md](./11-templates-and-conventions.md) — full template details
- [04-capture-pipeline.md](./04-capture-pipeline.md) — how content reaches `10-knowledge/`

## Frequency and cadence

| Cadence | Action |
|---------|--------|
| As-needed | Create a Topic Note when you understand something well enough to consolidate |
| As-needed | Propose an Insight Note when a connection becomes obvious (propose first) |
| Monthly | `/knowledge audit-moc` for active domains (the AI MOC is overdue) |
| Quarterly | `/knowledge find-connections` to surface insight candidates |
| Yearly | Review MOCs for restructuring (split, merge, delete) |

There is no enforced cadence. The knowledge base grows at the speed of understanding — and at the moment it is paused, frozen at 91 notes since 2026-02-23.
