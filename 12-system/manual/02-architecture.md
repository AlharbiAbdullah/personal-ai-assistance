# 02 — Architecture

> **Last updated:** 2026-06-14. The live source of truth for the brain's layout is `03-rai/ARCHITECTURE.md` and the per-folder `CLAUDE.md` files; this chapter is a snapshot and points to them. Where ARCHITECTURE.md and the live filesystem diverge (e.g. the retired `algorithm-tracker.py`), the filesystem wins and the divergence is flagged inline.

How the layers of the brain fit together. Where each layer lives. What talks to what.

## The 8 layers (top down)

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
│      Wired in: 03-rai/config/settings.json (via ~/.claude link) │
│      Code in:  03-rai/hooks/*.py  (19 scripts)                  │
└──────────────────────────────┬──────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────┐
│  L6  IDENTITY (auto-loaded context)                             │
│      03-rai/identity/*.md  +  02-ana/identity/*.md              │
│      Loaded by session-start.py at every SessionStart           │
└──────────────────────────────┬──────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────┐
│  L5  ALGORITHM (decision framework)                             │
│      03-rai/algorithm/v3.7.0.md                                 │
│      OBSERVE → THINK → PLAN → BUILD → EXECUTE → VERIFY → LEARN  │
└──────────────────────────────┬──────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────┐
│  L4  SKILLS + AGENTS (capabilities)                             │
│      03-rai/skills/{router}/SKILL.md  +  sub-skills             │
│      03-rai/agents/{name}.md                                    │
└──────────────────────────────┬──────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────┐
│  L3  STATE + WORK (per-session + per-task)                      │
│      03-rai/memory/state/   per-session runtime                 │
│      03-rai/memory/work/    per-task PRD records                │
└──────────────────────────────┬──────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────┐
│  L2  MEMORY (long-term)                                         │
│      03-rai/memory/{learning,relationship,security,ai-calls}/   │
│      03-rai/semantic-memory/{chromadb, pending}/                │
└──────────────────────────────┬──────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────┐
│  L1  VAULT CONTENT (the actual brain)                           │
│      00-13 numbered folders                                     │
└─────────────────────────────────────────────────────────────────┘
```

Reading the diagram: a user prompt enters at L8. Hooks (L7) fire on the events that prompt creates. Identity (L6) shapes the model's worldview. The Algorithm (L5) governs how non-trivial work proceeds. Skills and agents (L4) are the capabilities. State and work (L3) track what is happening now. Memory (L2) preserves what happened across sessions. Vault content (L1) is the substrate everything operates on.

## What each layer does

### L1 — Vault content

The 14 numbered folders. The actual notes, ideas, projects, knowledge, work artifacts. This is what John reads, edits, and refers to. Everything else exists to make L1 better.

Full reference: [01-folder-map.md](./01-folder-map.md).

### L2 — Memory

Two memory systems running in parallel:

| System | Storage | Read by | Written by |
|--------|---------|---------|------------|
| **File memory** | `03-rai/memory/{learning,relationship,security,ai-calls}/` | Hooks, skills, /rai sanity | Hooks (SessionEnd), /ask-model, /gemini |
| **Semantic memory** | `03-rai/semantic-memory/chromadb/` | `session-start.py`, `/recall history` | `/rai process-sessions` (Linux coordinator only) |

File memory is structured (JSONL, dated folders). Fast to read. Used for daily integrity checks, performance metrics, user signal tracking, security events. A newer `ai-calls/` subdir logs external-LLM telemetry written by the `/ask-model` skill.

Semantic memory is vector-based (ChromaDB 1.5.9, SQLite + HNSW indices). Slower to query. Used for "what did I work on last month?" recall, pattern discovery across sessions, continuation detection. The live collection is named `memories` (~734 embeddings, 384-dim cosine, `all-MiniLM-L6-v2`). A second `session_summaries` collection exists but is empty/legacy.

ChromaDB is **single-writer**: the Linux coordinator (`pc`) is the only machine that ever writes the binary store. The Mac reads it for recall only, and any read-induced byte drift is discarded rather than synced. See the cross-machine sync section below and [17-config-and-security.md](./17-config-and-security.md).

Sessions land in `semantic-memory/pending/` at SessionEnd. They sit there until `/rai process-sessions` summarizes them and writes embeddings to ChromaDB — a step that runs only on the Linux coordinator, on a 04/10/16/22:00 schedule.

Full reference: [10-memory-systems.md](./10-memory-systems.md).

### L3 — State and work

Two short-lived storage areas that keep individual sessions and tasks coherent.

| Folder | What lives there | Lifetime |
|--------|------------------|----------|
| `memory/state/` | Per-session runtime: current-work-{uuid}, tab-titles/{uuid}, algorithms/{uuid}, session-names, identity-cache, work.json | Cleaned at SessionEnd; orphans swept at next SessionStart (6h threshold) |
| `memory/work/{slug}/` | Per-task record: META.yaml ledger + nested tasks/{NNN}_{task}/{PRD.md, ISC.json, THREAD.md} | Persisted indefinitely |

State files die. Work files live. The line between them is "did this task produce a deliverable?" — yes means work, no means state.

### L4 — Skills and agents

The two capability surfaces.

| Surface | Invocation | Where it lives |
|---------|------------|----------------|
| **Skill** | `Skill("name")` or `/name` (top-level routers only) | `03-rai/skills/{router}/SKILL.md` (router) or `03-rai/skills/{router}/{sub-skill}.md` (sub-skill) |
| **Agent** | `Task(subagent_type: "name")` | `03-rai/agents/{name}.md` |

Skills are deterministic procedures with named steps. They route based on user intent. Sub-skills are not directly invocable — they are reached via their parent router.

Agents are personas with their own context window. They are spawned for parallelism, isolation, or specialized expertise.

35 top-level skill entries (30 routers + 5 leaves: ask-model, map-updater, project-init, visual-plan, workflow), spanning ~128 sub-skill files. 12 agents (10 specialists + 2 methodology). Claude Code discovers skills by a depth-1 scan of `skills/*/SKILL.md`; sub-skills are reachable only through their router.

Full references: [07-skills-catalog.md](./07-skills-catalog.md), [08-agents-catalog.md](./08-agents-catalog.md).

### L5 — Algorithm

The 7-phase decision framework. Every non-trivial task runs through it. Trivial tasks (greetings, lookups) skip it.

```
OBSERVE → THINK → PLAN → BUILD → EXECUTE → VERIFY → LEARN
```

Effort tier (Standard / Extended / Advanced / Deep / Comprehensive) sets the time budget, ISC count floor, and minimum capabilities to invoke.

The Algorithm writes a PRD to `memory/work/{slug}/PRD.md` as it progresses. The PRD is the system of record.

Full reference: [06-algorithm-and-prd.md](./06-algorithm-and-prd.md).

### L6 — Identity

Two folders, both auto-loaded into every session.

| Folder | Files | Loaded by |
|--------|-------|-----------|
| `03-rai/identity/` | dai-identity.md, ai-steering-rules.md, response-format.md, coding-format.md (4) | session-start.py |
| `02-ana/identity/` | who-i-am, goals, vision, mindset, story, wrong, projects, ideas, contacts, definitions, environment, tech-stack, rai-public (13) | session-start.py |

17 `.md` files total auto-load every session (4 Rai + 13 John). `rai-public.md` (Rai's public-facing self-description) was the most recent addition.

Non-`.md` files (e.g. `security-patterns.yaml`) are NOT auto-loaded. They are runtime config for specific hooks.

Adding context to every session = drop a `.md` in identity/. Removing = move it out.

### L7 — Hooks

Event-driven scripts that the harness fires on Claude Code events. Configured in `03-rai/config/settings.json` (reached via the symlink `~/.claude/settings.json`). Code in `03-rai/hooks/*.py`. There are 19 distinct `.py` hook scripts, wired across 24 invocations (`security-validator.py` is reused on four PreToolUse matchers). The two PostToolUse codemap handlers are shell scripts that live under `03-rai/skills/map-updater/scripts/`, not in `hooks/` — which is why `map-updater` stays a top-level skill.

Six events have hooks wired:

| Event | Hooks (in order) |
|-------|------------------|
| **SessionStart** | session-start.py (chroma + identity), check-version.py |
| **UserPromptSubmit** | rating-capture.py, auto-work-creation.py, session-auto-name.py, update-tab-title.py |
| **PreToolUse** (Bash, Edit, Write, Read) | security-validator.py |
| **PreToolUse** (Task) | agent-execution-guard.py |
| **PreToolUse** (Skill) | skill-guard.py |
| **PreToolUse** (AskUserQuestion) | set-question-tab.py |
| **PostToolUse** (Write) | map-updater/scripts/auto-update-codemap.sh |
| **PostToolUse** (Bash) | map-updater/scripts/codemap-on-bash.sh |
| **PostToolUse** (AskUserQuestion) | question-answered.py |
| **Stop** | stop-orchestrator.py |
| **SessionEnd** | save-memory.py, work-completion-learning.py, session-summary.py, relationship-memory.py, update-counts.py, integrity-check.py, algorithm-scan.py |

Full reference: [09-hooks-reference.md](./09-hooks-reference.md).

### L8 — User intent

The user prompt. Either a trivial request (handled directly) or a non-trivial request (handled via the Algorithm). Where the chain begins.

## Where each layer lives in the file system

```
~/
├── helm/                              ← VAULT ROOT
│   ├── CLAUDE.md                      ← root rules
│   ├── 00-landing/  ... 13-archive/   ← L1 vault content
│   ├── .helm-index/                   ← navigation index (auto)
│   ├── 02-ana/identity/*.md           ← L6 John identity (auto-loaded)
│   ├── 03-rai/                        ← Rai brain
│   │   ├── CLAUDE.md                  ← Rai rules
│   │   ├── ARCHITECTURE.md            ← Rai layout map
│   │   ├── SYNC-ARCHITECTURE.md       ← cross-machine sync spec (NEW)
│   │   ├── identity/                  ← L6 Rai identity (auto-loaded)
│   │   ├── algorithm/v3.7.0.md        ← L5 Algorithm spec (latest → v3.7.0.md)
│   │   ├── skills/                    ← L4 skills (35 entries + map-updater/scripts/)
│   │   ├── agents/                    ← L4 agents (10)
│   │   ├── hooks/                     ← L7 hook code (19 .py + lib/ + scripts/)
│   │   ├── config/                    ← Rai config (settings.json, mcp.json, statusline.sh)
│   │   ├── memory/                    ← L2 file memory + L3 state/work
│   │   │   ├── state/                 ← L3 per-session
│   │   │   ├── work/                  ← L3 per-task
│   │   │   ├── learning/              ← L2 long-term
│   │   │   ├── relationship/          ← L2 long-term
│   │   │   ├── security/              ← L2 long-term
│   │   │   └── ai-calls/              ← L2 external-LLM telemetry (NEW)
│   │   ├── semantic-memory/           ← L2 ChromaDB (collection "memories")
│   │   └── .pai-protected.json        ← secret patterns (pre-commit scanner)
│   └── 12-system/manual/              ← THIS MANUAL
└── .claude/
    └── settings.json                  ← symlink → 03-rai/config/settings.json (L7 hook wiring)
```

## Cross-layer interactions

These are the named flows where layers talk to each other.

### Flow A — SessionStart → Identity load

```
SessionStart event
  └─▶ session-start.py (L7)
        ├─▶ Read 03-rai/identity/*.md (L6 Rai)
        ├─▶ Read 02-ana/identity/*.md (L6 John)
        ├─▶ Read 03-rai/semantic-memory/chromadb/ (L2)
        ├─▶ Sweep memory/state/ for orphans (L3)
        └─▶ Output identity digest to model context
```

### Flow B — User prompt → Algorithm → PRD

```
User prompt (L8)
  └─▶ UserPromptSubmit hooks (L7)
        ├─▶ auto-work-creation.py creates memory/work/{slug}/ (L3)
        └─▶ session-auto-name.py names the session (L3)

  └─▶ Model decides: trivial or Algorithm?
        │
        ├─▶ Trivial: respond directly
        │
        └─▶ Algorithm (L5)
              ├─▶ Voice: "Entering the Algorithm"
              ├─▶ Write PRD stub at memory/work/{slug}/PRD.md (L3)
              ├─▶ OBSERVE → write ISC criteria to PRD
              ├─▶ THINK → refine ISC, premortem
              ├─▶ PLAN → architecture, sequence
              ├─▶ BUILD → invoke selected skills/agents (L4)
              ├─▶ EXECUTE → run, mark criteria done in PRD
              ├─▶ VERIFY → confirm criteria pass
              └─▶ LEARN → reflection log + JSONL append (L2)
```

### Flow C — Tool call → security gate

```
Bash, Edit, Write, Read tool call
  └─▶ PreToolUse: security-validator.py (L7)
        ├─▶ Read security-patterns.yaml (L6 non-loaded)
        ├─▶ Read .pai-protected.json (L1 dotfile)
        └─▶ Decision: allow / block / confirm
        └─▶ Log to memory/security/{YYYY}/{MM}.jsonl (L2)
```

### Flow D — SessionEnd → Memory persistence

```
SessionEnd event
  └─▶ save-memory.py (L7)
        └─▶ Write transcript to semantic-memory/pending/ (L2)
  └─▶ work-completion-learning.py (L7)
        └─▶ Write learning to memory/learning/ (L2)
  └─▶ session-summary.py (L7)
        └─▶ Delete per-session state files (L3)
        └─▶ Prune session-names.json (L3)
  └─▶ relationship-memory.py (L7)
        └─▶ Write daily user signals to memory/relationship/{YYYY-MM}/{date}.md (L2)
  └─▶ update-counts.py (L7)
        └─▶ Recount skills/hooks/ratings/work/learnings, append counts-history.jsonl (L2)
        └─▶ Attempt counts-block write NO-OPS (targets non-existent 03-rai/settings.json)
  └─▶ integrity-check.py (L7)
        └─▶ Verify memory state consistency
  └─▶ algorithm-scan.py (L7)
        └─▶ Analyze algorithm execution, log to memory/state/algorithms/ (L3)
```

### Flow E — /rai process-sessions → ChromaDB (Linux coordinator only)

```
Linux coordinator invokes /rai process-sessions (04/10/16/22:00)
  └─▶ Skill reads semantic-memory/pending/*.json from BOTH machines (L2)
  └─▶ For each pending session:
        ├─▶ Decide if it should be saved (>=4 user messages, or plan mode)
        ├─▶ Auto-infer type (build/explore/debug/planning/brainstorm)
        ├─▶ Auto-infer mood (low/med/high)
        ├─▶ Compute content density score
        ├─▶ Summarize via AI
        ├─▶ Embed and store in ChromaDB collection (L2)
        └─▶ Move JSON to 13-archive/historical-sessions/ (L1)
```

### Flow F — Capture pipeline

```
Manual file drop
  └─▶ 00-landing/ (L1)
  
User: /triage process-landing
  └─▶ Walk each file, decision: promote or delete
        └─▶ If promote: move to 01-inbox/ (L1)

User: /triage process-inbox
  └─▶ For each file in 01-inbox/:
        ├─▶ Read 02-ana/identity/{goals,who-i-am}.md (L6)
        ├─▶ Apply research template (What/Why-care/Why-matters/Rating)
        ├─▶ Determine destination
        └─▶ Move to destination folder (07/06/10/09/05/04) (L1)
```

### Flow G — Idea pipeline

```
Idea captured
  └─▶ /ideas start-seed → write 09-ideas/{name}.md with status: seed (L1)

Idea matures
  └─▶ /ideas promote → frontmatter status: seed → plant → tree (L1)

Idea ready
  └─▶ /ideas graduate
        ├─▶ Update status: graduated (L1)
        ├─▶ Create 05-projects/kitchen/{name}/ (L1)
        ├─▶ Write initial PRD to kitchen (L1)
        └─▶ Add wiki-link to spawned: in source idea (L1)

Project starts
  └─▶ Create ~/projects/{name}/ (outside vault)
  └─▶ Move planning docs alongside code
  └─▶ Create 05-projects/active/{name}/ for non-code work (L1)

Project completes
  └─▶ Create 05-projects/completed/{name}/ with retrospective (L1)
```

## Cross-file relationships (verbatim from ARCHITECTURE.md)

> **SessionStart** → `session-start.py` reads `identity/*` (Rai persona) plus `~/helm/02-ana/` anchors (`identity/{who-i-am,vision,mindset,goals}.md`, `ideas.md`, `contacts.md`, `environment.md`, `definitions.md`, `tech-stack.md`), writes identity digest to stdout
>
> **Pre-commit** → `security-validator.py` scans Bash `git commit` commands, calls `protected_scan.py` which reads `.pai-protected.json`
>
> **SessionEnd** → `save-memory.py` dumps transcript to `semantic-memory/pending/`
>
> **Skill-invoked** → `/process-sessions` calls `hooks/scripts/store_to_chromadb.py` to drain `pending/` into `chromadb/`
>
> **Self-healing** → SessionStart sweep (`hooks/lib/state_sweep.py`) clears orphan `memory/state/*` files from crashed sessions (6h threshold)
>
> **Algorithm tracking** → `algorithm-tracker.py` writes per-session phase history to `memory/state/algorithms/{uuid}.json`

Correction: the per-PostToolUse `algorithm-tracker.py` has been retired. The live writer of `memory/state/algorithms/{uuid}.json` is `algorithm-scan.py`, a SessionEnd hook. ARCHITECTURE.md and `state/README.md` still name the dead tracker — doc-rot to ignore.

## Cross-machine sync architecture

The eight layers above describe one machine. In practice the brain runs on two: a Linux desktop and a Mac laptop, kept in lockstep. As of 2026-06-13 the topology is **single-coordinator**, not peer-to-peer. The authoritative spec is `03-rai/SYNC-ARCHITECTURE.md`; the full operational detail lives in [17-config-and-security.md](./17-config-and-security.md). This is a summary so the architecture reads complete.

### Topology

| Role | Machine | What it does |
|------|---------|--------------|
| **Coordinator** | Linux (`pc`, Tailscale `100.64.0.2`, user `john`) | Sole maintenance runner, the ONLY machine that writes `origin` (GitHub), and the sole ChromaDB writer. Always-on. |
| **Replica** | Mac (`100.64.0.3`, user `johndoe`) | Passive source + replica. Refreshes from Linux over Tailscale SSH. Runs no scheduler of its own. Never touches GitHub. |

GitHub `origin` is Linux's off-site backup only. The two machines talk over **two keyless Tailscale SSH channels** (`ssh mac` from Linux, `ssh linux` from Mac), with git remotes `mac:helm` and `linux:helm`.

### The coordinator pipeline

A systemd user timer (`rai-maintenance.timer`) fires on Linux at 04:00 / 10:00 / 16:00 / 22:00 and runs `03-rai/skills/rai/scheduled/run-maintenance-ubuntu.sh`:

```
0. origin pull   — git fetch origin main + merge --ff-only FETCH_HEAD
1. capture_mac   — ssh mac mac-sync.sh commit → fetch mac → merge -X ours (Linux wins)
2. merge-collisions — fold durably-backed-up collider files, strip markers (claude -p)
3. process-sessions — drain BOTH machines' pending/ into ChromaDB (Linux = sole writer)
4. git-commit+push — group churn into commits, push to origin (the ONLY GitHub push)
5. refresh_mac   — ssh mac mac-sync.sh refresh → fast-forward Mac, propagate origin SHA
```

The Mac side (`mac-sync.sh`) has just two subcommands, both driven by Linux over SSH: `commit` (snapshot local churn into a `wip(mac)` commit, no network) and `refresh` (pull the `linux` remote over Tailscale SSH — never GitHub, whose creds are unreachable from a non-interactive SSH session).

### Why ChromaDB is Linux-only

`03-rai/semantic-memory/chromadb/` is a binary store (`chroma.sqlite3` + `*.bin`) that git cannot merge. Merely *opening* it to read mutates the bytes. So Linux is its sole writer; the Mac reads it for recall and then **discards** the read-induced drift — `mac-sync.sh` unstages chromadb on `commit` and `git checkout -- chromadb` before `refresh`, and the coordinator merges Mac churn with `-X ours` so Linux's copy always wins. Append-only `memory/**/*.jsonl` logs are reconciled by a `.gitattributes` `merge=union` rule so no log entry is ever dropped.

The 2026-06-14 fix (`abc1234`) changed step 0 from `pull --rebase --autostash` to `fetch` + `merge --ff-only`. The rebase form replayed unpushed `wip(mac)` churn onto origin and choked on "Cannot merge binary files" in ChromaDB, stranding half-rebases that poisoned every following run. ff-only is a steady-state no-op and fails cleanly on the diverged-origin anomaly.

This is why the "deliberately does not have → no remote sync" entry below now carries a caveat: there IS cross-machine sync, but it sits at the ops layer over Tailscale SSH, outside the brain's internal design.

## Design principles behind the architecture

The following are not stated as rules in any single file, but emerge from how the system was built. They are useful to keep in mind when extending the brain.

### 1. Filesystem is the database

Every piece of state, every record, every config is a file. There is no SQL database, no daemon, no service. The only persistent service is ChromaDB (which is also just a SQLite file). This makes the brain debuggable with `ls`, `cat`, `grep`, and `git log`.

### 2. Hooks are the only side-channel

Anything that happens "automatically" within a session runs through a hook. There are no background daemons inside the brain. The one OS-level exception is the Linux coordinator's systemd timer, which drives scheduled vault maintenance and the news digest from outside the brain's layers. When you wonder "what causes X to happen," the answer is "the user did it," "a hook fired," or "the coordinator's scheduled run did it." No mystery.

### 3. Every layer can be read in isolation

You can understand identity without understanding skills. You can understand skills without understanding hooks. You can understand hooks without understanding the algorithm. The layers compose; they do not entangle.

### 4. Identity is the universal context

Auto-loaded identity is the universal cross-layer context. It is how Rai knows who John is, what tone to take, what coding rules apply, what security patterns matter. Putting something in identity/ makes it always-on. Removing it makes it gone.

### 5. The Algorithm is opt-in for the AI, not for the user

The user does not invoke the Algorithm. Rai decides when to enter it. The signal is task complexity, not user request. If the user asks for a one-line edit, no Algorithm. If the user asks for a refactor, the Algorithm runs.

### 6. Delete over archive

Stated explicitly in CLAUDE.md. Restated here because it has architectural impact: there is no "archive" folder for stale text content. If a file is no longer live, it is deleted. Git log is the archive. This keeps the vault clean and queryable. Two standing exceptions (John-approved) are kept indefinitely under `13-archive/`: `news/` (prior digests + raw dumps) and `learning/` (retired curricula). Session JSONs are the third thing kept (principle 7).

### 7. Sessions are the unit of historical record

Session JSONs in `13-archive/historical-sessions/` are the only thing kept indefinitely besides notes. They are cheap. They are auditable. They are the basis of relationship memory and learning logs.

## Layer-by-layer extension guide

Adding to each layer follows a different procedure. Here is the cheat sheet.

| To add | Procedure | Reference |
|--------|-----------|-----------|
| A new top-level folder (00-13) | This is structural. Don't. Place content in an existing folder. If new pipeline emerges, extend `_workflows/` first. | — |
| A new note type | Add a template to `12-system/templates/`. Update CLAUDE.md inventory. | [11-templates-and-conventions.md](./11-templates-and-conventions.md) |
| A new identity fact | Add a `.md` to `02-ana/identity/` (John) or `03-rai/identity/` (Rai). Auto-loads next session. | — |
| A new skill | Run `/rai create-skill`. Place in correct router. Update `skills/MANIFEST.md`. | [07-skills-catalog.md](./07-skills-catalog.md) |
| A new agent | Add `.md` to `03-rai/agents/` with frontmatter (`name`, `description`, `model`, `permissions.allow`). Update `agents/MANIFEST.md`. | [08-agents-catalog.md](./08-agents-catalog.md) |
| A new hook | Add `.py` to `03-rai/hooks/`. Wire it in `03-rai/config/settings.json`. | [09-hooks-reference.md](./09-hooks-reference.md) |
| A new workflow | Add `NN-name.md` to `11-workflows/` with the next number (8 exist, 01-08). Update CLAUDE.md (sole guidance — the folder README was removed). | [16-workflows.md](./16-workflows.md) |
| A new permission | Edit `03-rai/config/settings.json` `permissions.allow` array (machine-local-only allows go in `~/.claude/settings.local.json`). | [17-config-and-security.md](./17-config-and-security.md) |
| A new secret pattern | Edit `03-rai/.pai-protected.json`. | [17-config-and-security.md](./17-config-and-security.md) |
| A new MOC topic | Add a Topic Note to `10-knowledge/{domain}/` and a MOC entry to `_mocs/`. | [12-knowledge-system.md](./12-knowledge-system.md) |

## What the architecture deliberately does not have

- No web UI. The vault is read in Obsidian and operated from Claude Code.
- No daemon. No services running between sessions.
- No queue worker. Pending sessions wait until `/rai process-sessions` is invoked (now driven by the Linux coordinator's scheduled maintenance, not by hand).
- No cron *inside the brain*. Recurring work in a session is handled by `/loop` or `/schedule` (Claude Code-native). Note the caveat: vault maintenance and the news digest ARE scheduled, but by an OS-level systemd timer on the Linux coordinator, outside the brain's own layers.
- No remote sync *in the brain layer*. The brain's internal design is local-only. Caveat: at the ops layer there is now a single-coordinator Tailscale-SSH sync between the Linux coordinator and the Mac replica (see the cross-machine sync section above and [17-config-and-security.md](./17-config-and-security.md)). Git remains the external dependency for backup, written only by Linux.
- No external authentication. The brain trusts the local user.
- No multi-user support. One principal (John). One AI (Rai).

These are deliberate. The brain is for one person. Adding any of the above expands surface area for very little gain. The two-machine sync is the one concession — and it is engineered to keep a single authoritative writer, so the one-principal model holds.
