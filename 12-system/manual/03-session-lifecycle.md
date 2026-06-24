# 03 — Session Lifecycle

> Last updated: 2026-06-14. Live source of truth for hook wiring is `~/helm/03-rai/config/settings.json` (the canonical, git-tracked settings file, reached via the symlink `~/.claude/settings.json`). When this chapter and that file disagree, the file wins.

What happens from the moment Claude Code starts a session to the moment it ends. Every hook, every state file, every artifact. Trace this chapter and you understand the operating loop.

There are **19 distinct hook Python scripts** in `~/helm/03-rai/hooks/`, wired into **24 invocations** across six events (`security-validator.py` is reused across four PreToolUse matchers; two PostToolUse entries are shell scripts, not Python). All 19 scripts are wired. Every hook is path-portable: as of the 2026-06-09 cross-platform fix, every command in `settings.json` uses `$HOME/helm/03-rai/...` (the shell expands `$HOME`), so the same settings file works on both John's Mac and the Linux coordinator. The `env` block is now empty (no `PAI_DIR`); hooks self-resolve to `$HOME/helm/03-rai` via `lib/paths.py`.

## High-level timeline

```
TIME ─────────────────────────────────────────────────────────────────────────▶

[SessionStart]                                                       [SessionEnd]
     │                                                                     │
     ▼                                                                     ▼
┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐    ┌────────────┐
│  Identity  │  │   User     │  │   Tool     │  │   Stop     │    │   Memory   │
│  Auto-Load │─▶│   Prompt   │─▶│   Calls    │─▶│  Signal    │───▶│ Persistence│
│  + Sweep   │  │   Hooks    │  │ + Guards   │  │            │    │   + Logs   │
└────────────┘  └────────────┘  └────────────┘  └────────────┘    └────────────┘
     │                │                │              │                  │
     ▼                ▼                ▼              ▼                  ▼
session-start.py  rating-capture   security-       stop-           save-memory
(via py-chroma)   auto-work-       validator       orchestrator    work-completion-
check-version     creation         agent-                          learning
                  session-auto-    execution-                      session-summary
                  name             guard                           relationship-memory
                  update-tab-      skill-guard                     update-counts
                  title            set-question-                   integrity-check
                                   tab                             algorithm-scan
                                   PostToolUse:
                                   auto-update-
                                   codemap.sh
                                   codemap-on-
                                   bash.sh
                                   question-
                                   answered
```

`security-validator.py` is wired to four PreToolUse matchers (Bash, Edit, Write, Read). The two codemap PostToolUse entries are shell scripts under `~/helm/03-rai/skills/map-updater/scripts/`, and they are inert inside the helm vault (no `.codemap/` directory exists here — they only do anything inside a code project).

## Phase 1 — SessionStart

When Claude Code spawns a new session in the helm directory, two hook chains fire.

### Hook chain A — session-start.py

**Command:** `$HOME/helm/03-rai/semantic-memory/scripts/py-chroma.sh $HOME/helm/03-rai/hooks/session-start.py`
**Path:** `~/helm/03-rai/hooks/session-start.py`
**Wrapped by:** `~/helm/03-rai/semantic-memory/scripts/py-chroma.sh` — `exec uv run --quiet --python 3.12 --with chromadb python3 "$@"`. This wrapper exists because the system `python3` (3.9 on Mac, 3.14 on the Linux box) lacks `chromadb`, and chromadb wheels target 3.12. This is the **only** hook that touches ChromaDB.
**Timeout budget:** SIGALRM 8 seconds. On timeout it prints "Rai identity load timed out (8s)" and exits 0.

What it does (in order):

1. **State sweep** — `_sweep_orphans_safe()` → `lib/state_sweep.sweep_orphans()`. Walks `memory/state/` for orphaned per-session files (`current-work-*.json`, `tab-titles/*.json`, `algorithms/*.json`) and `session-names.json` entries whose session has had no state-file activity in the last 6 hours (`STALE_HOURS=6`). Deletes them. The current session is always kept. This handles crashed sessions that did not run SessionEnd.
2. **Identity load** — reads every `.md` file (sorted) in:
   - `~/helm/03-rai/identity/` — 4 auto-loaded files (`ai-steering-rules.md`, `coding-format.md`, `dai-identity.md`, `response-format.md`). `security-patterns.yaml` is intentionally skipped (it is read only by `security-validator.py`).
   - `~/helm/02-ana/identity/` — 13 auto-loaded files.
   - Caches the digest at `memory/state/identity-cache.json` (mtime-validated). The cache is valid only if its `max_mtime` is at least the sources' max mtime AND the file list matches; output is tagged `cached` or `fresh`.
3. **Index + codemap append** — appends `.helm-index/helm-index.md` (if ≤20 KB) as "## Helm Index", then walks up from CWD (plus up to 3 parents) for a `.codemap/codemap.md` (if ≤20 KB) as "## Codemap". The helm vault has no `.codemap/`, so that section is empty unless the session starts inside a code project.
4. **ChromaDB read** — `chromadb.PersistentClient` opens `semantic-memory/chromadb/`, collection `"memories"`, sorted by `meta.date` descending. Scope depends on CWD via `in_brain_vault(cwd)`:
   - Inside `~/helm/`: **full** memory scope (full doc text, all dates).
   - Elsewhere: last **7** rolling days only, each truncated to 200 chars.
5. **Output** — prints `=== Rai Identity Loaded (cached|fresh) ===` … `=== End Rai Identity ===` to stdout. Claude Code injects it into the model context.
6. **SKILL.md frontmatter validation** (added 2026-05-13) — `_validate_skills()` regex-checks every `skills/<name>/SKILL.md` for a `---` frontmatter block carrying `name:` and `description:` (no PyYAML dependency). Malformed skills are printed and counted. This was added after a "skills not loading" outage where `project-init` shipped with no frontmatter.
7. **Status line** — final stderr line: `[rai] memories=N identity=cached|fresh|none [orphans_swept=N] [pending=N [WARN: run /process-sessions]] [skills_bad=N]`. The pending-warn threshold is **20** (`PENDING_WARN`): once ≥20 session JSONs sit in `semantic-memory/pending/`, the footer nags you to run `/rai process-sessions`.

If anything fails: log to stderr, continue. Never hard-fail SessionStart.

**Known live failure mode:** on a fresh box where the `memories` collection does not exist yet, `load_memories` raises `NotFoundError: Collection [memories] does not exist`. It is handled gracefully (returns `[], 0`). Non-fatal.

**Cost:** the in-process Python body runs p50 ≈ 559 ms, but the real wall time is higher because the `uv`/chromadb cold-start is not captured by the timer. This is the single heaviest hook.

### Hook chain B — check-version.py

**Command:** `python3 $HOME/helm/03-rai/hooks/check-version.py`
**Path:** `~/helm/03-rai/hooks/check-version.py`
**Timeout budget:** SIGALRM 5 seconds.

Compares the installed Claude Code version (`claude --version`, 3s timeout) against the latest published version (`npm view @anthropic-ai/claude-code version`, 5s timeout). If they differ, prints `Claude Code update available: X -> Y...` to stderr. Does not block the session. Exits immediately if `is_subagent` is set in the stdin JSON.

**Cost:** p50 ≈ 897 ms — the second-heaviest hook, dominated by the `npm view` network call. Both SessionStart hooks run only at startup, so nothing in the prompt/tool hot path inherits this latency.

### What gets created

SessionStart does not write to memory by default. The `identity-cache.json` file is rewritten only if source identity files have a newer mtime; the state sweep may delete orphan files. No ChromaDB writes occur at SessionStart — it is read-only against the vector store.

## Phase 2 — User prompt arrives

The user types a message. Before the model sees it, four hooks fire in order.

All four UserPromptSubmit hooks run under `python3`, carry a 5-second SIGALRM, and exit 0 on error.

### Hook 1 — rating-capture.py

**Path:** `~/helm/03-rai/hooks/rating-capture.py`
**Event:** UserPromptSubmit.
**Cost:** ~0 ms.

Scans the prompt for an explicit 1-10 rating on a line (`RATING_RE`), rejecting false positives — counts, ordinals, units, decimals, times (`FALSE_POSITIVE_RE`). Skips prompts longer than 200 chars. If found, appends to `memory/learning/signals/ratings.jsonl` with timestamp and context. A score below 6 also writes `memory/learning/system/YYYY-MM/low-rating-{score}-{ts}.json` for follow-up.

### Hook 2 — auto-work-creation.py

**Path:** `~/helm/03-rai/hooks/auto-work-creation.py`
**Event:** UserPromptSubmit.
**Cost:** ~0.3 ms.

`classify_prompt()` sorts the prompt into conversational | work | continuation. It creates a work directory **only** on a fresh "work" prompt (when no current-work pointer exists yet). When it fires:

1. Generates a slug and builds `memory/work/{YYYYMMDD_HHMMSS}_{slug}/` — note the timestamp uses **underscores** (`YYYYMMDD_HHMMSS`), which is the on-disk convention even though the Algorithm spec writes dashes.
2. Inside it: `META.yaml` (the 6-field hook-written ledger — `id`, `title`, `session_id`, `created_at`, `status`, `completed_at`), a `tasks/` dir, a `scratch/` dir, and a `tasks/current` symlink.
3. The first task dir `tasks/001_{slug}/` gets `ISC.json`, `THREAD.md`, and a `PRD.md` (from `lib/prd_template`, Algorithm v3.7.0 schema).
4. Writes both `memory/state/current-work-{uuid}.json` (scoped) and the legacy `memory/state/current-work.json`.

This pre-creates the nested work layout so the Algorithm can immediately drop a PRD without doing setup. In practice the hook-written `META.yaml` is the authoritative status marker; PRDs are rarely populated to the full spec frontmatter (see [06-algorithm-and-prd.md](./06-algorithm-and-prd.md) for the spec-vs-reality drift).

### Hook 3 — session-auto-name.py

**Path:** `~/helm/03-rai/hooks/session-auto-name.py`
**Event:** UserPromptSubmit.
**Cost:** ~0.2 ms.

First prompt only (idempotent per session). `short_name()` (from `lib/name_extraction`) derives a 2-3 word, noise-filtered name from the first user prompt. Writes to `memory/state/session-names.json` keyed by session UUID and echoes the name to stderr.

### Hook 4 — update-tab-title.py

**Path:** `~/helm/03-rai/hooks/update-tab-title.py`
**Event:** UserPromptSubmit.
**Cost:** ~1.3 ms.

Calls `set_tab_state("working", session_id, "{first 4 words}")` via `lib/tab_setter`, setting the terminal tab title to `Working: {first 4 words}`. Tab control is WezTerm-specific (OSC escape + `wezterm cli set-tab-title` fallback). Since the Mac moved to Ghostty (2026-06-10), the OSC title sequence still works but the `wezterm cli` fallback is a no-op. Title state persists at `memory/state/tab-titles/{uuid}.json`.

## Phase 3 — Model decides: trivial or Algorithm?

This is a model-internal decision, not a hook. The model reads the user prompt, considers the loaded identity rules (especially `ai-steering-rules.md` and the Algorithm spec injected via `03-rai/CLAUDE.md`), and decides:

- **Trivial** (greeting, lookup, single-question, simple-yes/no): respond directly. Skip the Algorithm.
- **Non-trivial** (task with deliverable, code change, research, planning): enter the Algorithm.

The Algorithm (spec v3.7.0, unchanged) has 7 working phases: OBSERVE → THINK → PLAN → BUILD → EXECUTE → VERIFY → LEARN. The hook-level state machine in `lib/algorithm_state.py` bookends these with IDLE and COMPLETE (9 states total). Each phase transition by the primary agent fires a voice announcement (curl POST to `http://localhost:8888/notify`; subagents must never call it) and updates the PRD. Five effort tiers gate the work (Standard / Extended / Advanced / Deep / Comprehensive). Full Algorithm flow in [06-algorithm-and-prd.md](./06-algorithm-and-prd.md).

## Phase 4 — Tool calls during the session

Every tool call goes through PreToolUse and PostToolUse hooks. Different matchers wire different hooks.

### PreToolUse hooks

| Matcher | Hook | What it does |
|---------|------|--------------|
| Bash | `security-validator.py` | Scans command for blocked/confirm/alert patterns. Pre-commit secret scan on `git commit`. May block (exit 2), ask, or pass. Fails OPEN. |
| Edit | `security-validator.py` | Same engine, path-mode: blocks `zeroAccess`, blocks Write/Edit on `readOnly`, asks on `confirmWrite`. |
| Write | `security-validator.py` | Same — checks the target path against protected-path levels. |
| Read | `security-validator.py` | Same — blocks reads of `zeroAccess` paths (ssh/aws/gnupg/credentials globs). |
| Task | `agent-execution-guard.py` | **Advisory only — never blocks.** Suggests `run_in_background: true` on non-fast Task spawns. Passes silently if `run_in_background`, `model=="haiku"`, `subagent_type=="Explore"`, or the prompt contains `"Timing: FAST"`. Does NOT validate agent existence, read frontmatter, or enforce permissions. |
| Skill | `skill-guard.py` | Blocks false-positive skill invocations. `BLOCKED_SKILLS = {"keybindings-help"}` — that skill is first in the list and false-fires on the Algorithm's aggressive BLOCKING-REQUIREMENT language. |
| AskUserQuestion | `set-question-tab.py` | Sets the tab title to a question/"Awaiting input" state, saving the previous title for restore. |

### PostToolUse hooks

| Matcher | Hook | What it does |
|---------|------|--------------|
| Write | `skills/map-updater/scripts/auto-update-codemap.sh` | No-op unless a `.codemap/` dir exists at the git root; else prints a `[CODEMAP]` reminder. Inert in the helm vault (no `.codemap/` here). |
| Bash | `skills/map-updater/scripts/codemap-on-bash.sh` | Same `.codemap/` gate; fires only for `rm`/`rmdir`/`mkdir`/`mv` commands. Code projects only. |
| AskUserQuestion | `question-answered.py` | Restores the tab from the question state back to working using `previous_title`. |

Note: there is no longer any per-tool Algorithm hook. The old per-PostToolUse `algorithm-tracker.py` was retired and replaced by the single SessionEnd `algorithm-scan.py`.

### State files updated during the session

| File | Updated by | Contents |
|------|------------|----------|
| `memory/state/current-work-{uuid}.json` + legacy `current-work.json` | auto-work-creation | Pointer to active task |
| `memory/state/session-names.json` | session-auto-name, session-summary, state_sweep | UUID → name map |
| `memory/state/tab-titles/{uuid}.json` | tab_setter (update-tab-title, set-question-tab) | Tab title state + previous_title |
| `memory/state/algorithms/{uuid}.json` | `lib/algorithm_state` (via stop-orchestrator, algorithm-scan) | Phase/criteria/agents per session |
| `memory/work/{slug}/META.yaml` | auto-work-creation (hook-written ledger) | id, title, session_id, created_at, status, completed_at |
| `memory/work/{slug}/tasks/001_*/PRD.md` + `ISC.json` + `THREAD.md` | The model directly via Edit/Write | Full task record |

### Security validator log

Every tool call that goes through `security-validator.py` results in a JSONL entry at:

```
03-rai/memory/security/{YYYY}/{MM}/security-{YYYYMMDD}.jsonl
```

Records: command, decision (allow/block/ask/alert), pattern matched, timestamp. The pattern set cascades: `identity/security-patterns.yaml` (user, v1.0) → `security-patterns.example.yaml` (fallback) → a hardcoded minimal dict if no PyYAML. `security-validator.py` is by far the most-invoked hook (~1500 calls per session window) and the cheapest at ~2.6 ms average.

## Phase 5 — Stop signal

Claude Code emits a Stop signal when the user interrupts or the session is paused. One hook fires.

### stop-orchestrator.py

**Path:** `~/helm/03-rai/hooks/stop-orchestrator.py`
**Event:** Stop.
**Timeout budget:** SIGALRM 10 seconds.

Does a single transcript parse, then runs three isolated handlers (each failure is isolated so one crash does not block the others):

1. `handle_tab_reset` → `set_tab_state("completed", session_id, response[:50])` — flips the tab to a Done state.
2. `handle_algorithm_enrichment` → if the algorithm phase is not IDLE/COMPLETE, calls `algorithm_end` to close out the algorithm state file.
3. `handle_notification` → if `current-work-{session_id}.json` shows ≥3 `files_changed`, fires `notify("task_complete", ...)`.

Latency is ~7 ms average.

## Phase 6 — SessionEnd

When the session truly ends (the user closes Claude Code or starts a new session), seven hooks fire in order.

### Hook 1 — save-memory.py

**Path:** `~/helm/03-rai/hooks/save-memory.py`
**Cost:** ~20 ms average.
**No AI calls.** Pure JSON storage.

What it does:

1. **Skip gate first** — if the session has fewer than 4 human messages, it does nothing. Trivial chats never reach the pending queue.
2. Extracts session metadata: cwd, context (via `context_mapping.json`), project name (resolved from `.git` remote / `pyproject.toml` / `package.json` / folder name), duration (first vs last timestamp), tool counts, and modified files (from Edit/Write/NotebookEdit calls).
3. Writes the full transcript plus metadata to `semantic-memory/pending/session_{YYYYMMDD_HHMMSS}.json`. A debug log goes to `~/.claude/logs/save-memory-debug.log`.

This file sits in `pending/` until `/rai process-sessions` (Linux coordinator only) summarizes and ingests it into ChromaDB.

### Hook 2 — work-completion-learning.py

**Path:** `~/helm/03-rai/hooks/work-completion-learning.py`
**Cost:** ~0.1 ms.

Reads `memory/state/current-work.json` (the legacy pointer only). Treats the work as "significant" if ≥3 files changed OR ≥1 task completed OR status is completed. If significant, it categorizes the work via `ALGORITHM_KEYWORDS` (22 keywords) into `algorithm` vs `system`, then writes a learning JSON to `memory/learning/{algorithm|system}/{YYYY-MM}/work-{ts}.json`. Finally it **deletes** `current-work.json`.

### Hook 3 — session-summary.py

**Path:** `~/helm/03-rai/hooks/session-summary.py`
**Cost:** ~1.3 ms.

The cleanup pass. Finds the scoped-or-legacy state file, then:

1. Marks the work's `META.yaml` and any v3.7.0 `tasks/*/PRD.md` frontmatter as `status: COMPLETED` with a `completed_at` stamp.
2. Deletes per-session state files for this UUID:
   - `memory/state/current-work-{uuid}.json` (and legacy `current-work.json`)
   - `memory/state/tab-titles/{uuid}.json`
   - `memory/state/algorithms/{uuid}.json`
3. Removes this session's entry from `memory/state/session-names.json`.

It skips the OSC tab write at session end (saving ~200-600 ms). State files die here.

### Hook 4 — relationship-memory.py

**Path:** `~/helm/03-rai/hooks/relationship-memory.py`
**Cost:** ~6.6 ms.

Classifies each user message into one of three tags using regex sets:

- `O` — preference (5 regex).
- `W` — world fact (4 regex).
- `B` — biographical (4 regex).

Dedups by 80-char prefix, caps at 30 signals per session, and appends to `memory/relationship/{YYYY-MM}/{YYYY-MM-DD}.md`. Human-readable; one bucket per day.

### Hook 5 — update-counts.py

**Path:** `~/helm/03-rai/hooks/update-counts.py`
**Cost:** ~3.8 ms.

Recounts the brain inventory: skills (dirs with a `SKILL.md`), hooks (`*.py` glob), ratings (lines in `ratings.jsonl`), work (subdirs), learnings (`.json` under `learning/`). It then appends a row to `memory/learning/system/counts-history.jsonl`.

**KNOWN BUG:** it tries to write the live counts via `lib/paths.get_settings_path()`, which returns `03-rai/settings.json` — **a path that does not exist** (the real file is `03-rai/config/settings.json`). So the `counts` block in the canonical settings file never refreshes; it is frozen at its 2026-04-18 values (`skills: 66, hooks: 22, ratings: 4, work: 27, learnings: 16`). Those numbers are stale: there are really 19 hook scripts and 35 top-level skill entries today. The append-only `counts-history.jsonl` is the only place the recount actually lands.

### Hook 6 — integrity-check.py

**Path:** `~/helm/03-rai/hooks/integrity-check.py`
**Cost:** ~5.6 ms.

`extract_modified_files(transcript)` collects files touched during the session, keeps those under the Rai root that are NOT in the exclude set (`memory/work`, `memory/learning`, `memory/state`, `scratch` — overridable via `settings.integrityCheck.exclude`), and writes a change record to `memory/learning/system/integrity/change-{ts}.json`. Records older than 30 days (by mtime) are rotated out. This is the tripwire that surfaces edits to Rai's own system files.

### Hook 7 — algorithm-scan.py

**Path:** `~/helm/03-rai/hooks/algorithm-scan.py`
**Cost:** ~11.5 ms. SIGALRM 10 seconds.

Replaces the retired per-PostToolUse `algorithm-tracker.py`. Does a single transcript walk:

- On `TaskCreate`: extracts `ISC-[CA]\d+` criteria and phase hints.
- On `Task`: records the agent spawn.
- Reads the final assistant text for a phase hint, then calls `algorithm_end`.

Writes `memory/state/algorithms/{uuid}.json` (rework_cycles, effort_level, criteria/anti_criteria, agents_spawned). Note ordering: `session-summary.py` (hook 3) deletes this file earlier in the chain, so on a normal SessionEnd the freshly written algorithm artifact is the post-summary record.

## Phase 7 — Post-SessionEnd processing

The session is over. Nothing more runs automatically. But two things wait in the wings:

### Pending sessions in semantic-memory/pending/

Each session JSON sits there until manually drained. The drain command:

```
/rai process-sessions
```

This skill:

1. Reads each `pending/session_*.json`.
2. Auto-infers session type (build / explore / debug / planning / brainstorm).
3. Auto-infers mood (low / med / high) from rating + tone.
4. Computes a content-density score (session duration is deliberately ignored).
5. Applies the save gate: plan-mode sessions always save; non-plan sessions save with ≥4 user messages; below that they are archived without a ChromaDB write.
6. Summarizes the rest via AI.
7. Embeds and stores in ChromaDB (collection `memories`, all-MiniLM-L6-v2, 384-dim, cosine) via `hooks/scripts/store_to_chromadb.py`, keyed by session UUID.
8. Moves the JSON to `13-archive/historical-sessions/`.

**Single-writer rule:** ChromaDB has exactly one writer — the Linux coordinator box ("pc"). `/rai process-sessions` runs only there, on the maintenance cadence (04/10/16/22:00). The Mac is a passive replica over Tailscale SSH and never writes to ChromaDB or to GitHub origin; it discards any read-induced ChromaDB drift. SessionEnd's `save-memory.py` only drops a file into `pending/` on whichever machine ran the session; the drain into the vector store is a separate Linux-only step. Authoritative doc: `~/helm/03-rai/SYNC-ARCHITECTURE.md`.

Run cadence: scheduled on the coordinator; also invoked manually when memory of past work is needed.

### Recall via /recall history

Once sessions are in ChromaDB, they are searchable:

```
/recall history "what did I work on last week?"
/recall history "have I tried Solution X for this problem before?"
```

Returns: matching session summaries, links to full transcripts, cross-session patterns.

## State files: what dies, what lives

| File | Lives |
|------|-------|
| `memory/state/current-work-{uuid}.json` | Dies at SessionEnd |
| `memory/state/current-work.json` (legacy) | Dies at SessionEnd |
| `memory/state/tab-titles/{uuid}.json` | Dies at SessionEnd |
| `memory/state/algorithms/{uuid}.json` | Dies at SessionEnd (kept if useful per algorithm-scan) |
| `memory/state/session-names.json` (entry) | Entry pruned at SessionEnd |
| `memory/state/work.json` | Lives — master index, rebuilt by `lib/work_index` (manual/`/rai` runs, not a SessionEnd hook) |
| `memory/state/identity-cache.json` | Lives — invalidated on identity mtime change |
| `memory/work/{slug}/` | Lives indefinitely |
| `memory/learning/**` | Lives (30-day rotation for some logs) |
| `memory/relationship/{YYYY-MM}/*.md` | Lives indefinitely |
| `memory/security/{YYYY}/{MM}/security-{YYYYMMDD}.jsonl` | Lives indefinitely |
| `semantic-memory/pending/session_*.json` | Lives until drained by /rai process-sessions |
| `semantic-memory/chromadb/` | Lives forever |

## Crash recovery

If a session crashes (Claude Code dies, SIGKILL, OS restart) before SessionEnd hooks fire, state files for that UUID are orphaned. The next SessionStart sweep cleans them:

1. `lib/state_sweep.py` walks `memory/state/`.
2. For each per-UUID file (`current-work-{uuid}`, `tab-titles/{uuid}`, `algorithms/{uuid}`), checks mtime.
3. If mtime is older than 6 hours, the file is deleted.
4. `session-names.json` ghosts (UUIDs with no live session) are pruned.

Threshold is 6 hours because long-running sessions can sit idle (e.g. John comes back the next morning to continue). Anything older than 6 hours is assumed dead.

## Hook execution order — full reference

```
SessionStart (2)
  ├── session-start.py     (via py-chroma.sh: uv + chromadb; identity + memories)
  └── check-version.py

UserPromptSubmit (4, every prompt)
  ├── rating-capture.py
  ├── auto-work-creation.py
  ├── session-auto-name.py
  └── update-tab-title.py

PreToolUse (7 matchers)
  Bash         → security-validator.py
  Edit         → security-validator.py
  Write        → security-validator.py
  Read         → security-validator.py
  Task         → agent-execution-guard.py
  Skill        → skill-guard.py
  AskUserQ     → set-question-tab.py

PostToolUse (3 matchers)
  Write        → map-updater/scripts/auto-update-codemap.sh
  Bash         → map-updater/scripts/codemap-on-bash.sh
  AskUserQ     → question-answered.py

Stop (1)
  └── stop-orchestrator.py

SessionEnd (7, in order)
  ├── save-memory.py
  ├── work-completion-learning.py
  ├── session-summary.py
  ├── relationship-memory.py
  ├── update-counts.py
  ├── integrity-check.py
  └── algorithm-scan.py
```

That is **24 wired invocations** referencing **19 distinct Python hook scripts** plus 2 map-updater shell scripts (`security-validator.py` covers 4 of the PreToolUse matchers). Every Python hook carries a SIGALRM timeout (5s default; 8s for `session-start.py`; 10s for `stop-orchestrator.py` and `algorithm-scan.py`) and exits 0 on error — hooks fail safe, and `security-validator.py` fails OPEN. All errors append to `memory/learning/system/hook-errors.jsonl`; every hook's latency appends to `memory/learning/system/hook-perf.jsonl`.

## What can fail and what it costs

| Failure | Symptom | Recovery |
|---------|---------|----------|
| `session-start.py` times out (8s) | Identity not in context; "timed out (8s)" on stderr | Restart session; check `hook-perf.jsonl` |
| `NotFoundError: Collection [memories]` | Fresh box, no vector store yet | Expected and handled; session-start returns empty memories |
| `security-validator.py` false positive | Tool blocked unexpectedly | Override via prompt or update `identity/security-patterns.yaml` (never `--no-verify`) |
| `auto-work-creation.py` over-fires | Empty work directories accumulate | `/rai sanity` flags them; manually delete |
| `update-counts.py` writes nowhere | `counts` block in settings frozen at 2026-04-18 | Known bug — `get_settings_path()` targets non-existent `03-rai/settings.json`; counts live only in `counts-history.jsonl` |
| ChromaDB lock contention | session-start.py slow | Wait; the lock will release |
| `pending/` accumulates (≥20) | `skills_bad`/pending WARN in `[rai]` footer; semantic memory stale | Run `/rai process-sessions` on the Linux coordinator |
| Session crash before SessionEnd | Orphan state files | Auto-swept on next SessionStart (6h threshold) |
| Identity cache mtime drift | Stale identity in context | Touch identity files or delete `identity-cache.json` |
| `skills_bad=N` in `[rai]` footer | A `SKILL.md` lost its `name:`/`description:` frontmatter | Fix the named skill's frontmatter (caught by `_validate_skills()`) |

Full troubleshooting in [20-troubleshooting.md](./20-troubleshooting.md).
