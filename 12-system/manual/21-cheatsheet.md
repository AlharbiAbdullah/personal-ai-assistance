# 21 — Cheatsheet

_Last updated 2026-06-14._

One page. Top paths, top skills, top agents, the 7 phases, the 5 effort tiers, the 4 idea states, the 3 project lifecycle stages, the 2 identity folders, the 1 critical rule.

Counts: 35 skill entries (31 routers + 4 leaves), 12 agents, 16 templates, 8 workflows, 19 hook scripts / 24 wired invocations, Algorithm v3.7.0. CLAUDE.md is the live source of truth; this page is a quick index, not a substitute.

## Top paths

| Thing | Path |
|-------|------|
| Vault root | `~/helm/` |
| Rai brain | `03-rai/` |
| Algorithm spec | `03-rai/algorithm/v3.7.0.md` |
| Skills | `03-rai/skills/{router}/SKILL.md` |
| Agents | `03-rai/agents/{name}.md` |
| Hooks (code) | `03-rai/hooks/*.py` (19 scripts) |
| Hook wiring / settings | `03-rai/config/settings.json` (symlinked as `~/.claude/settings.json`) |
| Sync architecture | `03-rai/SYNC-ARCHITECTURE.md` |
| John identity | `02-ana/identity/` (13 auto-loaded `.md`) |
| Rai identity | `03-rai/identity/` (4 auto-loaded `.md`) |
| File memory | `03-rai/memory/{state,work,learning,relationship,security}/` |
| ChromaDB | `03-rai/semantic-memory/chromadb/` |
| Pending sessions | `03-rai/semantic-memory/pending/` |
| Templates | `12-system/templates/` (16 files) |
| Workflows | `11-workflows/` (8 playbooks) |
| Manual | `12-system/manual/` |
| Investment | `02-ana/financial/investment/` |
| Code | `~/projects/{name}/` (outside vault) |

## Top skills (by frequency)

35 skill entries total = 31 routers + 4 leaves (leaves: `ask-model`, `map-updater`, `project-init`, `workflow`); ~134 sub-skill files. Full catalog in [07-skills-catalog.md](./07-skills-catalog.md).

| Skill | Use |
|-------|-----|
| `/triage process-landing` | Walk landing files: promote or delete |
| `/triage process-inbox` | Research + rate + route inbox items |
| `/ideas start-seed` | Capture a new idea |
| `/ideas promote` | Advance idea Seed→Plant→Tree |
| `/ideas graduate` | Tree → kitchen project |
| `/news-digest` | Daily/weekly news digest (v5.6) |
| `/routine journal` | Daily journal entry |
| `/routine today-prep` | Morning prioritization |
| `/routine bills` | Monthly bill-pay run |
| `/work weekly-planner` | Monday work plan |
| `/investment status` | values-based paper-trading status |
| `/rai process-sessions` | Drain pending → ChromaDB (Linux coordinator only) |
| `/rai sanity` | Brain healthcheck (tiers A–K) |

Routers new since 2026-04-22: `/writing` (arabic, proposals, prds, social-media, blog), `/investment` (status, recommend, screen, review, ops, convene), `/ubuntu` (theme, hyprland, diagnostics, dotfiles-bootstrap, tips), `/ask-model`. `/business` shrank to 3 subs (sales, presentations, pricing) when proposals + prds moved into `/writing`.

## Top agents

12 agents = 10 specialists (architect, engineer, designer, pentester, qa-tester, reviewer, artist, writer, debugger, sre) + 2 methodology (algorithm, researcher). All run model `opus` at `effort: xhigh` — no sonnet, no haiku. Invoke via `Task(subagent_type: "<name>")`. Full roster in [08-agents-catalog.md](./08-agents-catalog.md).

| Agent | When |
|-------|------|
| `engineer` | Production-grade implementation with tests (opus) |
| `architect` | System design, ADRs, trade-off analysis (opus) |
| `reviewer` | Code review (independent context, opus) |
| `qa-tester` | Edge case hunt from user POV (opus) |
| `debugger` | Root-cause specialist — reproduce, bisect, prove (opus) |

## The 7 algorithm phases

```
1. OBSERVE   →  Reverse-engineer wants. Set tier. Generate ISC. Select capabilities.
2. THINK     →  Pressure-test ISC. Premortem. Refine.
3. PLAN      →  Architecture, file structure, sequence.
4. BUILD     →  Invoke selected capabilities (Skill/Task tool calls).
5. EXECUTE   →  Do the work. Mark criteria done.
6. VERIFY    →  Test each criterion. Capture evidence.
7. LEARN     →  Reflect. Append JSONL. phase: complete.
```

## The 5 effort tiers

| Tier | Budget | ISC | Min capabilities |
|------|--------|-----|------------------|
| Standard | <2 min | 8-16 | 1-2 |
| Extended | <8 min | 16-32 | 3-5 |
| Advanced | <16 min | 24-48 | 4-7 |
| Deep | <32 min | 40-80 | 6-10 |
| Comprehensive | <120 min | 64-150 | 8-15 |

## The 4 idea states

```
Seed → Plant → Tree → Graduated
```

| State | Frontmatter | Skill |
|-------|-------------|-------|
| Seed | `status: seed` | `/ideas start-seed` |
| Plant | `status: plant` | `/ideas promote` |
| Tree | `status: tree` | `/ideas promote` |
| Graduated | `status: graduated` | `/ideas graduate` |

## The 3 project lifecycle stages

```
05-projects/kitchen/   → 05-projects/active/ + ~/projects/   → 05-projects/completed/
(planning)               (in progress)                          (retrospective)
```

## The 2 identity folders (auto-loaded)

| Folder | Files |
|--------|-------|
| `02-ana/identity/` | who-i-am, goals, vision, mindset, story, wrong, projects, ideas, contacts, definitions, environment, tech-stack, rai-public (13 `.md`) |
| `03-rai/identity/` | dai-identity, ai-steering-rules, response-format, coding-format (4 `.md`; `security-patterns.yaml` is NOT auto-loaded) |

## The 1 critical rule

> Listing a capability without invoking it = CRITICAL FAILURE.

Every capability selected in the Algorithm's OBSERVE phase MUST be invoked via `Skill()` or `Task()` tool call during BUILD or EXECUTE. Writing prose that resembles the skill's output does NOT count.

When in doubt, invoke MORE capabilities, not fewer.

## The capture pipeline (one-line)

```
00-landing → 01-inbox → {07-reading | 06-learning | 10-knowledge | 09-ideas | 05-projects | 04-work}
```

Triggered by `/triage process-landing` then `/triage process-inbox`.

## The session lifecycle (hooks in order)

19 distinct `.py` scripts, 24 wired invocations (security-validator runs across 4 PreToolUse matchers).

```
SessionStart (2):  session-start.py → check-version.py
UserPromptSubmit (4):  rating-capture → auto-work-creation → session-auto-name → update-tab-title
PreToolUse (7 matchers):  security-validator (Bash/Edit/Write/Read), agent-execution-guard (Task),
                          skill-guard (Skill), set-question-tab (AskUserQuestion)
PostToolUse (3):  auto-update-codemap.sh (Write), codemap-on-bash.sh (Bash), question-answered (AskUserQuestion)
Stop (1):  stop-orchestrator
SessionEnd (7):  save-memory → work-completion-learning → session-summary → relationship-memory
                 → update-counts → integrity-check → algorithm-scan
```

Note: `agent-execution-guard.py` is WARN-ONLY (never blocks). `update-counts.py` targets a non-existent `03-rai/settings.json`, so the on-disk counts block is frozen at 2026-04-18 and stale.

## Memory tiers (one-line each)

- **State** (`memory/state/`): per-session, dies at SessionEnd, orphans swept at SessionStart (6h).
- **Work** (`memory/work/{slug}/`): per-task ledger (META.yaml + nested `tasks/`), lives indefinitely.
- **File memory** (`memory/{learning,relationship,security}/`): JSONL + dated MD, indefinite.
- **Semantic memory** (`semantic-memory/chromadb/`): vector store, collection `memories` (~734 embeddings, all-MiniLM-L6-v2, 384-dim), forever. Pending queue at `semantic-memory/pending/`. SINGLE-WRITER: only the Linux coordinator (`pc`) drains pending → ChromaDB and writes to origin; Mac is a read-only replica over Tailscale SSH (`03-rai/SYNC-ARCHITECTURE.md`).

## The 5 governing rules (chapter 00)

1. **Identity auto-load is the contract.** Files in `*/identity/*.md` load every session.
2. **Delete over archive.** Session JSONs archive automatically; two standing exceptions also stay (`13-archive/news/`, `13-archive/learning/`). Everything else: delete when no longer live.
3. **CLAUDE.md is the live source of truth.** When references contradict CLAUDE.md, CLAUDE.md wins.
4. **Always use existing templates.** Never invent structure. 16 templates cover most needs.
5. **Min Capabilities is binding.** Selecting a capability without invoking = CRITICAL FAILURE.

## When to skip the Algorithm

- Greetings, casual chat
- Direct lookups ("what is X", "where does Y live")
- Single-line edits with obvious correctness
- Acknowledgments, thanks

When in doubt: run a Standard-tier Algorithm, not skip.

## Voice rule

Only the primary agent emits voice curls (Algorithm phase transitions). Subagents and background agents skip voice entirely.

## Confidentiality

`02-ana/` and `04-work/` contain personal and client data. No external sharing without explicit authorization. No AI mentions in `04-work/` outputs.

## When something is broken

1. Read the relevant CLAUDE.md.
2. Read the relevant SKILL.md or agent file.
3. Run `/rai sanity`.
4. Check `memory/learning/system/integrity/` for recent reports.
5. Check `memory/learning/system/hook-errors.jsonl` for recent failures.
6. Restart the session.

Full troubleshooting in [20-troubleshooting.md](./20-troubleshooting.md).

## Refreshing the navigation index

```
/map-updater
```

Updates `.helm-index/helm-index.md`. Run after structural changes (new folders, renamed files, new chapters in this manual).

## Drain ChromaDB

```
/rai process-sessions
```

Empties `semantic-memory/pending/` into ChromaDB. Run weekly or when pending count is high.

## Healthcheck

```
/rai sanity
```

Runs an 11-tier (A–K) brain healthcheck: data safety, environment, ChromaDB, pipeline, config, vault+identity, memory index, hygiene, algorithm+agents, skills+hooks, work state.

## Read the manual

```
ls 12-system/manual/
```

22 chapters (00–21) + README.md = 23 files. Start with README.md.
