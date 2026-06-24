---
name: graduate
description: Graduate a Tree idea to 05-projects/kitchen/. Scaffold project docs; mark idea graduated.
allowed-tools: Read, Write, Bash, AskUserQuestion
---

# Graduate

Move a Tree idea into active project preparation. Creates the `05-projects/kitchen/{name}/` folder and scaffolds initial project docs.

## Instructions

### Step 1: Identify target

Ask John for the idea slug. Read `~/helm/09-ideas/{slug}.md`. Verify `status: tree` in frontmatter.

If status is not `tree`, tell John to promote it first (`/ideas promote {slug}`).

### Step 2: Confirm project name

The kitchen folder name is usually the same as the idea slug, but may differ if the project name has been refined.

Ask: "Project folder name?" Default to the idea slug.

### Step 3: Check for collision

If `~/helm/05-projects/kitchen/{project-name}/` already exists, stop. Report the collision. Ask John whether to overwrite, merge, or pick a different name.

### Step 4: Create the kitchen folder

```bash
mkdir -p ~/helm/05-projects/kitchen/{project-name}
```

### Step 5: Scaffold initial docs

Create these from the Tree content:

**`~/helm/05-projects/kitchen/{project-name}/README.md`**
```markdown
# {Project Name}

{Spark + Problem + Idea from the Tree, condensed}

## Status
Kitchen phase — planning. Code lives in `~/projects/{project-name}/` once active.

## Related
- Idea origin: `[[09-ideas/{slug}]]`
```

**`~/helm/05-projects/kitchen/{project-name}/PRD.md`**
```markdown
# {Project Name} — PRD

## Problem
{from Tree}

## Goals
{from Tree requirements}

## Non-goals
(fill in during iteration)

## Users / stakeholders
{inferred from Plant research}

## Success criteria
{from Tree milestones}

## Open questions
{from Tree open assumptions}
```

**`~/helm/05-projects/kitchen/{project-name}/ARCHITECTURE.md`** — stub only, to be filled.

### Step 6: Update the idea file

Change the idea's frontmatter:
- `status: graduated`
- Add `spawned: [[05-projects/kitchen/{project-name}]]`

Do NOT delete the idea file. Graduated ideas stay in `09-ideas/` per the "ideas never die" rule.

### Step 7: Report

"Graduated `{slug}` to `05-projects/kitchen/{project-name}/`. Initial PRD + README scaffolded. Iterate on the PRD; when ready for code, create `~/projects/{project-name}/` and an `05-projects/active/{project-name}/` folder."

## Rules

- Never graduate without status: tree.
- Never delete the idea file on graduation — lineage preserved.
- Never move the idea file out of `09-ideas/`.
- Kitchen PRD is deliberately rough. It gets refined in the kitchen, not at graduation.
