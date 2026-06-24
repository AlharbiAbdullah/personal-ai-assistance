# The Helm Vault Manual

The brain folder, explained. Every screw, every bolt.

This manual is the read-the-manual document for the helm vault. It addresses both the vault owner and Rai (the AI). It assumes nothing. If you read it cover to cover, you will be able to operate the vault, debug failures, and extend the system without guessing.

> **About the examples.** This manual documents a real, working system. The owner, names, engagements, dates, and life details throughout reflect a fictional **"John Doe"** sample persona used for illustration — replace them with your own as you adopt the vault. The system mechanics (folders, skills, agents, hooks, the algorithm, memory) are real and accurate.

**Last updated:** 2026-06-14.
**Vault root:** `~/helm/`.
**Brain root:** `~/helm/03-rai/`.
**Algorithm version:** v3.7.0.

## Table of contents

| #   | Chapter                                                        | What it covers                                                              |
| --- | -------------------------------------------------------------- | --------------------------------------------------------------------------- |
| 00  | [Overview](./00-overview.md)                                   | Philosophy, principals, conventions, the rules that govern everything       |
| 01  | [Folder map](./01-folder-map.md)                               | All 14 numbered folders (00-13) plus root files and dotfiles, with rules quoted from each CLAUDE.md |
| 02  | [Architecture](./02-architecture.md)                           | How the layers fit together: identity, memory, skills, agents, hooks, state |
| 03  | [Session lifecycle](./03-session-lifecycle.md)                 | What happens from SessionStart to SessionEnd, hook by hook                  |
| 04  | [Capture pipeline](./04-capture-pipeline.md)                   | 00-landing → 01-inbox → destination, the routing table                      |
| 05  | [Idea lifecycle](./05-idea-lifecycle.md)                       | Seed → Plant → Tree → Graduated → Project, lineage tracking                 |
| 06  | [Algorithm and PRD](./06-algorithm-and-prd.md)                 | The 7 phases, ISC decomposition, effort tiers, the PRD contract             |
| 07  | [Skills catalog](./07-skills-catalog.md)                       | All 35 top-level skills (30 routers + 5 leaves) and their sub-skills, when to invoke each |
| 08  | [Agents catalog](./08-agents-catalog.md)                       | All 12 agents, models, scope, invocation                                    |
| 09  | [Hooks reference](./09-hooks-reference.md)                     | Every hook, its event, what it does, what it costs                          |
| 10  | [Memory systems](./10-memory-systems.md)                       | File memory + ChromaDB + state + work + learning + relationship + security  |
| 11  | [Templates and conventions](./11-templates-and-conventions.md) | All 16 templates, naming rules, frontmatter schemas                         |
| 12  | [Knowledge system](./12-knowledge-system.md)                   | Topic Notes, MOCs, Insight Notes, the Simplicity Theorem rule               |
| 13  | [Personal OS](./13-personal-os.md)                             | 02-ana structure, identity files, life skills                               |
| 14  | [Work and projects](./14-work-and-projects.md)                 | 04-work engagements, work-plans, 05-projects lifecycle                      |
| 15  | [News digest](./15-news-digest.md)                             | The /news v5.6 pipeline, sources, scoring, gem feed + Bawaba Weekly, headless Ubuntu scheduling |
| 16  | [Workflows](./16-workflows.md)                                 | The 8 numbered playbooks in 11-workflows                                    |
| 17  | [Config and security](./17-config-and-security.md)             | settings.json, hook wiring, secret patterns, security validator             |
| 18  | [Diagrams](./18-diagrams.md)                                   | Every flow diagram in one place                                             |
| 19  | [Glossary](./19-glossary.md)                                   | Every term defined                                                          |
| 20  | [Troubleshooting](./20-troubleshooting.md)                     | Common failures and how to fix them                                         |
| 21  | [Cheatsheet](./21-cheatsheet.md)                               | One-page reference for the impatient                                        |

## How to read this manual

**If you are a human onboarding the vault:** read 00 → 01 → 02 → 06. That is the conceptual frame. Everything else is reference.

**If you are an AI session that just woke up here:** the identity auto-load already gave you the operating rules. This manual exists for when you need to look up *how something works* (how does the capture pipeline route? what hook fires when? what is the ISC count gate?). Use the table of contents above as a jump table.

**If you came here to debug something:** start at chapter 20 (Troubleshooting). It has the common failures and where to look.

**If you came here to add something new** (a skill, an agent, a hook, a folder): the relevant chapter has the rules. 07 for skills, 08 for agents, 09 for hooks, 11 for templates and naming. 02 for the architecture context.

**If you just want a one-page reminder:** chapter 21 (Cheatsheet) is a single page with the top paths, top skills, top agents, the 7 phases, the 5 effort tiers, the 4 idea states, and the one critical rule.

## Conventions inside the manual

- File paths are absolute (`~/helm/...`). They work without context.
- Tables for inventories. ASCII diagrams for flows. Code fences for paths and snippets.
- Quotes from CLAUDE.md files are verbatim. CLAUDE.md is the live source of truth; this manual is a compiled reference. When the two diverge, CLAUDE.md wins.
- Cross-links between chapters use relative paths (`./03-session-lifecycle.md`).
- No emojis (per response-format rules). No banned words.

## Versioning

This manual is a snapshot. The vault evolves. Re-read the source CLAUDE.md when you need to confirm a current rule. The manual is never the source of truth — it points to the source of truth.

When the vault structure changes materially (a new folder, a new top-level skill router, an algorithm version bump), update the affected chapter and bump the "Last updated" date at the top of this README.

## What this manual does not cover

- Code inside `~/projects/` (lives outside the vault)
- The Claude Code harness itself (refer to Anthropic docs)
- Plugin internals (frontend-design, claude-hud — refer to their own docs)
- The Obsidian config in `.obsidian/` (editor concern, not vault concern)

For everything else inside `~/helm/`, this manual is the answer.
