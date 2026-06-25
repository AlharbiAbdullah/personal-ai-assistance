# 04 — Capture Pipeline

How information enters the vault. Two folders, one routing matrix, two skills.

> Last updated 2026-06-14. The capture mechanism (the `00-landing/` and `01-inbox/` CLAUDE.md rules and the two `/triage` skill files) is UNCHANGED since the 2026-04-22 baseline — no commits touched `03-rai/skills/triage/*`, `00-landing/CLAUDE.md`, or `01-inbox/CLAUDE.md` in this window. What this revision fixes is drift between the prior chapter and what the live skill files actually do. The live source of truth is `~/helm/00-landing/CLAUDE.md`, `~/helm/01-inbox/CLAUDE.md`, and the skill files under `~/helm/03-rai/skills/triage/`.

## The pipeline

```
┌─────────────────┐  /triage process-landing  ┌─────────────────┐  /triage process-inbox  ┌─────────────────┐
│   00-landing/   │─────────────────────────▶│    01-inbox/    │───────────────────────▶│   destination   │
│                 │  (promote, delete,        │                 │  (research + rate +    │   (07/06/10/    │
│  manual drops   │   skip, or stop)          │  research queue │   route)               │    09/05/04)    │
└─────────────────┘                           └─────────────────┘                         └─────────────────┘
   ▲                                                  │
   │                                                  │
   │  user only                                       │  rated D → propose delete (John confirms)
   │  (Claude must NOT                                ▼
   │   create files here)                          (gone)
   │
   │
   externally:
   anything you want to remember
```

## Stage 1 — 00-landing

The parking lot.

### Rules

- **Manual drops only.** Claude must NOT create, move, or edit files in `00-landing/`.
- **Strict flat.** No subfolders.
- **Two exits only.** Promote to `01-inbox/` or delete. No archive path.
- **Ignore by default.** Do not scan for context unless John explicitly references a file.

### When something enters

John drops a file. Could be:

- A snippet from a conversation.
- A URL.
- A book title.
- A question to ask someone.
- A half-formed thought.
- A research topic seed.

The file sits there indefinitely until triaged.

### Why this stage exists

The vault would degrade if every random capture had to be classified at capture-time. Landing decouples capture from classification. You can dump fast, then classify later in batch.

### What Claude does here

Nothing autonomous. Only when the user explicitly invokes `/triage process-landing`.

## Stage 2 — /triage process-landing

The first triage skill. Walks each file in `00-landing/` interactively.

### Skill location

`~/helm/03-rai/skills/triage/process-landing.md`
(invoked via `/triage` router which routes to this sub-skill)

Frontmatter: `name: process-landing`; `allowed-tools: Read, AskUserQuestion, Bash`. The skill cannot write or edit — it can only read, ask, and shell out to `mv`/`rm`. It never edits a file's contents during triage.

### Behavior

1. **List.** `ls -1 ~/helm/00-landing/*.md`. Skip `CLAUDE.md` and hidden files. If empty, tell John landing is clear and stop.
2. **For each file:** read it and show the FULL contents (no summary). If a file is unusually large (>10 KB), show only the first 50 lines and note the full size.
3. **Ask one question** via `AskUserQuestion` with **four options**:
   - **Promote to inbox** → `mv ~/helm/00-landing/{file} ~/helm/01-inbox/{file}`
   - **Delete** → `rm ~/helm/00-landing/{file}`
   - **Skip** → leave the file in landing, advance to the next file
   - **Stop** → end the run immediately
4. **Report** one line: `promoted: N, deleted: N, skipped: N`.

It is always one file at a time — John's call on every file. The skill never batch-moves or batch-deletes. **Skip** is a real, supported choice: it leaves a file in landing and moves on, which is how a noisy folder gets partially cleared without forcing a verdict on every item. **Stop** halts the whole walk.

### When to invoke

When the landing folder feels heavy or noisy. Typical cadence: weekly.

## Stage 3 — 01-inbox

The research queue.

### Rules

- **Strict flat.** No subfolders.
- **One concept per file.** Filename is the topic.
- **Writers:** John (file moves from landing), Claude (research, via `/triage process-inbox` only).
- **No autonomous enrichment.** Rai does not enrich an inbox item without being asked.
- **Reference ≠ trigger.** When John references a specific inbox file WITHOUT invoking the skill, answer from its contents only — do not enrich, rate, or move it.

### When something enters

Two paths in:

1. **From landing** via `/triage process-landing` (the main path).
2. **Directly** from John, when he knows something already deserves research and skips landing.

### File state

A new inbox item is bare (just the filename or a few words). The next stage adds the research overlay.

## Stage 4 — /triage process-inbox

The research and routing skill.

### Skill location

`~/helm/03-rai/skills/triage/process-inbox.md`

Frontmatter: `name: process-inbox`; `allowed-tools: Read, Write, Edit, WebSearch, WebFetch, AskUserQuestion, Bash`. Unlike `process-landing`, this skill can write and edit — it rewrites each inbox file in place with the research overlay before moving it.

### Behavior (per file)

1. **Read context (Step 0).** The skill reads **three** identity files, mandatorily and up front: `02-ana/identity/goals.md`, `02-ana/identity/who-i-am.md`, and `02-ana/identity/vision.md`. This is what makes the routing personalized. (Note: it does NOT read `projects.md` or `ideas.md` — earlier chapter revisions listed those as "sometimes" reads, but the live skill does not touch them.)
2. **List.** `ls -1 ~/helm/01-inbox/*.md`, skipping `CLAUDE.md`.
3. **Per file:** read the bare item, then `WebFetch` any linked URLs and/or `WebSearch` the topic. Enrich in place with the template below.
4. **Apply the research template** to the file in place (exact shape the skill writes):

```markdown
# {title}

{original content or link}

---

## What is it
{1-2 sentences describing the subject}

## Why I should care
{1-2 sentences tied to John's goals / identity — quote specifics from the identity files}

## Why it matters
{urgency / leverage / uniqueness — what makes this non-ignorable}

## Rating
**{A | B | C | D}** — {one-line justification, relative to John's priorities}

## Suggested destination
`{folder path}` — {why this folder}
```

5. **Confirm and move.** `AskUserQuestion`: "Move to {dest}, or keep in inbox?" On confirmation, `mv` the enriched file (keeping the filename or renaming to match destination conventions). The file moves *whole* — research overlay included.
6. **Report** one line: `enriched: N, moved: N, kept: N`.

Hard rule from the skill: never fabricate "Why I should care." If you cannot honestly tie the item to John's identity, rate it lower instead of inventing a reason.

### Rating system

The A/B/C/D scale measures **relevance to John**, not generic importance. An item that would rate A for someone with different goals can rate C for him. The wording below is the live skill's scale.

| Rating | Meaning (verbatim from the skill) | Default action |
|--------|-----------------------------------|----------------|
| **A** | Directly serves a current goal or a deep identity anchor. | Move to destination |
| **B** | Clearly relevant; worth acting on soon. | Move to destination |
| **C** | Adjacent; revisit when bandwidth opens. | Move to destination, but de-prioritize |
| **D** | Weak tie; consider deleting instead of routing. | Propose delete |

D-rated items are not auto-deleted — John confirms. And the skill is explicit: "If you think an item is worse than D, propose deletion."

### Routing matrix

This is the core of the pipeline. Each routing decision is based on content type. There are exactly **six** destinations, and the skill routes to one of them — it never invents a seventh. The table below is the skill's Step-3 destination list (verbatim, and slightly richer than the bare routing table in `01-inbox/CLAUDE.md`).

| Content type | Destination folder | Why |
|--------------|--------------------|-----|
| Reading material (book, article, paper) | `07-reading/{name}/` | Books and reading get the curriculum treatment (create a curriculum folder if a book) |
| Curriculum / course / tutorial | `06-learning/{name}/` | Courses become structured learning topics |
| Tool / library / concept | `10-knowledge/{domain}/` | Permanent knowledge base — folded into existing topic notes when possible |
| Idea seed | `09-ideas/` | Routed in as a Seed (status `seed`) — this is the hand-off into the idea pipeline (see `./05-idea-lifecycle.md`) |
| Project (anything that needs PRD + design) | `05-projects/kitchen/{name}/` | Planning starts in kitchen |
| Work item (paid engagement-related) | `04-work/{engagement}/` | Confidential; engagement-scoped |

### Conventions the skill follows (not a separate options menu)

These are judgment guidelines, not a distinct branch in the skill file — the skill itself only ever routes to the six destinations above. They describe how to choose among them and how non-standard items are commonly handled in practice:

| Situation | Common handling |
|-----------|-----------------|
| Item fits two destinations | Pick the primary; cross-link via wiki-link in the secondary if appropriate |
| Item is really a quote worth preserving | Belongs in `02-ana/quotes/` (via `/life quote`), not the capture pipeline — this is a sign it should not have been promoted as a research item |
| Item is a person | Belongs in `02-ana/contacts.md` (append, not new file), outside the capture pipeline |
| Item is a private soul-level note | Belongs in `02-ana/soul/`, outside the capture pipeline |
| Item is news that should become an idea | Route to `09-ideas/` as a Seed; mention provenance in the seed |

> These are author guidance for the human running triage, NOT enforced steps in `process-inbox.md`. The live skill reads context, researches, rates, proposes one of the six destinations, and moves on confirmation — nothing more. It does not branch on quotes/people/soul-notes, and it does not chain into any other skill (no `/reading start-book` scaffolding, no `/ideas start-seed` call). Earlier chapter revisions claimed both; neither is in the skill.

### When to invoke

When `01-inbox/` accumulates 5+ items, or weekly during the Saturday review.

## Skill router — /triage

Both stages are sub-skills of `/triage`:

```
/triage
├── process-landing
└── process-inbox
```

Invocation:

```
/triage           ← router asks which sub-skill
/triage process-landing
/triage process-inbox
```

The group is exactly three files on disk — `SKILL.md` (router), `process-landing.md`, and `process-inbox.md` under `~/helm/03-rai/skills/triage/`. Nothing else. The `/triage` router appears in the skills catalog (`./07-skills-catalog.md`) among the 31 routers.

When `process-inbox` routes an item to `09-ideas/` as a Seed, it hands off to the idea pipeline — Seed → Plant → Tree → Graduated, driven by the `/ideas` skill group. That pipeline is its own chapter: `./05-idea-lifecycle.md`. So `09-ideas/` is simultaneously a capture *destination* and the *start* of the idea lifecycle.

## What does NOT enter through this pipeline

| Content | Direct path |
|---------|-------------|
| Daily journal entries | `/routine journal` writes directly to `02-ana/journal/` |
| Today/tomorrow plans | `/routine today-prep`, `/routine tomorrow-prep` write directly to `02-ana/todos/` |
| Quotes captured live | `/life quote` writes directly to `02-ana/quotes/` |
| News digest output | `/news-digest` writes directly to `08-bawaba/` (`daily/` + `weekly/`) |
| Algorithm PRDs | Algorithm writes to the work ledger under `03-rai/memory/work/{slug}/` (per-task `PRD.md` lives under `tasks/{NNN}_{task}/`) |
| Topic note edits | Direct edits via `/knowledge` skills |
| Code | Lives in `~/projects/` outside the vault |

The capture pipeline is for *new* items that don't fit a pre-existing direct path.

## Read context for personalization

This is the secret sauce of inbox triage. In Step 0, before touching any file, the skill reads exactly **three** identity files (mandatory, every run):

- `02-ana/identity/goals.md` — current goals
- `02-ana/identity/who-i-am.md` — self-definition
- `02-ana/identity/vision.md` — direction and long-horizon aim

It does NOT read `projects.md` or `ideas.md` — those are not in the skill. These three files are the lens through which an inbox item is rated and routed. An item rated A for someone with different goals would be rated C for John. The personalization is in the rating, not the categorization.

## Example walkthrough — full pipeline trace

John is reading a tweet. It mentions a book called *Antifragile*. He drops a single-line file `00-landing/antifragile-book.md` containing the URL.

A week later he runs `/triage process-landing`:

```
File: antifragile-book.md
(full contents shown)
Promote to inbox / Delete / Skip / Stop? > promote
moved → 01-inbox/antifragile-book.md
```

He runs `/triage process-inbox`:

```
File: antifragile-book.md
Reading 02-ana/identity/goals.md...
Reading 02-ana/identity/who-i-am.md...
Reading 02-ana/identity/vision.md...
Researching...

Item: Antifragile (book by Nassim Taleb)

What is it
A book about systems that gain from disorder. Argues that some things benefit from shocks
while others fall apart.

Why I should care
John is building a personal AI system designed for long-term reliability. Antifragile
thinking applies directly to system design and personal resilience.

Why it matters
Foundational text for anyone designing under uncertainty. Often cited in distributed systems
and operational excellence work.

Rating: A
Suggested destination: 07-reading
```

After confirmation, the enriched file is moved whole to `07-reading/antifragile/`. The `process-inbox` skill stops there — it does NOT chain into `/reading start-book` or any other skill. Scaffolding the curriculum (`progress.md`, lessons) is a separate, later step the user runs via `/reading start-book` when they are ready to actually work the book.

## What the pipeline does NOT do

- It does not delete D-rated items without confirmation.
- It does not move items it cannot classify — those stay in inbox until the user provides direction.
- It does not apply the template if the file already has structure (it skips and asks).
- It does not promote items into `02-ana/identity/` (those are deliberate manual additions, not capture).
- It does not bypass the 6 destinations — every routed item lands in one of them.

## Current state of the two folders (2026-06-14)

A snapshot of the backlog, to make clear that landing is *deliberately* a sedimented pile and inbox is a shorter, cleaner queue:

| Folder | Untriaged items (excl. `CLAUDE.md`) | Character |
|--------|-------------------------------------|-----------|
| `00-landing/` | ~30 manual-drop `.md` files | Mostly a single 2026-04-17 batch import. Includes stale captures like `matchbox.md` whose downstream idea was already deleted in May — landing is *not* kept in sync with downstream renames. That is expected: it is untriaged backlog, not a live index. |
| `01-inbox/` | ~8 files | Real reading/learning/tool items awaiting `process-inbox` (4 books → `07-reading/`, 2 courses → `06-learning/`, DSPy → `10-knowledge/`, 1 paper → `07-reading/`). They map cleanly to the routing table. |

The takeaway: a large landing pile is normal and healthy. Capture is decoupled from classification on purpose — the cost of an untriaged landing file is zero until you choose to triage it.

## Frequency and flow

Typical weekly cadence:

| Day | Action |
|-----|--------|
| Daily | Drops into `00-landing/` as needed |
| Wednesday | `/triage process-landing` mid-week sweep |
| Saturday | `/triage process-landing` + `/triage process-inbox` as part of weekly review |

Or: process landing/inbox whenever they feel heavy. There is no enforced cadence; the pipeline is a tool, not a ritual.
