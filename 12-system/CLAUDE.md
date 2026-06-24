# 12-system/ — Templates, References, Scripts

## Purpose

Reusable system components for the vault. Templates for new notes, reference docs (snapshots, manuals), snippets, diagrams, media, translations.

## Subfolders

| Folder | Contents |
|--------|----------|
| `templates/` | Note templates (see inventory below) |
| `references/` | Documentation snapshots, current-state pointers (e.g., `rai-current.md`) |
| `snippets/` | Reusable code snippets |
| `diagrams/` | Diagram source files |
| `media/` | Embedded images, audio, etc. |
| `translations/` | Translation work |
| `manual/` | The full vault manual — 22 chapters (00–21) + README.md = 23 files, covering every system, folder, skill, agent, hook |

## Templates Inventory

**CRITICAL RULE: Always use existing templates. Never invent note structures.**

Before creating any note:
1. Check `12-system/templates/` for the appropriate template.
2. Read the template to understand the correct structure.
3. Use that exact structure (adapting Templater syntax to actual values).

| Template | Purpose | Destination |
|----------|---------|-------------|
| **Topic Note** | Comprehensive topic coverage with sections + toolbox | `10-knowledge/` |
| **Insight Note** | Emergent connections between notes | `10-knowledge/` |
| **Concept Note** | Focused concept capture | `10-knowledge/` |
| **Tool Note** | Tool / library / CLI reference | `10-knowledge/` |
| **MOC** | Map of content (topic hub) | `10-knowledge/_mocs/` |
| **Seed** | Raw idea capture, minimal effort | `09-ideas/` |
| **Plant** | Researched idea with Q&A and market validation | `09-ideas/` |
| **Tree** | Planned idea with requirements and schedule | `09-ideas/` |
| **Capture** | Quick inbox items | `01-inbox/` |
| **PRD** | Product Requirements Document | `05-projects/kitchen/{name}/` |
| **Project Retrospective** | Completed project reflection | `05-projects/completed/{name}/` |
| **Learning** | Courses, books, tutorials | `06-learning/` or `07-reading/` |
| **Soul Note** | Personal writing: beliefs, worldview, reflections | `02-ana/soul/` |
| **Quote** | Captured quote | `02-ana/quotes/` |
| **Personal Chapter** | Long-form personal narrative | `02-ana/soul/` |

## Rules

- **Templates are read-only.** Copy via Templater, never modify originals during a normal session. Template changes are deliberate edits, made consciously.
- **References are snapshots.** When you find drift between a reference doc and reality, update the reference doc — but flag it as "snapshot from {date}" so future sessions know it's not the live source of truth.
- **Live source of truth lives in CLAUDE.md files.** When references contradict CLAUDE.md, CLAUDE.md wins.

## What Claude should do

When creating a new note in `10-knowledge/`, `09-ideas/`, etc. — check `templates/` first. Use the appropriate template structure. Never invent.

When asked "where does X live?" or "what's the current state of Y?" — check `references/rai-current.md` first.

Do not modify templates without an explicit user request. They are infrastructure.
