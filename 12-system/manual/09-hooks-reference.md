# 09 — Hooks Reference

Every hook in the brain. What event fires it. What it does. What it costs. What it reads and writes.

> Last updated: 2026-06-14. CLAUDE.md and the live `03-rai/config/settings.json` are the source of truth; this chapter is a snapshot. When they disagree, they win.

## Where hooks are wired

```
03-rai/config/settings.json   ← canonical, git-tracked event → hook mapping
03-rai/hooks/*.py             ← hook implementations (19 distinct scripts)
03-rai/hooks/lib/*.py         ← shared utilities (17 modules + __init__.py)
03-rai/hooks/scripts/*.py     ← skill-called utilities (not event-triggered)
```

### Canonical settings path — read this first, it is easy to get wrong

Claude Code reads `~/.claude/settings.json`, but that is a **symlink**. The real, git-tracked file lives at `03-rai/config/settings.json` (9.1 KB). Edit there.

| Symlink (what Claude reads) | Real target (edit here) |
|---|---|
| `~/.claude/settings.json` | `~/helm/03-rai/config/settings.json` |
| `~/.claude/hooks` (whole dir) | `~/helm/03-rai/hooks` |
| `~/.claude/CLAUDE.md` | `~/helm/03-rai/CLAUDE.md` |

Two consequences this chapter relies on:

- `03-rai/settings.json` **does not exist** — only `03-rai/config/settings.json` does. Anything that targets `03-rai/settings.json` is pointing at nothing. (This is the root of the known counts bug — see `update-counts.py` below.)
- Because `~/.claude/hooks` is a directory symlink, `save-memory.py` loading `~/.claude/hooks/context_mapping.json` resolves through to `03-rai/hooks/context_mapping.json` and works.

The rest of `03-rai/config/` holds `mcp.json` (123 B), `statusline.sh` (4.1 KB), and `.skill-lock.json` (461 B).

### Path resolution (cross-platform, since 2026-06-09)

Every hook command in `settings.json` uses `$HOME/helm/03-rai/...` (the shell expands `$HOME`). The `env` block is now **empty** (`"env": {}`) — the old `PAI_DIR` env var was removed. Hooks self-resolve to `~/helm/03-rai` via `lib/paths.py` (`get_pai_dir()` returns `$PAI_DIR` if set, else `~/helm/03-rai`). This was done so the Mac↔Linux git sync stops breaking machine-specific home paths on whichever box wasn't last to write. Python hooks run under system `python3` (3.9 on Mac); the one ChromaDB-touching hook runs through a `uv` Python-3.12 wrapper (`py-chroma.sh`).

## The 6 hooked events

```
SessionStart          → fires when Claude Code session begins
UserPromptSubmit      → fires before model sees each user message
PreToolUse            → fires before each tool call (matchable by tool type)
PostToolUse           → fires after each tool call (matchable)
Stop                  → fires on user interruption / pause
SessionEnd            → fires when session ends
```

## Full wiring table — exactly what runs when

**24 total wired invocations** across the 6 events, referencing **19 distinct hook Python scripts** + **2 distinct map-updater shell scripts**. The arithmetic: SessionStart 2 + UserPromptSubmit 4 + PreToolUse 7 + PostToolUse 3 + Stop 1 + SessionEnd 7 = 24. The gap between 24 and 19 is `security-validator.py`, which is reused across 4 PreToolUse matchers (Bash, Edit, Write, Read). All 19 `.py` hook scripts are wired into at least one event — there are no orphan hook scripts.

This is the verbatim wiring from `03-rai/config/settings.json`:

### SessionStart (2, in order)

```
1. $HOME/helm/03-rai/semantic-memory/scripts/py-chroma.sh \
     $HOME/helm/03-rai/hooks/session-start.py
2. python3 $HOME/helm/03-rai/hooks/check-version.py
```

### UserPromptSubmit (4, in order)

```
1. python3 $HOME/helm/03-rai/hooks/rating-capture.py
2. python3 $HOME/helm/03-rai/hooks/auto-work-creation.py
3. python3 $HOME/helm/03-rai/hooks/session-auto-name.py
4. python3 $HOME/helm/03-rai/hooks/update-tab-title.py
```

### PreToolUse (7 matchers)

```
matcher: Bash             → security-validator.py
matcher: Edit             → security-validator.py
matcher: Write            → security-validator.py
matcher: Read             → security-validator.py
matcher: Task             → agent-execution-guard.py
matcher: Skill            → skill-guard.py
matcher: AskUserQuestion  → set-question-tab.py
```

### PostToolUse (3 matchers)

```
matcher: Write            → skills/map-updater/scripts/auto-update-codemap.sh
matcher: Bash             → skills/map-updater/scripts/codemap-on-bash.sh
matcher: AskUserQuestion  → question-answered.py
```

### Stop (1)

```
1. python3 stop-orchestrator.py
```

### SessionEnd (7, in order)

```
1. python3 save-memory.py
2. python3 work-completion-learning.py
3. python3 session-summary.py
4. python3 relationship-memory.py
5. python3 update-counts.py
6. python3 integrity-check.py
7. python3 algorithm-scan.py
```

### Hook script inventory (`03-rai/hooks/*.py` — 19 files)

| # | File | Size | Event(s) / matcher | One-line purpose |
|---|---|---|---|---|
| 1 | `session-start.py` | 11 KB | SessionStart #1 | Load Rai identity + memories from ChromaDB; sweep orphan state; validate SKILL.md; emit status line |
| 2 | `check-version.py` | 2.0 KB | SessionStart #2 | Compare installed Claude Code vs latest npm; warn to stderr if outdated |
| 3 | `rating-capture.py` | 4.6 KB | UserPromptSubmit | Detect explicit 1-10 ratings in prompt; log to ratings.jsonl; low (<6) → learning file |
| 4 | `auto-work-creation.py` | 4.8 KB | UserPromptSubmit | Pre-create `memory/work/{ts}_{slug}/tasks/001_*/` for "work" prompts |
| 5 | `session-auto-name.py` | 1.8 KB | UserPromptSubmit | Heuristic 2-3 word session name on first prompt; store in session-names.json |
| 6 | `update-tab-title.py` | 1.4 KB | UserPromptSubmit | Set tab title to "Working: {first 4 words}" |
| 7 | `security-validator.py` | 13 KB | PreToolUse: Bash/Edit/Write/Read | Block/confirm/alert dangerous bash + protected paths; pre-commit secret scan |
| 8 | `agent-execution-guard.py` | 1.7 KB | PreToolUse: Task | Suggest `run_in_background: true` on non-fast Task spawns (advisory only) |
| 9 | `skill-guard.py` | 1.3 KB | PreToolUse: Skill | Block false-positive skill invocations (currently only `keybindings-help`) |
| 10 | `set-question-tab.py` | 1.8 KB | PreToolUse: AskUserQuestion | Switch tab title to "Awaiting input" state, save previous title |
| 11 | `question-answered.py` | 1.3 KB | PostToolUse: AskUserQuestion | Restore tab from question state back to working |
| 12 | `stop-orchestrator.py` | 3.9 KB | Stop | Parse transcript once; reset tab to Done; close algorithm state; notify if ≥3 files changed |
| 13 | `save-memory.py` | 12 KB | SessionEnd #1 | Save transcript + metadata to `semantic-memory/pending/` (skips if <4 human msgs) |
| 14 | `work-completion-learning.py` | 3.3 KB | SessionEnd #2 | If work significant, write learning JSON; delete `current-work.json` |
| 15 | `session-summary.py` | 4.5 KB | SessionEnd #3 | Mark work META.yaml + PRD.md COMPLETED; clean per-session state files |
| 16 | `relationship-memory.py` | 4.1 KB | SessionEnd #4 | Extract W/B/O signals → `memory/relationship/YYYY-MM/YYYY-MM-DD.md` |
| 17 | `update-counts.py` | 3.1 KB | SessionEnd #5 | Recount skills/hooks/ratings/work/learnings (writes to wrong path — see below) |
| 18 | `integrity-check.py` | 2.9 KB | SessionEnd #6 | Detect edits to Rai system files; write change record; rotate >30 days |
| 19 | `algorithm-scan.py` | 4.5 KB | SessionEnd #7 | Parse transcript; extract ISC criteria + Task spawns + phase → `state/algorithms/{id}.json` |

---

## Hook reference (alphabetical by file)

### agent-execution-guard.py

**Path:** `03-rai/hooks/agent-execution-guard.py`
**Event:** PreToolUse (matcher: Task).
**Timeout:** SIGALRM 5s.
**Cost:** Fast (<5ms).

**What it does:**

This is a **WARN-ONLY, advisory** guard. It does **not** block, does not validate that the agent exists, does not read frontmatter, and does not enforce permissions. It only nudges toward backgrounding heavy agent spawns.

- Passes silently if any of: `run_in_background: true`, `model == "haiku"`, `subagent_type == "Explore"`, or the prompt contains `"Timing: FAST"`.
- Otherwise emits `{"decision": "allow", "message": "Consider adding run_in_background: true..."}` — allow plus a suggestion.

**Reads:** the pending Task call args.

**Writes:** nothing (advisory message only).

**Failure mode:** never blocks the Task call. (The old manual claimed this hook validates agent existence and enforces per-agent permissions — it does neither. See [./08-agents-catalog.md](./08-agents-catalog.md).)

### algorithm-scan.py

**Path:** `03-rai/hooks/algorithm-scan.py`
**Event:** SessionEnd (#7).
**Timeout:** SIGALRM 10s.
**Cost:** Medium (avg ~11.5ms).

**What it does:**

Replaces the **retired** per-PostToolUse `algorithm-tracker.py`. No per-tool algorithm hook is wired anymore — this single SessionEnd pass does the work. One transcript walk:

- `TaskCreate` events → extract `ISC-[CA]\d+` criteria + phase hints.
- `Task` events → record each agent spawn.
- Final assistant text → phase hint.
- Then calls `algorithm_end` to close out the per-session algorithm state.

**Reads:**
- The session transcript.
- `memory/state/algorithms/{session_id}.json` (per-session phase history, written by `lib/algorithm_state.py`).

**Writes:**
- `memory/state/algorithms/{session_id}.json` (scan results).

### auto-work-creation.py

**Path:** `03-rai/hooks/auto-work-creation.py`
**Event:** UserPromptSubmit.
**Timeout:** SIGALRM 5s.
**Cost:** Fast (avg ~0.3ms).

**What it does:**

`classify_prompt()` buckets the prompt as `conversational | work | continuation`. Only on a fresh **work** prompt (no existing current-work) does it pre-create a work tree so the Algorithm can immediately drop a PRD:

1. Generates a slug: `{filename_ts}_{kebab-task-description}` (note: underscore separators, `YYYYMMDD_HHMMSS_slug`).
2. Creates `memory/work/{ts}_{slug}/` with `tasks/`, `scratch/`, and a `META.yaml` ledger.
3. Creates first task dir `tasks/001_{slug}/` with `ISC.json`, `THREAD.md`, and `PRD.md` (from `lib/prd_template`, Algorithm v3.7.0 schema), plus a `tasks/current` symlink.
4. Writes both `memory/state/current-work-{session_id}.json` AND a legacy `memory/state/current-work.json`.

**Reads:**
- The user prompt (passed by the harness).
- Existing current-work state (to avoid double-creating).

**Writes:**
- `memory/work/{ts}_{slug}/` (new tree: META.yaml + tasks/001_*/{ISC.json, THREAD.md, PRD.md}).
- `memory/state/current-work-{session_id}.json` + legacy `current-work.json`.

**Failure mode:** over-firing creates empty work directories. Work dirs accumulate (>500 on disk); `/rai sanity` flags them.

### auto-update-codemap.sh

**Path:** `03-rai/skills/map-updater/scripts/auto-update-codemap.sh`
**Event:** PostToolUse (matcher: Write).
**Cost:** Fast (<5ms typically).

**What it does:**

No-op unless a `.codemap/` directory exists at the git root. It does NOT regenerate the codemap itself — it prints a `[CODEMAP]` reminder nudging `/map-updater`. Skips `.codemap/`, `node_modules`, `.git`, `__pycache__`, `.venv`/`venv`. Reads `$CLAUDE_TOOL_ARG_FILE_PATH`. Always a no-op inside the helm vault (no `.codemap/` there).

**Reads:** `$CLAUDE_TOOL_ARG_FILE_PATH`, git root.
**Writes:** nothing (reminder to stdout only).

### check-version.py

**Path:** `03-rai/hooks/check-version.py`
**Event:** SessionStart (#2).
**Timeout:** SIGALRM 5s.
**Cost:** Slow (p50 ~897ms, max ~1925ms) — the **second-heaviest hook**, dominated by the `npm view` network call.

**What it does:**

- Reads stdin JSON; **exits immediately if `is_subagent`** is set (subagents skip the version check).
- Runs `claude --version` (3s timeout) against `npm view @anthropic-ai/claude-code version` (5s timeout).
- If they differ, prints `Claude Code update available: X -> Y...` to stderr. Does not block the session.

**Reads:** stdin JSON, the two version sources.
**Writes:** nothing (stderr warning only).

### codemap-on-bash.sh

**Path:** `03-rai/skills/map-updater/scripts/codemap-on-bash.sh`
**Event:** PostToolUse (matcher: Bash).
**Cost:** Fast (<5ms typically).

**What it does:**

Same `.codemap/` gate as `auto-update-codemap.sh`, but triggered by Bash. Fires only for structure-changing commands (`rm`, `rmdir`, `mkdir`, `mv` — reads `$CLAUDE_TOOL_ARG_COMMAND`). Prints a `[CODEMAP]` structure-change reminder.

**Reads:** `$CLAUDE_TOOL_ARG_COMMAND`, git root.
**Writes:** nothing (reminder only).

### integrity-check.py

**Path:** `03-rai/hooks/integrity-check.py`
**Event:** SessionEnd (#6).
**Timeout:** SIGALRM 5s.
**Cost:** Fast (avg ~5.6ms).

**What it does:**

Detects edits to Rai **system** files during the session. `extract_modified_files(transcript)` keeps files under PAI_DIR that are NOT in the exclude set (`memory/work`, `memory/learning`, `memory/state`, `scratch` — overridable via `settings.integrityCheck.exclude`).

**Reads:**
- The session transcript.

**Writes:**
- `memory/learning/system/integrity/change-{TIMESTAMP}.json` — per-run change record. Records older than 30 days (`RETENTION_DAYS=30`) are rotated out by mtime.

### question-answered.py

**Path:** `03-rai/hooks/question-answered.py`
**Event:** PostToolUse (matcher: AskUserQuestion).
**Timeout:** SIGALRM 5s.
**Cost:** Fast (avg ~1.4ms).

**What it does:**

Restores the tab title from the question/"Awaiting input" state back to "working", using the `previous_title` stashed by `set-question-tab.py`.

**Reads:** `memory/state/tab-titles/{uuid}.json`.
**Writes:** same file (clears pending state).

### rating-capture.py

**Path:** `03-rai/hooks/rating-capture.py`
**Event:** UserPromptSubmit.
**Timeout:** SIGALRM 5s.
**Cost:** Fast (avg ~0ms).

**What it does:**

`RATING_RE` matches a line starting with a 1-10 score optionally followed by a separator/comment; `FALSE_POSITIVE_RE` rejects counts, ordinals, units, decimals, and times (so "8 files" or "3rd" don't register). Skips prompts longer than 200 chars.

**Reads:** the user prompt.
**Writes:**
- `memory/learning/signals/ratings.jsonl` (every captured rating).
- `memory/learning/system/YYYY-MM/low-rating-{score}-{ts}.json` if the score is <6.

### relationship-memory.py

**Path:** `03-rai/hooks/relationship-memory.py`
**Event:** SessionEnd (#4).
**Timeout:** SIGALRM 5s.
**Cost:** Medium (avg ~6.6ms).

**What it does:**

Classifies each user message with regex into three signal tags:
- `O` — preference (5 regex).
- `W` — world fact (4 regex).
- `B` — biographical (4 regex).

Dedups by 80-char prefix, caps at **30 signals** per session.

**Reads:** the session transcript (user messages).
**Writes:** `memory/relationship/{YYYY-MM}/{YYYY-MM-DD}.md` — appends or creates the daily note.

### save-memory.py

**Path:** `03-rai/hooks/save-memory.py`
**Event:** SessionEnd (#1).
**Cost:** Medium (avg ~20ms, max ~43ms).
**No AI calls.** Pure JSON storage.

**What it does:**

1. **Skips entirely if the session has <4 human messages** — trivial sessions never reach the pending queue.
2. Extracts cwd, context (via `context_mapping.json`), project name (resolved from `.git` remote, then `pyproject.toml`, `package.json`, then folder name), duration (first vs last timestamp), tool counts, and modified files (Edit/Write/NotebookEdit).
3. Writes `semantic-memory/pending/session_{YYYYMMDD_HHMMSS}.json` with the full user + assistant messages.

It writes to the pending queue only — the drain into ChromaDB is a **separate Linux-only step** run by `/rai process-sessions` (see [./10-memory-systems.md](./10-memory-systems.md)).

**Reads:**
- The session transcript.
- `~/.claude/hooks/context_mapping.json` (→ `03-rai/hooks/context_mapping.json` via the directory symlink).

**Writes:**
- `semantic-memory/pending/session_{TIMESTAMP}.json`.
- Debug log → `~/.claude/logs/save-memory-debug.log`.

### session-auto-name.py

**Path:** `03-rai/hooks/session-auto-name.py`
**Event:** UserPromptSubmit.
**Timeout:** SIGALRM 5s.
**Cost:** Fast (avg ~0.2ms; first prompt only, idempotent per session).

**What it does:**

If the session has no name yet, `short_name()` generates a 2-3 word, noise-filtered name from the first user prompt (heuristics in `lib/name_extraction.py`, 100+ NOISE_WORDS). Echoes the name to stderr.

**Reads:** the first user prompt, `memory/state/session-names.json`.
**Writes:** `memory/state/session-names.json` — adds entry `{uuid: name}`.

### session-start.py

**Path:** `03-rai/hooks/session-start.py`
**Wrapped by:** `03-rai/semantic-memory/scripts/py-chroma.sh` (a `uv` Python-3.12 + chromadb wrapper — system python3 lacks chromadb).
**Event:** SessionStart (#1).
**Timeout:** SIGALRM 8s. On timeout it prints "Rai identity load timed out (8s)" and exits 0.
**Cost:** Medium-slow. Python body p50 ~559ms (avg ~592ms, max ~1260ms) PLUS the uv/chromadb wrapper cold-start (not captured by the in-process timer). This is the **single heaviest hook** by wall time.

**What it does (in order):**

1. **State sweep** — `_sweep_orphans_safe()` → `lib/state_sweep.sweep_orphans()`. Deletes per-session state files (`current-work-*.json`, `tab-titles/*.json`, `algorithms/*.json`) and prunes `session-names.json` entries whose session has had no state activity in the last **6 hours** (`STALE_HOURS=6`). The current session is always kept.
2. **Identity discovery** — every `*.md` in `03-rai/identity/` (4 files) and `02-ana/identity/` (13 files), sorted. Non-`.md` (e.g. `security-patterns.yaml`) is intentionally skipped.
3. **Identity cache** — `_load_identity_cached()` reads an mtime-invalidated cache at `memory/state/identity-cache.json`. Cache is valid if its `max_mtime ≥` the sources' max mtime AND the file list matches; output is tagged `cached` or `fresh`.
4. **CWD scope** — `in_brain_vault(cwd)`: if CWD is anywhere under `~/helm`, load **FULL** memory (full doc text, all dates); else **last 7 rolling days** only, truncated to 200 chars.
5. **Helm index** — append `.helm-index/helm-index.md` (if ≤20 KB) as "## Helm Index".
6. **Codemap** — walk up from CWD (+3 parents) for `.codemap/codemap.md` (if ≤20 KB) → "## Codemap".
7. **ChromaDB read** — `chromadb.PersistentClient` → collection `"memories"`, sorted by `meta.date` desc.
8. **Identity emit** — print `=== Rai Identity Loaded (cached|fresh) ===` … `=== End Rai Identity ===` for harness injection.
9. **SKILL.md validation** (added 2026-05-13) — `_validate_skills()` regex-checks every `skills/<name>/SKILL.md` for `---` frontmatter with `name:` and `description:`. Malformed skills are printed and counted as `skills_bad=N`. (Added after a "skills not loading" outage where `project-init` had no frontmatter.)
10. **Status line** — `[rai] memories=N identity=cached|fresh|none [orphans_swept=N] [pending=N [WARN: run /process-sessions]] [skills_bad=N]`. The pending warn threshold is **20** (`PENDING_WARN`).

**Reads:** all identity `.md` files, ChromaDB, `memory/state/identity-cache.json`.

**Writes:** `memory/state/identity-cache.json` (if cache invalid); may delete orphaned state files.

**Failure mode:** logs to stderr, continues — never hard-fails SessionStart. **Known LIVE state:** on a fresh box where the `memories` collection doesn't exist yet, `load_memories` raises `NotFoundError: Collection [memories] does not exist`; this is caught and returns `[], 0`. Occasional `BrokenPipeError` (stdout closed early) is likewise non-fatal.

### session-summary.py

**Path:** `03-rai/hooks/session-summary.py`
**Event:** SessionEnd (#3).
**Timeout:** SIGALRM 5s.
**Cost:** Fast (avg ~1.3ms).

**What it does:**

This is the **cleanup pass**.

1. Finds the scoped-or-legacy current-work state file.
2. Marks the work as done: sets legacy `META.yaml` and v3.7.0 `tasks/*/PRD.md` frontmatter to `status: COMPLETED` + `completed_at`.
3. Deletes per-session state files for this UUID: `current-work-{uuid}.json` (+ legacy `current-work.json`), `tab-titles/{uuid}.json`, `algorithms/{uuid}.json`.
4. Removes this session's entry from `session-names.json`.
5. Skips the OSC tab write at session end (saves ~200-600ms).

**Reads:** the session transcript, all per-session state files.
**Writes:** deletes per-session state files; updates `session-names.json`; marks META.yaml/PRD.md COMPLETED.

### set-question-tab.py

**Path:** `03-rai/hooks/set-question-tab.py`
**Event:** PreToolUse (matcher: AskUserQuestion).
**Timeout:** SIGALRM 5s.
**Cost:** Fast (avg ~1.4ms).

**What it does:**

Extracts the first question header (≤20 chars) and calls `set_tab_state("question", ...)` to signal a pending question — so John notices the tab when working in another window. Saves the previous title for restore.

**Reads / Writes:** `memory/state/tab-titles/{uuid}.json`.

### skill-guard.py

**Path:** `03-rai/hooks/skill-guard.py`
**Event:** PreToolUse (matcher: Skill).
**Timeout:** SIGALRM 5s.
**Cost:** Fast (avg ~0ms).

**What it does:**

Blocks specific **false-positive** skill invocations. `BLOCKED_SKILLS = {"keybindings-help"}` — currently the only blocked skill. When a blocked skill is requested it returns `{"decision": "block", ...}` + exit 2. Rationale: `keybindings-help` sits first in the skills list and false-fires on aggressive BLOCKING-REQUIREMENT language.

This is **not** a concurrency lock. (The old manual described a `.skill-lock.json`-based mutex acquired per skill call — that is not what this hook does today.)

**Reads:** the pending Skill call.
**Writes:** nothing.

### security-validator.py

**Path:** `03-rai/hooks/security-validator.py`
**Event:** PreToolUse (matchers: Bash, Edit, Write, Read).
**Timeout:** SIGALRM 5s. **Fails OPEN** on any internal error (a crash never blocks a tool call).
**Cost:** by far the most-invoked hook (~1498 samples in window) but very cheap: avg 2.6ms, p50 2.4ms, max ~50ms.

**What it does:**

The most important hook in the brain. It scans every Bash command, Edit, Write, and Read.

**Pattern cascade** (first available wins): `identity/security-patterns.yaml` (user, v1.0) → `security-patterns.example.yaml` (fallback superset) → a hardcoded minimal dict if PyYAML is unavailable.

**Bash levels:**
- `blocked` — substring match → exit 2, prints `{"error":"BLOCKED: ..."}` to stderr (e.g. `rm -rf /`, `diskutil eraseDisk/zeroDisk`, `mkfs`, `gh repo delete`, `gh repo edit --visibility public`).
- `confirm` — regex → stdout `{"decision":"ask","message":...}`, exit 0 (e.g. force push, `reset --hard`, `DROP DATABASE/TABLE`, `TRUNCATE`, `terraform destroy`, `docker system prune`).
- `alert` — regex → log only, allow (e.g. `curl|sh`/`wget|bash`).

**Pre-commit secret scan:** if the command matches `\bgit\s+commit\b`, it runs `lib/protected_scan.scan_staged_git_files()` against `.pai-protected.json`; any hit → exit 2 BLOCKED with a per-file category summary (fail-open if the scanner errors).

**Path levels (Read/Write/Edit):** `zeroAccess` (block all — ssh/aws/gnupg/credentials globs), `readOnly` (block Write/Edit — e.g. `/etc/**`), `confirmWrite` (ask before Write/Edit — e.g. `.env`, `~/.ssh/*`). `noDelete` (.git, LICENSE*, README.md) is documented but not enforced for Write/Edit.

**Reads:**
- The pending tool call args.
- `03-rai/identity/security-patterns.yaml` (or the `.example.yaml` fallback).
- `03-rai/.pai-protected.json` (14 KB, version `rai-1.0`, 15 categories) via `lib/protected_scan.py`.

**Writes:** `memory/security/{YYYY}/{MM}/security-{YYYYMMDD}.jsonl` — JSONL event log.

**Failure mode:** a blocked pattern blocks the tool call with a reason; an internal error fails OPEN (allows).

### state_sweep (lib/state_sweep.py)

**Path:** `03-rai/hooks/lib/state_sweep.py`
**Called by:** `session-start.py`.
**Event:** indirectly on SessionStart.

**What it does:**

`sweep_orphans()` walks `memory/state/` for orphan per-session files. Threshold: **6 hours** (`STALE_HOURS=6`). For each `current-work-{uuid}.json`, `tab-titles/{uuid}.json`, `algorithms/{uuid}.json`, it checks mtime and deletes if older than 6h (the current session is never swept). Also prunes `session-names.json` for stale UUIDs. Returns counts (`current_work`, `tab_titles`, `algorithms`, `session_names`).

### stop-orchestrator.py

**Path:** `03-rai/hooks/stop-orchestrator.py`
**Event:** Stop.
**Timeout:** SIGALRM 10s.
**Cost:** Fast (avg ~7.4ms, max ~14ms).

**What it does:**

One transcript parse, then three **isolated** handlers (a failure in one does not stop the others):

1. `handle_tab_reset` → `set_tab_state("completed", session_id, response[:50])`.
2. `handle_algorithm_enrichment` → if the algorithm phase is not IDLE/COMPLETE, call `algorithm_end`.
3. `handle_notification` → if `current-work-{session_id}.json` shows ≥3 `files_changed`, `notify("task_complete", ...)`.

**Reads:** session transcript, `current-work-{session_id}.json`, algorithm state.
**Writes:** tab state, algorithm state (may close it).

### update-counts.py

**Path:** `03-rai/hooks/update-counts.py`
**Event:** SessionEnd (#5).
**Timeout:** SIGALRM 5s.
**Cost:** Fast (avg ~3.8ms).

**What it does:**

Recounts and intends to refresh the `counts` block:
- skills (dirs with `SKILL.md`),
- hooks (`*.py` glob in `03-rai/hooks/` — every `.py`, not just wired ones),
- ratings (lines in `ratings.jsonl`),
- work (subdirs of `memory/work/`),
- learnings (`.json` under `learning/`).

**KNOWN BUG — the counts block is FROZEN.** It writes to `lib/paths.get_settings_path()`, which returns `get_pai_dir() / "settings.json"` = `03-rai/settings.json`. **That file does not exist** (the real file is `03-rai/config/settings.json`). So the write silently no-ops and the live `counts` block has not refreshed since 2026-04-18. The stale frozen values in `config/settings.json` read:

```
skills: 66, hooks: 22, ratings: 4, work: 27, learnings: 16
updatedAt: 2026-04-18T06:54:29Z
```

None are current. The real hook count today is **19 `.py` files** (all wired); `hooks: 22` is an April-era artifact. Skills are 35 top-level entries, not 66 (see [./07-skills-catalog.md](./07-skills-catalog.md)). The fix is to point `get_settings_path()` at `config/settings.json`.

**Writes (that succeed):** appends `memory/learning/system/counts-history.jsonl`.
**Writes (that no-op):** the `counts` block in the non-existent `03-rai/settings.json`.

### update-tab-title.py

**Path:** `03-rai/hooks/update-tab-title.py`
**Event:** UserPromptSubmit.
**Timeout:** SIGALRM 5s.
**Cost:** Fast (avg ~1.3ms).

**What it does:**

`set_tab_state("working", session_id, "{first 4 words}")` via `lib/tab_setter` — sets the terminal tab title to "Working: {first 4 words}". Tab control is via OSC escape sequences plus a `wezterm cli` fallback (see the Ghostty note in gotchas).

**Reads:** `memory/state/session-names.json`, `memory/state/tab-titles/{uuid}.json`.
**Writes:** `memory/state/tab-titles/{uuid}.json`; emits the tab title.

### work-completion-learning.py

**Path:** `03-rai/hooks/work-completion-learning.py`
**Event:** SessionEnd (#2).
**Timeout:** SIGALRM 5s.
**Cost:** Fast (avg ~0.1ms).

**What it does:**

Reads `memory/state/current-work.json` (legacy path only). Work is "significant" if ≥3 files changed OR ≥1 task completed OR status is completed. It categorizes the learning via `ALGORITHM_KEYWORDS` (22 keywords) → `algorithm`, else `system`, then writes `learning/{cat}/YYYY-MM/work-{ts}.json` and **deletes** `current-work.json`.

**Reads:** `memory/state/current-work.json`, the session transcript.
**Writes:** `memory/learning/{system|algorithm}/YYYY-MM/work-{ts}.json`; deletes `current-work.json`.

---

## Shared utilities (lib/)

Imported by multiple hooks. Not directly fired by events. `03-rai/hooks/lib/` holds **17 modules + `__init__.py`** (18 files).

| Module | Purpose |
|--------|---------|
| `__init__.py` | "Rai Hook shared libraries" marker (28 B) |
| `paths.py` | Central path resolver. `get_pai_dir()` = `$PAI_DIR` or `~/helm/03-rai`. **`get_settings_path()` returns the stale `03-rai/settings.json`** (real file is `config/settings.json`) — the counts-bug root cause |
| `hook_timer.py` | `@contextmanager hook_timer(name)` → append `{hook, ms, ts}` to `learning/system/hook-perf.jsonl` |
| `hook_errors.py` | `log_error(hook, err, ctx)` → append `learning/system/hook-errors.jsonl` (name, type, msg, traceback, ts) |
| `algorithm_state.py` | Per-session algorithm state at `state/algorithms/{id}.json`. PHASES: IDLE, OBSERVE, THINK, PLAN, BUILD, EXECUTE, VERIFY, LEARN, COMPLETE. `phase_transition`, `criteria_add`, `agent_add`, `algorithm_end`; tracks rework_cycles |
| `identity.py` | Cached settings reader; `get_da_name`, `get_principal_name/timezone`, `get_notification_config` |
| `learning_utils.py` | `get_learning_category` (12 ALGORITHM + 15 SYSTEM keywords); `is_learning_capture` |
| `name_extraction.py` | `short_name()` (2-3 word name), `work_slug()` (kebab); 100+ NOISE_WORDS set |
| `notifications.py` | `notify(event,...)` → ntfy / Discord / Twilio per `settings.notifications.routing`. All channels disabled in current config |
| `output_validators.py` | `is_valid_working_title` (gerund 2-4 words); `gerund_to_past_tense` (33-entry map) |
| `prd_template.py` | `slugify`, `generate_prd_filename`, `generate_prd_template` (Algorithm v3.7.0 PRD: Context/Criteria/Anti-criteria/Decision Log/Verification/Capability invocation log) |
| `protected_scan.py` | Loads `.pai-protected.json`; `scan`, `scan_file`, `scan_staged_git_files()`; respects `allowed_prefixes` + `exception_files`. CLI: `python3 -m hooks.lib.protected_scan [--staged\|path]` |
| `state_sweep.py` | `sweep_orphans()` — delete per-session state files with no activity in 6h; returns counts |
| `tab_constants.py` | `PHASE_CONFIG` (8 phases, symbols O/T/P/B/X/V/L/D); `TAB_STATES` (thinking/working/question/completed/error/idle) |
| `tab_setter.py` | Terminal tab control via OSC `\033]1;...\007` + `wezterm cli set-tab-title` fallback; `set_tab_state`, `set_phase_tab`, `read_tab_state`; persists `state/tab-titles/{id}.json` with previous_title |
| `time_utils.py` | ISO/local timestamps, year-month, `get_filename_timestamp` (YYYYMMDD_HHMMSS); reads principal timezone (America/Chicago) from settings |
| `transcript_parse.py` | Shared JSONL walker: `iter_transcript`, `iter_assistant_tool_uses`, `extract_modified_files`, `extract_user_messages` |
| `work_index.py` | Scan `memory/work/` → `state/work.json` master index (slug, tier, status, ISC progress, capabilities). CLI runnable; tolerant of v1.6 + v3.7 schemas |

## Skill-called scripts (scripts/)

Not event-triggered. Called explicitly by skills or wrappers.

| Script | Called by | Purpose |
|--------|-----------|---------|
| `hooks/scripts/store_to_chromadb.py` | `/rai process-sessions` | Drain `pending/*.json` into ChromaDB collection `memories` (cosine HNSW). 30+ CLI args across v2/v3 metadata schemas; computes `related_to` via embedding similarity (threshold 0.85, up to 3) |
| `semantic-memory/scripts/py-chroma.sh` | `session-start.py` (SessionStart #1) | `exec uv run --quiet --python 3.12 --with chromadb python3 "$@"` — exists because system python3 lacks chromadb |
| `skills/map-updater/scripts/suggest-update.sh` | `/map-updater` (manual) | NOT wired into settings — nudges `/map-updater` after N new files (THRESHOLD default 5) |

---

## Hook cost summary

Measured from a recent ~2000-sample `hook-perf.jsonl` window (2026-06-14). The two slow hooks both run only at SessionStart; everything in the prompt/tool hot path is single-digit ms.

| Cost class | Typical range | Hooks |
|------------|---------------|-------|
| **Fast** | <10ms | rating-capture, session-auto-name, work-completion-learning, skill-guard, auto-work-creation, update-tab-title, session-summary, question-answered, set-question-tab, security-validator, agent-execution-guard, update-counts, integrity-check, relationship-memory, stop-orchestrator |
| **Medium** | 10-30ms | algorithm-scan, save-memory |
| **Slow** | 500ms-2s | session-start (~559ms p50 + uv cold-start), check-version (~897ms p50) |

Per-hook measured latency (avg / p50 / max ms), heaviest first:

| Hook | n | avg | p50 | max |
|---|---|---|---|---|
| check-version | 23 | 775.3 | 896.9 | 1925.0 |
| session-start | 23 | 592.0 | 559.0 | 1259.7 |
| save-memory | 22 | 19.9 | 25.0 | 43.2 |
| algorithm-scan | 22 | 11.5 | 14.6 | 32.0 |
| stop-orchestrator | 41 | 7.4 | 7.8 | 14.4 |
| relationship-memory | 22 | 6.6 | 8.0 | 18.2 |
| integrity-check | 22 | 5.6 | 7.4 | 12.4 |
| update-counts | 22 | 3.8 | 3.4 | 8.5 |
| security-validator | 1498 | 2.6 | 2.4 | 50.1 |
| set-question-tab / question-answered | 8 / 8 | 1.4 | 1.8 | 2.7 |
| update-tab-title | 61 | 1.3 | 0.9 | 4.0 |
| session-summary | 22 | 1.3 | 1.2 | 4.0 |
| auto-work-creation | 61 | 0.3 | 0.1 | 1.7 |
| session-auto-name | 61 | 0.2 | 0.1 | 0.7 |
| work-completion-learning | 22 | 0.1 | 0.1 | 0.3 |
| rating-capture / skill-guard | 61 / 1 | 0.0 | 0.0 | 0.1 |

Total SessionStart overhead: ~1.5-3s (dominated by check-version + session-start, both with network/cold-start).
Total UserPromptSubmit overhead: ~2ms (all four hooks are single-digit ms).
Total SessionEnd overhead: ~40-60ms across all 7 hooks.
PreToolUse overhead per call: ~2.6ms for security-validator (the hot path).
PostToolUse overhead per call: ~1.4ms (codemap shells + question-answered).

## Hook timeouts (SIGALRM)

Every Python hook installs a SIGALRM alarm and exits 0 on timeout, so a hung hook can never wedge the session.

| Hook | Timeout |
|---|---|
| `session-start.py` | 8s |
| `stop-orchestrator.py` | 10s |
| `algorithm-scan.py` | 10s |
| `security-validator.py` | 5s (and **fails OPEN** on any internal error) |
| all other Python hooks | 5s default |

`save-memory.py` is wrapped in `lib/hook_timer` rather than a raw SIGALRM but is still bounded. The two shell codemap hooks have no alarm — they are trivial gate-and-print scripts.

## State / output file map

What each hook reads and writes, in one table.

| Path | Written by | Read by |
|---|---|---|
| `memory/state/identity-cache.json` | session-start | session-start |
| `memory/state/session-names.json` | session-auto-name, session-summary, state_sweep | session-start, session-summary |
| `memory/state/current-work-{id}.json` + legacy `current-work.json` | auto-work-creation | work-completion-learning, session-summary, stop-orchestrator |
| `memory/state/tab-titles/{id}.json` | tab_setter (via update-tab-title, set-question-tab) | question-answered, state_sweep |
| `memory/state/algorithms/{id}.json` | algorithm_state | stop-orchestrator, algorithm-scan, state_sweep |
| `memory/work/{ts}_{slug}/...` | auto-work-creation | session-summary, work_index |
| `memory/learning/signals/ratings.jsonl` | rating-capture | update-counts |
| `memory/learning/system/YYYY-MM/low-rating-*.json` | rating-capture | (review) |
| `memory/learning/{system,algorithm}/YYYY-MM/work-*.json` | work-completion-learning | — |
| `memory/learning/system/integrity/change-*.json` | integrity-check | — |
| `memory/learning/system/counts-history.jsonl` | update-counts | — |
| `memory/learning/system/hook-perf.jsonl` | lib/hook_timer (every hook) | (analysis) |
| `memory/learning/system/hook-errors.jsonl` | lib/hook_errors (every hook) | (analysis) |
| `memory/relationship/YYYY-MM/YYYY-MM-DD.md` | relationship-memory | session-start (indirect) |
| `memory/security/YYYY/MM/security-*.jsonl` | security-validator | — |
| `semantic-memory/pending/session_*.json` | save-memory | session-start (count), /process-sessions |
| `semantic-memory/chromadb/` (collection `memories`) | store_to_chromadb | session-start |

## Security / protected-data config

`security-validator.py` reads three layers, in cascade order:

| File | Role |
|---|---|
| `03-rai/identity/security-patterns.yaml` (2.1 KB, v1.0) | USER patterns, loaded first. bash.blocked (10 patterns), bash.confirm (8), bash.alert; paths.zeroAccess (6 ssh/aws/gnupg/credentials globs), readOnly `/etc/**`, confirmWrite (.env, ~/.ssh/*), noDelete (.git, LICENSE*, README.md) |
| `03-rai/security-patterns.example.yaml` (4.4 KB) | Fallback superset (extra diskutil/apfs/force-push patterns) |
| `03-rai/.pai-protected.json` (14 KB, version `rai-1.0`) | The secret/PII scanner config. **15 categories** (api_keys, github_tokens, slack_tokens, webhooks, database_credentials, private_keys, pii_financial, personal_emails, private_paths, internal_infrastructure, credentials_inline, cloudflare, locale_identity, ai_attribution, misc_sensitive). `allowed_prefixes` (~45) + `exception_files` (~140 globs, heavy on the Helios `backend/` tree, `08-bawaba/`, news `.runs/`, memory subtrees) |

Note: `security-patterns.yaml` is in `03-rai/identity/` but is intentionally **NOT** auto-loaded into session context (only `.md` files in identity/ are). It is read by this hook only.

## Disabling a hook (temporarily)

Edit `03-rai/config/settings.json` (reached via `~/.claude/settings.json`). Either:

- Remove the hook entry from the event array.
- Set the path to a no-op (the hook will fail silently and the harness moves on).

settings.json does not support comments, so use a backup file rather than commenting out. Restart the Claude Code session for changes to take effect.

## Adding a new hook

1. **Write the script** at `03-rai/hooks/{name}.py`. Make executable: `chmod +x`.
2. **Use `lib/` utilities** — `paths`, `hook_errors`, `hook_timer`, `output_validators`, `time_utils`.
3. **Install a SIGALRM timeout** (5s default; raise for genuinely heavy work) so the hook can never block the session indefinitely.
4. **Use `$HOME/helm/03-rai/...` paths**, never hardcoded `~/...` — the vault syncs Mac↔Linux and hardcoded home paths break.
5. **Wire it in `03-rai/config/settings.json`** under the appropriate event:

```json
"SessionEnd": [
  ...existing hooks...,
  {
    "hooks": [
      {
        "type": "command",
        "command": "python3 $HOME/helm/03-rai/hooks/your-new-hook.py"
      }
    ]
  }
]
```

6. **Test** — start a new session, trigger the event, verify behavior. Latency lands in `hook-perf.jsonl`; errors land in `hook-errors.jsonl`.
7. **Do NOT rely on `update-counts.py`** to refresh the hook count — it is broken (writes to a non-existent path). The `counts` block in settings.json is frozen until that path is fixed.

## Hook security

Hooks run with the same permissions as the user. Never wire an untrusted script as a hook. `security-validator.py` validates *tool calls*, not the hooks themselves — the hooks are the gate.

When adding a hook:

- Validate inputs; sanitize anything coming from the user prompt.
- Limit subprocess calls.
- Use a SIGALRM timeout and exit 0 on error (fail safe).
- Log failures explicitly via `lib/hook_errors`.

## Common hook failures

| Failure | Symptom | Fix |
|---------|---------|-----|
| `session-start.py` times out (8s) | "Rai identity load timed out"; identity not loaded | Check `hook-perf.jsonl`; reduce ChromaDB scan size; uv cold-start is the usual cause |
| `Collection [memories] does not exist` | session-start NotFoundError on a fresh box | Expected/handled — run `/rai process-sessions` on the Linux coordinator to seed the collection |
| `security-validator.py` blocks an innocuous command | Tool refused | Whitelist the pattern in `identity/security-patterns.yaml` (validator fails OPEN on errors, never on a real match) |
| `auto-work-creation.py` over-fires | Empty `memory/work/` directories | `/rai sanity` reports them; tighten `classify_prompt` heuristics |
| counts in settings.json look wrong (skills:66, hooks:22) | They never update | KNOWN BUG: `get_settings_path()` targets non-existent `03-rai/settings.json`; ignore the values or fix the path |
| Tab title wrong | OSC/`wezterm cli` no-op | On Ghostty the OSC sequence still sets the title; the `wezterm cli` fallback is a no-op there — harmless |
| ChromaDB lock contention on `session-start.py` | Slow start | Wait; the lock releases. Only SessionStart #1 touches ChromaDB |

Full troubleshooting in [./20-troubleshooting.md](./20-troubleshooting.md). For the memory side of what these hooks feed, see [./10-memory-systems.md](./10-memory-systems.md); for the agent guard's behavior, [./08-agents-catalog.md](./08-agents-catalog.md); for the Algorithm state these hooks track, [./06-algorithm-and-prd.md](./06-algorithm-and-prd.md).
