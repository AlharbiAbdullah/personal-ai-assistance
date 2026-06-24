---
name: promote
description: Advance an idea one stage (Seed→Plant, Plant→Tree). Runs stage-appropriate research/planning.
allowed-tools: Read, Write, Edit, WebSearch, WebFetch, AskUserQuestion, Bash
---

# Promote

Advance an idea to the next pipeline stage. Reads current status; runs the right process.

## Instructions

### Step 0: Identify target

Ask John for the idea slug. Read `~/helm/09-ideas/{slug}.md`. Check current `status` in frontmatter.

### Step 1: Pick the promotion

- `seed` → `plant` (research + Q&A + web)
- `plant` → `tree` (plan + requirements + schedule)
- `tree` → graduated — use `/ideas graduate`, not this skill. Stop here.
- `graduated` → nothing. Tell John the idea has already graduated.

---

## Seed → Plant

**Your job**: heavy lifting. Research the idea from all angles.

### Process

1. **Re-read the Seed** — know the raw idea.

2. **Research the vault**:
   - `~/helm/05-projects/` — past projects, what John has built.
   - `~/helm/10-knowledge/` — relevant technical context.
   - `~/helm/06-learning/` — current learning / growth areas.
   - `~/helm/02-ana/identity/` — values, goals, vision.

3. **Ask clarifying questions** (AskUserQuestion, multiple rounds if needed):
   - What problem does this solve?
   - Who's the target user?
   - What's the unique angle — why you, why now?
   - What assumptions need validation?

4. **Search the internet** (WebSearch + WebFetch):
   - Who else has this problem?
   - What solutions exist?
   - What companies are doing this?
   - What's missing in the market?

5. **Rewrite the file as a Plant**:

```markdown
---
status: plant
domain: {same}
created: {same}
updated: {YYYY-MM-DD}
derived_from: [{links}]
spawned: []
---

# {Slug}

## Spark
{original spark}

## The Problem
{2-4 sentences: what problem, for whom, why it matters}

## The Idea
{2-4 sentences: how this solves it, unique angle}

## Research

### What others are doing
{companies, projects, products — with links}

### What's missing
{the gap this idea fills}

### Internal context
{connections to John's past projects / knowledge — wiki-links}

## Q&A (session with John)
{key questions + answers from the AskUserQuestion rounds}

## Open assumptions
{what still needs validation}

## Next steps
{to move to Tree: plan + requirements}
```

---

## Plant → Tree

**Your job**: planning and requirements.

### Process

1. **Re-read the Plant** — all research and clarifications.

2. **Gather requirements** (AskUserQuestion):
   - What must it have to be viable?
   - What's the first milestone?
   - What defines "done" for v1?

3. **Define risks** — what could go wrong; what kills this.

4. **Set schedule** — realistic start date, milestones, review dates.

5. **Rewrite as Tree**:

```markdown
---
status: tree
domain: {same}
created: {same}
updated: {YYYY-MM-DD}
derived_from: [{same}]
spawned: []
---

# {Slug}

## Spark / Problem / Idea
{condensed from Plant}

## Requirements
{must-haves for v1, bulleted}

## Plan

### Milestone 1: {name}
- {step}
- {step}

### Milestone 2: {name}
- {step}

### First actions (smallest starters)
- {thing John can do this week}

## Schedule
- Start: {date}
- M1 target: {date}
- v1 target: {date}
- Review cadence: {weekly / monthly}

## Risks
- {risk} — {mitigation}

## Graduation readiness
Ready for `05-projects/kitchen/` when:
- [ ] Requirements clear
- [ ] Plan realistic
- [ ] Risks named with mitigations
- [ ] John committed to starting
```

---

### Step 2: Update frontmatter

Change `status` from `seed` → `plant` (or `plant` → `tree`). Update `updated:` field.

### Step 3: Preserve lineage

If this idea derived from / relates to another idea, update `derived_from` (wiki-links) on both files.

### Step 4: Report

Summary: "Promoted {slug} from {old} to {new}. Next: {plant → tree | tree → graduate}."

## Rules

- Always write from research, not from prior knowledge alone. Use WebSearch for market / competitor context.
- Preserve the original Spark verbatim across stages.
- Don't skip a stage. Seed must go Plant first, Plant must go Tree before graduating.
