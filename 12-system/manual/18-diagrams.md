# 18 — Diagrams

Every flow diagram in the manual, collected in one place. Use this chapter for visual reference.

Last updated: 2026-06-14. Diagrams reflect current state; the live source of truth for any subsystem is its `CLAUDE.md` and the chapter that owns it. Cross-links point to the owning chapter (e.g. `./07-skills-catalog.md`).

Every fact here is current as of 2026-06-14; the manual's prior baseline was 2026-04-22.

## Vault folder map

```
~/helm/
├── 00-landing/      Parking lot for manual drops
├── 01-inbox/        Research queue (Rai enriches and routes)
├── 02-ana/          John's Life OS
│   ├── identity/      ← AUTO-LOADED (13 .md)
│   ├── soul/
│   ├── journal/
│   ├── todos/
│   ├── quotes/
│   ├── family/
│   ├── health/
│   ├── financial/      (incl. investment/ — values-based paper-trading)
│   ├── admin/
│   ├── travel/
│   ├── shopping/
│   └── voice-samples/  (Arabic writing corpus)
├── 03-rai/          Rai's brain
│   ├── identity/      ← AUTO-LOADED (4 .md + security-patterns.yaml)
│   ├── algorithm/
│   ├── skills/
│   ├── agents/
│   ├── hooks/
│   ├── config/         (settings.json, mcp.json, statusline.sh, .skill-lock.json)
│   ├── memory/
│   ├── semantic-memory/
│   └── SYNC-ARCHITECTURE.md   ← single-coordinator sync spec
├── 04-work/         Work footprint (client-alpha, helios, tableau)
├── 05-projects/     Project lifecycle
│   ├── kitchen/       ← planning (cloud-lab, open-kit)
│   ├── active/        ← in progress (created on demand; code in ~/projects/)
│   └── completed/     ← retrospective
├── 06-learning/     Courses and tutorials
├── 07-reading/      Books through Claude Code
├── 08-bawaba/       News digest output (daily/ + weekly/)
├── 09-ideas/        Idea pipeline (Seed → Plant → Tree → Graduated)
├── 10-knowledge/    Topic notes, MOCs, Insight Notes
├── 11-workflows/    8 numbered playbooks
├── 12-system/       Templates, references, snippets, diagrams, manual
│   ├── templates/
│   ├── references/
│   ├── snippets/
│   ├── diagrams/
│   ├── media/
│   ├── translations/
│   └── manual/        ← THIS MANUAL
├── 13-archive/      Session JSONs + frozen exceptions (news/, learning/)
├── CLAUDE.md        Vault-wide navigation (live source of truth)
├── north-star.md    Root Kanban
├── scratch-board.md
├── Excalidraw/
├── .helm-index/     Auto-maintained navigation
├── .obsidian/  .claude/  .git
```

Note: `.codemap/` does NOT exist in the vault. `/map-updater` only creates it inside a code project; in the vault it maintains `.helm-index/helm-index.md`.

## Architecture — the 8 layers

```
┌─────────────────────────────────────────────────────────────────┐
│  L8  USER INTENT                                                │
│      John types into Claude Code                            │
└──────────────────────────────┬──────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────┐
│  L7  HOOKS (event-driven)                                       │
│      SessionStart / UserPromptSubmit / PreToolUse /             │
│      PostToolUse / Stop / SessionEnd                            │
│      19 .py scripts, 24 wired invocations                       │
└──────────────────────────────┬──────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────┐
│  L6  IDENTITY (auto-loaded context)                             │
│      03-rai/identity/*.md (4)  +  02-ana/identity/*.md (13)     │
└──────────────────────────────┬──────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────┐
│  L5  ALGORITHM (decision framework)                             │
│      OBSERVE → THINK → PLAN → BUILD → EXECUTE → VERIFY → LEARN  │
└──────────────────────────────┬──────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────┐
│  L4  SKILLS + AGENTS (capabilities)                             │
│      35 skill entries (30 routers + 5 leaves) + 12 agents       │
└──────────────────────────────┬──────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────┐
│  L3  STATE + WORK (per-session + per-task)                      │
└──────────────────────────────┬──────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────┐
│  L2  MEMORY (long-term)                                         │
│      File memory + ChromaDB semantic memory                     │
└──────────────────────────────┬──────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────┐
│  L1  VAULT CONTENT (the actual brain)                           │
│      00-13 numbered folders                                     │
└─────────────────────────────────────────────────────────────────┘
```

## Session lifecycle timeline

```
TIME ─────────────────────────────────────────────────────────────────────────▶

[SessionStart]                                                       [SessionEnd]
     │                                                                     │
     ▼                                                                     ▼
┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐    ┌────────────┐
│  Identity  │  │   User     │  │   Tool     │  │   Stop     │    │   Memory   │
│  Auto-Load │─▶│   Prompt   │─▶│   Calls    │─▶│  Signal    │───▶│ Persistence│
│  + Sweep   │  │   Hooks    │  │ + Guards   │  │            │    │   + Logs   │
│   (2)      │  │    (4)     │  │ Pre+Post(10)│ │    (1)     │    │    (7)     │
└────────────┘  └────────────┘  └────────────┘  └────────────┘    └────────────┘
```

The 6 events fire 24 wired hook invocations in total (2 + 4 + 7 PreToolUse + 3 PostToolUse + 1 + 7). See the Hook event flow diagram below and `./09-hooks-reference.md`.

## Capture pipeline

```
┌─────────────────┐  /triage process-landing  ┌─────────────────┐  /triage process-inbox  ┌─────────────────┐
│   00-landing/   │─────────────────────────▶│    01-inbox/    │───────────────────────▶│   destination   │
│                 │  Promote / Delete /       │                 │  research + rate +     │   (07/06/10/    │
│  manual drops   │  Skip / Stop              │  research queue │  A/B/C/D + route       │    09/05/04)    │
└─────────────────┘                           └─────────────────┘                         └─────────────────┘
```

`process-landing` offers 4 options (Promote / Delete / Skip / Stop). `process-inbox` Step 0 reads three identity files first — `02-ana/identity/goals.md`, `who-i-am.md`, `vision.md` — then rates each item A/B/C/D for relevance to John (worse-than-D proposes deletion) and routes. The 6 routing destinations are `07-reading/`, `06-learning/`, `10-knowledge/`, `09-ideas/`, `05-projects/kitchen/`, `04-work/{engagement}/`. See `./04-capture-pipeline.md`.

## Idea lifecycle

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
                  │  05-projects/kitchen/{name}/                          │
                  │    scaffolds README.md + PRD.md + ARCHITECTURE.md     │
                  │    (inline templates, not 12-system/templates/PRD.md) │
                  └──────────────────────────────────────────────────────┘
                                                  │
                                                  │  start coding
                                                  ▼
                  ┌──────────────────────────────────────────────────────┐
                  │  ~/projects/{name}/  (code, outside vault)            │
                  │                       +                              │
                  │  05-projects/active/{name}/  (non-code; created on    │
                  │                               demand)                 │
                  └──────────────────────────────────────────────────────┘
                                                  │
                                                  │  ship
                                                  ▼
                  ┌──────────────────────────────────────────────────────┐
                  │  05-projects/completed/{name}/  (retrospective)      │
                  └──────────────────────────────────────────────────────┘
```

The pipeline is flat — status lives in frontmatter, not folders, until graduate. Current inventory: 6 ideas (2 seed, 0 plant, 3 tree, 1 graduated). The `/ideas` router has 4 sub-skills: start-seed, promote, graduate, derive. See `./05-idea-lifecycle.md`.

## Algorithm 7 phases

```
                   ┌──────────────────────────────────────────────┐
                   │  Algorithm v3.7.0                            │
                   │  Goal: Euphoric Surprise (9-10 ratings)      │
                   │  State machine: IDLE → [7 phases] → COMPLETE │
                   └──────────────────┬───────────────────────────┘
                                      │
                   ┌──────────────────▼───────────────────────────┐
                   │  1. OBSERVE                                  │
                   │     Reverse-engineer wants                   │
                   │     Set effort tier                          │
                   │     Generate ISC criteria                    │
                   │     Apply Splitting Test (4 tests)           │
                   │     ISC count gate (floor per tier)          │
                   │     Select capabilities                      │
                   └──────────────────┬───────────────────────────┘
                                      │
                   ┌──────────────────▼───────────────────────────┐
                   │  2. THINK                                    │
                   │     Riskiest assumptions                     │
                   │     Premortem                                │
                   │     Prerequisites check                      │
                   │     Refine ISC                               │
                   └──────────────────┬───────────────────────────┘
                                      │
                   ┌──────────────────▼───────────────────────────┐
                   │  3. PLAN                                     │
                   │     Architecture                             │
                   │     File structure                           │
                   │     Step sequence                            │
                   │     EnterPlanMode if Advanced+               │
                   └──────────────────┬───────────────────────────┘
                                      │
                   ┌──────────────────▼───────────────────────────┐
                   │  4. BUILD                                    │
                   │     INVOKE selected capabilities             │
                   │     (Skill or Task tool calls)               │
                   │     Prepare execution                        │
                   └──────────────────┬───────────────────────────┘
                                      │
                   ┌──────────────────▼───────────────────────────┐
                   │  5. EXECUTE                                  │
                   │     Do the work                              │
                   │     Mark criteria done in PRD                │
                   │     Update progress counter                  │
                   └──────────────────┬───────────────────────────┘
                                      │
                   ┌──────────────────▼───────────────────────────┐
                   │  6. VERIFY                                   │
                   │     Test each criterion                      │
                   │     Capture evidence                         │
                   │     Check capability invocation              │
                   └──────────────────┬───────────────────────────┘
                                      │
                   ┌──────────────────▼───────────────────────────┐
                   │  7. LEARN                                    │
                   │     Reflection (4 questions)                 │
                   │     Set phase: complete                      │
                   │     (SessionEnd algorithm-scan.py records    │
                   │      ISC/phase/Task-spawn state)             │
                   └──────────────────────────────────────────────┘
```

Five effort tiers gate the ISC floor: Standard (8) / Extended (16) / Advanced (24) / Deep (40) / Comprehensive (64). The runtime state is recorded at SessionEnd by `algorithm-scan.py` (which replaced the retired per-PostToolUse `algorithm-tracker.py`), writing `memory/state/algorithms/{session_id}.json`. See `./06-algorithm-and-prd.md`.

## Memory tiers

```
┌──────────────────────────────────────────────────────────┐
│  TIER 1 — STATE     (per-session, dies at SessionEnd)    │
│  03-rai/memory/state/                                    │
│  - current-work-{uuid}.json                              │
│  - tab-titles/{uuid}.json                                │
│  - algorithms/{uuid}.json                                │
│  - session-names.json (entries pruned)                   │
│  - identity-cache.json (mtime-validated, self-healing)   │
└──────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│  TIER 2 — WORK      (per-task, lives indefinitely)       │
│  03-rai/memory/work/{slug}/                              │
│  - META.yaml (6-field hook-written ledger; authoritative)│
│  - tasks/{NNN}_{task}/PRD.md                             │
│  - tasks/{NNN}_{task}/ISC.json                           │
│  - tasks/{NNN}_{task}/THREAD.md                          │
└──────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│  TIER 3 — FILE MEMORY  (structured, JSONL + dated MD)    │
│  03-rai/memory/                                          │
│  - learning/signals/ratings.jsonl                        │
│  - learning/system/{counts-history,hook-perf}.jsonl      │
│  - learning/system/integrity/change-{TIMESTAMP}.json     │
│  - relationship/{YYYY-MM}/{YYYY-MM-DD}.md                │
│  - security/{YYYY}/{MM}/security-{YYYYMMDD}.jsonl         │
│  - ai-calls/  (external-LLM telemetry, /ask-model)        │
└──────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│  TIER 4 — SEMANTIC MEMORY  (vector store, ChromaDB)      │
│  03-rai/semantic-memory/                                 │
│  - chromadb/chroma.sqlite3                               │
│  - chromadb/{uuid}/HNSW indices                          │
│  - pending/session_{TIMESTAMP}.json (queue)              │
│  - scripts/py-chroma.sh (uv python3.12 + chromadb)       │
│  collection 'memories': ~734 embeddings, 384-dim, cosine │
│  embedding model: all-MiniLM-L6-v2                       │
│  SINGLE-WRITER: only the Linux coordinator writes        │
└──────────────────────────────────────────────────────────┘
```

The work-dir layout is nested now: `work/{slug}/META.yaml` is the authoritative status marker `/rai sanity` walks, with per-task `tasks/{NNN}_{task}/{PRD.md,ISC.json,THREAD.md}` artifacts. See `./10-memory-systems.md`.

## Memory drain — pending → ChromaDB

```
SessionEnd
    │
    │  save-memory.py  (skips if <4 human messages)
    ▼
semantic-memory/pending/session_{TIMESTAMP}.json
    │
    │  /rai process-sessions
    │  (runs ONLY on the Linux coordinator — sole ChromaDB writer)
    ▼
For each pending JSON:
  ├── should_save gate:
  │     Plan-mode → always save
  │     non-plan ≥4 user messages → save
  │     <4 → archive without ChromaDB save
  ├── Auto-infer type (build/explore/debug/planning/brainstorm)
  ├── Auto-infer mood (low/med/high)
  ├── Content-density score (duration ignored)
  │     outcome multipliers: completed 1.0 / partial 0.85 /
  │                          blocked 0.9 / exploration 0.7
  ├── Summarize via AI
  ├── Embed (all-MiniLM-L6-v2, 384-dim)
  └── store_to_chromadb.py → get_or_create_collection('memories',
                              hnsw:space=cosine), id = session uuid
                                    │
                                    ▼
                       13-archive/historical-sessions/
                       (raw JSON moved here for archival)
```

The drain runs through the uv/chromadb wrapper `semantic-memory/scripts/py-chroma.sh`. Because ChromaDB is a binary store git cannot merge, the drain is a Linux-only step — the Mac never writes it (see the Sync diagram below). See `./10-memory-systems.md`.

## Skills router map

```
                              skills/  (35 entries)
                                │
        ┌───────────────────────┼─────────────────────┐
        │                       │                     │
   ENGINEERING            KNOWLEDGE+CONTENT       PERSONAL
        │                       │                     │
   ┌────┴─────┐         ┌──────┴──────┐         ┌────┴────┐
   architecture          research              life
   data                 investigation         routine
   devops               scraping              work
   coding-standards     content-analysis      investment   ← NEW
   testing              media                 mac
   ai                   business              ubuntu        ← NEW
   security             writing        ← NEW
                        news-digest           BRAIN MAINTENANCE
   ENG-WORKFLOW         THINKING              ┌────┴────┐
   ┌─────┴────┐         ┌───┴───┐             rai
   git                  think (12 modes)      recall
   project-init (leaf)                        map-updater (leaf)
                        EXTERNAL MODELS       VAULT RHYTHM
                        ┌────┴────┐           ┌─────┴────┐
                        ask-model (leaf)      triage
                        workflow (leaf)       ideas
                                              knowledge
                                              learning
                                              reading
```

35 top-level entries = 30 routers + 5 leaves (ask-model, map-updater, project-init, visual-plan, workflow); ~128 sub-skill files. Routers new since 2026-04-22: writing, ask-model, investment, ubuntu. `/business` shrank to 3 subs (sales, presentations, pricing) when proposals + prds moved into the new `/writing` router (arabic, proposals, prds, social-media, blog). See `./07-skills-catalog.md`.

## Agents tier map

```
                              agents/  (12 total)
                                │
        ┌───────────────────────┼──────────────────────┐
        │                       │                      │
   SPECIALISTS (10)         METHODOLOGY (2)         (no sonnet/haiku)
        │                       │                  Models used:
   architect (opus)        algorithm (opus)        all 12 agents run
   engineer (opus)         researcher (opus)        opus at effort
   designer (opus)                                  xhigh.
   pentester (opus)
   qa-tester (opus)                               Permission allow-lists
   reviewer (opus)                                VARY per agent (not a
   artist (opus)                                  single uniform block).
   writer (opus)
   debugger (opus)
   sre (opus)
```

Unchanged since 2026-04-22. The four removed multi-model researchers (codex/gemini/grok/perplexity) are historical (gone 2026-04-18). The `agent-execution-guard.py` hook is WARN-ONLY — it never blocks, validates agent existence, reads frontmatter, or enforces permissions. See `./08-agents-catalog.md` (unchanged target).

## Hook event flow

```
SessionStart  (2)
  ├── session-start.py (via py-chroma.sh: chroma recall + identity load + state sweep)
  └── check-version.py

UserPromptSubmit  (4, every prompt)
  ├── rating-capture.py
  ├── auto-work-creation.py
  ├── session-auto-name.py
  └── update-tab-title.py

PreToolUse  (7, matched by tool)
  ├── Bash             → security-validator.py
  ├── Edit             → security-validator.py
  ├── Write            → security-validator.py
  ├── Read             → security-validator.py
  ├── Task             → agent-execution-guard.py  (WARN-ONLY)
  ├── Skill            → skill-guard.py
  └── AskUserQuestion  → set-question-tab.py

PostToolUse  (3, matched by tool)
  ├── Write            → map-updater/scripts/auto-update-codemap.sh
  ├── Bash             → map-updater/scripts/codemap-on-bash.sh
  └── AskUserQuestion  → question-answered.py

Stop  (1)
  └── stop-orchestrator.py

SessionEnd  (7, in order)
  ├── save-memory.py
  ├── work-completion-learning.py
  ├── session-summary.py
  ├── relationship-memory.py
  ├── update-counts.py
  ├── integrity-check.py
  └── algorithm-scan.py
```

19 distinct `.py` hook scripts, 24 wired invocations (`security-validator.py` is reused across 4 PreToolUse matchers; the 2 codemap PostToolUse hooks are `.sh` scripts under `03-rai/skills/map-updater/scripts/`, not in `hooks/`). Known bug: `update-counts.py` writes to a non-existent `03-rai/settings.json`, so the `counts` block in `config/settings.json` is frozen at 2026-04-18 (skills:66, hooks:22 — stale). See `./09-hooks-reference.md`.

## Identity auto-load

```
     SessionStart
          │
          │  session-start.py
          ▼
   ┌──────────────────────┐         ┌──────────────────────┐
   │  03-rai/identity/    │         │  02-ana/identity/    │
   │  (4 auto-loaded)     │         │  (13 auto-loaded)    │
   │                      │         │                      │
   │  dai-identity.md     │         │  who-i-am.md         │
   │  ai-steering-rules   │         │  goals.md            │
   │  response-format.md  │         │  vision.md           │
   │  coding-format.md    │         │  mindset.md          │
   │                      │         │  story.md            │
   │  (security-          │         │  wrong.md            │
   │   patterns.yaml is   │         │  projects.md         │
   │   NOT auto-loaded)   │         │  ideas.md            │
   │                      │         │  contacts.md         │
   │                      │         │  definitions.md      │
   │                      │         │  environment.md      │
   │                      │         │  tech-stack.md       │
   │                      │         │  rai-public.md  ← NEW│
   └──────────┬───────────┘         └──────────┬───────────┘
              │                                │
              └─────────────┬──────────────────┘
                            ▼
                ┌──────────────────────────┐
                │   identity-cache.json    │
                │   (mtime-validated,      │
                │    self-healing)         │
                └────────────┬─────────────┘
                             │
                             ▼
                  ┌──────────────────┐
                  │  Model context   │
                  │  (every session) │
                  └──────────────────┘
```

17 auto-loaded `.md` total (4 Rai + 13 John). `security-patterns.yaml` lives in `03-rai/identity/` but is read only by `security-validator.py`, never auto-loaded. See `./13-personal-os.md`.

## Knowledge note structure (Topic Note)

```
┌──────────────────────────────────────────┐
│  # [Topic Name]                          │
├──────────────────────────────────────────┤
│  ## Simplicity Theorem                   │
│  > [One sentence — the "aha"]            │
│  [2-3 sentence body, no jargon]          │
├──────────────────────────────────────────┤
│  ## Simplicity Diagram                   │
│  [3-5 line ASCII]                        │
├──────────────────────────────────────────┤
│  ---                                     │
├──────────────────────────────────────────┤
│  ## Why It Matters                       │
│  ## [Section 1]                          │
│  ## [Section 2]                          │
│  ## [...]                                │
│  ## Toolbox                              │
│  ## Connections                          │
│  ## Trade-offs                           │
└──────────────────────────────────────────┘
```

All 86 topic notes carry `type: topic` frontmatter. Insight, Concept, and Tool notes are templated but never instantiated (0 on disk each). See `./12-knowledge-system.md`.

## Capture-to-knowledge full path

```
External world
      │
      ▼
00-landing/  (manual drop)
      │
      │  /triage process-landing  (Promote / Delete / Skip / Stop)
      ▼
01-inbox/  (promoted)
      │
      │  /triage process-inbox
      │  - Step 0 reads 02-ana/identity/{goals,who-i-am,vision}.md
      │  - applies research template
      │  - rates A/B/C/D (relevance to John)
      │  - routes
      ▼
   destination
   ┌─────────────────────────┐
   │ 07-reading/             │
   │ 06-learning/            │
   │ 10-knowledge/{domain}/  │  ← this branch becomes Topic Notes
   │ 09-ideas/ (Seed)        │
   │ 05-projects/kitchen/    │
   │ 04-work/{engagement}/   │
   └─────────────────────────┘
```

## News-digest pipeline (v5.6)

```
/news  ─────────────────────────────────────────────────────────────────────────▶
       │
       ├─ mode "day"  (last 24h)                ├─ mode "week"  (last 7 days)
       │                                        │
       ▼                                        ▼
  COLLECT 6 sources (all mandatory)        MINE the week (NEVER opens a browser)
   ├ X (For You + Following)                 ├ raw dumps in 13-archive/news/dumps/
   │   PRIMARY: _collect_x_headless.py       │   (primary input)
   │   (headless Chrome over raw CDP,        ├ 7 dailies from 08-bawaba/daily/
   │    throwaway cloned-cookie profile,     └ WebSearch/WebFetch (≤~10 fetches)
   │    run via uv; @johndoe is X             │
   │    Premium → ~10k reads/day)                 │  weekly_mine.py → department briefs
   │   FALLBACK: Chrome-MCP scroller             │  .runs/weekly-YYYY-WWW/
   ├ Substack (/inbox, 200)                       ▼
   ├ Medium   (/me/following-feed, 30)      Bawaba Weekly magazine (design v3)
   ├ Hacker News (100)                       8 departments: Editor's Letter,
   ├ Reddit (~200 from 18 subs)              Cover Story, Model State, The Lesson,
   └ GitHub Trending (20)                    The Stack, The Workshop, Reading Shelf,
       │                                     Closing Wisdom (+ The Fold scan)
       ▼                                            │
  SCORE (6 axes: teaches·3 + tool·2 +              ▼
   artifact·2 + discussion·1.5 +            08-bawaba/weekly/YYYY-WWW.md
   contrarian·1 + postmortem·2)
   letter grades S/A/B/C; dedup via
   seen_ledger.jsonl (append-only)
       │
       ▼
  PRESENT  present_v5.py emits a SKELETON with
   <CLAUDE_FILL_*> placeholders; Claude fills the
   gem feed (~80-100 gems). X-share band [0.40,0.55]
       │
       ▼
  08-bawaba/daily/YYYY-MM-DD.md
  (raw collection archived to 13-archive/news/dumps/YYYY-MM-DD/)
```

Daily sections (fixed order): News Wire → Hot Topics → Top Shelf → Feed → Wisdom → Deep Dive. Automation runs HEADLESS via `claude -p --chrome`, scheduled on Ubuntu by systemd user timers (`news-daily.timer` 03:00, `news-weekly.timer` Sat 07:00) through `run-news-ubuntu.sh` — migrated off the retired Mac launchd/WezTerm path. See `./15-news-digest.md`.

## Project lifecycle (full)

```
[Idea matures in 09-ideas/ → status: tree]
       │
       │  /ideas graduate
       ▼
05-projects/kitchen/{name}/        (README.md + PRD.md + ARCHITECTURE.md stub)
       │
       │  start coding
       ▼
~/projects/{name}/      +     05-projects/active/{name}/
(code, outside vault)          (non-code work; created on demand)
       │                                │
       │                                │
       └─────────────┬──────────────────┘
                     │  ship
                     ▼
       05-projects/completed/{name}/
       (retrospective + diagrams; type: project-retrospective)
```

3 lifecycle stages (kitchen → active → completed). Current state: kitchen holds 2 (cloud-lab, open-kit); `active/` does not exist on disk (created on demand); completed holds 8 retrospectives. See `./14-work-and-projects.md`.

## Sync architecture — single coordinator (Linux ⇄ Mac over Tailscale SSH)

Adopted 2026-06-13, replacing the old two-writer GitHub-hub model. Authoritative doc: `03-rai/SYNC-ARCHITECTURE.md`.

```
                         ┌──────────────────────┐
                         │   GitHub origin      │
                         │   (off-site backup)  │
                         └──────────▲───────────┘
                                    │  push  (ONLY Linux pushes)
                                    │  step 4
                         ┌──────────┴───────────┐
                         │  LINUX  "pc"         │
                         │  100.64.0.2        │   ← sole COORDINATOR
                         │  user: john      │   ← sole origin writer
                         │  always-on desktop   │   ← sole ChromaDB writer
                         └──────────┬───────────┘
                                    │
        keyless Tailscale SSH       │       keyless Tailscale SSH
        Linux → Mac  (ssh mac)      │       Mac → Linux  (ssh linux)
                                    │
                         ┌──────────▼───────────┐
                         │  MAC                 │
                         │  100.64.0.3       │   ← passive SOURCE + REPLICA
                         │  user: johndoe│  ← never touches GitHub
                         │  no scheduler         │  ← read-only ChromaDB
                         └──────────────────────┘

Coordinator pipeline — run-maintenance-ubuntu.sh
(systemd rai-maintenance.timer @ 04:00 / 10:00 / 16:00 / 22:00, Linux only):

  step 0  origin pull   git fetch origin main + merge --ff-only FETCH_HEAD
                        (was pull --rebase; changed in abc1234 to end the
                         ChromaDB binary-conflict jam)
  step 1  capture_mac   ssh mac "mac-sync.sh commit"  → fetch mac main
                        → merge -X ours mac/main  (Linux wins conflicts;
                         jsonl union via .gitattributes; Mac asleep → skip)
  step 2  merge-collisions  fold durably-backed-up colliders (if any)
  step 3  process-sessions  drain BOTH queues into ChromaDB (Linux = sole writer)
  step 4  git-commit + push  → origin   (the ONLY push anywhere)
  step 5  refresh_mac   ssh mac "mac-sync.sh refresh"  + propagate origin SHA

Mac side — mac-sync.sh (driven by Linux over SSH; no local scheduler):
  commit   git add -A; git reset -- chromadb (drop read-induced drift);
           git commit "wip(mac): churn snapshot <ts>"   (no push, no network)
  refresh  git checkout -- chromadb (discard drift);
           git pull --rebase --autostash linux main   (pulls the 'linux'
           remote over Tailscale SSH, NOT GitHub — Mac's GitHub creds are
           in the Keychain, unreachable from non-interactive SSH)
```

Why ChromaDB is Linux-only: `chromadb/chroma.sqlite3` + `*.bin` are binary; git cannot merge them. The Mac only reads the store for recall, but opening it mutates the bytes — `mac-sync.sh` unstages/discards those changes so they never sync back, and the coordinator merges Mac churn with `-X ours` so Linux's copy always wins. If the Mac is asleep, capture + refresh skip and everything else runs. See `./17-config-and-security.md`.

## Cheatsheet matrix (key paths at a glance)

```
┌────────────────────────────┬─────────────────────────────────────────────────┐
│  WHERE TO FIND             │  PATH                                           │
├────────────────────────────┼─────────────────────────────────────────────────┤
│  Vault root                │  ~/helm/                  │
│  Rai brain                 │  ~/helm/03-rai/           │
│  Algorithm spec            │  03-rai/algorithm/v3.7.0.md                    │
│  Skills                    │  03-rai/skills/{router}/SKILL.md               │
│  Agents                    │  03-rai/agents/{name}.md                       │
│  Hooks (code)              │  03-rai/hooks/*.py                             │
│  Hook wiring (canonical)   │  03-rai/config/settings.json                   │
│  Settings symlink          │  ~/.claude/settings.json → 03-rai/config/...   │
│  John's identity       │  02-ana/identity/                              │
│  Rai's identity            │  03-rai/identity/                              │
│  File memory               │  03-rai/memory/                                │
│  ChromaDB                  │  03-rai/semantic-memory/chromadb/              │
│  Pending sessions          │  03-rai/semantic-memory/pending/               │
│  Sync spec                 │  03-rai/SYNC-ARCHITECTURE.md                   │
│  Templates                 │  12-system/templates/                          │
│  Workflows                 │  11-workflows/                                 │
│  This manual               │  12-system/manual/                             │
│  Archived sessions         │  13-archive/historical-sessions/               │
│  Archived news             │  13-archive/news/{daily,weekly,dumps}/         │
│  Code (outside vault)      │  ~/projects/{name}/                            │
└────────────────────────────┴─────────────────────────────────────────────────┘
```
