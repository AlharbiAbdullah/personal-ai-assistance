---
name: start-seed
description: Capture a raw idea as a Seed in 09-ideas/ with minimal frontmatter + spark
allowed-tools: Write, AskUserQuestion, Bash
---

# Start Seed

Capture effort: low. Just get the spark on paper. Detail comes later (via `/ideas promote`).

## Instructions

### Step 1: Get the spark

Ask John in one sentence: what's the idea? Don't explain, don't justify. Just the spark.

### Step 2: Classify domain

Ask (single-select): `ai | data | business | personal | other`.

### Step 3: Pick a slug

From the spark, propose a kebab-case slug (e.g., `ai-native-data-solutions`, `k8s-mlops-platform`). Ask John to confirm or override.

### Step 4: Write the Seed

File: `~/helm/09-ideas/{slug}.md`

```markdown
---
status: seed
domain: {domain}
created: {YYYY-MM-DD}
derived_from: []
spawned: []
---

# {Slug}

## Spark
{one sentence from John}

## What Is It?
{2-3 sentences plain language — brief}

## Trigger
{what sparked this idea — a conversation, a problem, a read, etc.}
```

### Step 5: Report

Tell John: "Seed captured at `~/helm/09-ideas/{slug}.md`. Run `/ideas promote {slug}` when it's time for research."

## Rules

- Keep the Seed minimal. Detail belongs in the Plant stage.
- Don't research the idea now. That's what `promote.md` does.
- Never skip frontmatter. Downstream skills rely on `status` and `derived_from`.
