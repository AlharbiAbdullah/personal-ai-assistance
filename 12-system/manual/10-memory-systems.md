# 10 — Memory Systems

> Last updated: 2026-06-14. The live source of truth is `03-rai/ARCHITECTURE.md` (memory sections), `03-rai/SYNC-ARCHITECTURE.md` (the single-writer rule), and the on-disk hooks. This chapter is a snapshot — when it drifts, those win.

Two memory systems run in parallel. File memory (structured, fast) and semantic memory (vector, slow but recall-rich). Plus state and work, which are short-lived.

## The four memory tiers

```
┌──────────────────────────────────────────────────────────┐
│  TIER 1 — STATE     (per-session, dies at SessionEnd)    │
│  03-rai/memory/state/                                    │
└──────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│  TIER 2 — WORK      (per-task record, lives indefinitely)│
│  03-rai/memory/work/{slug}/                              │
└──────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│  TIER 3 — FILE MEMORY  (structured, JSONL + dated MD)    │
│  03-rai/memory/{learning,relationship,security,ai-calls}/│
└──────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│  TIER 4 — SEMANTIC MEMORY  (vector store, ChromaDB)      │
│  03-rai/semantic-memory/{chromadb, pending, scripts}/    │
└──────────────────────────────────────────────────────────┘
```

Tiers correspond to lifetime:
- T1 dies at SessionEnd.
- T2 lives as long as the task record matters.
- T3 lives indefinitely (with some 30-day rotations).
- T4 lives forever.

A critical structural rule sits on top of all four tiers: **only the Linux coordinator writes**. SessionEnd on any machine writes the local file-memory tiers and drops a raw transcript into the `pending/` queue, but the drain into ChromaDB and the only `git push` to GitHub both happen on the Linux box. See "Single-writer rule" below.

---

## Tier 1 — State

**Path:** `03-rai/memory/state/`
**Lifetime:** Per-session. Cleaned at SessionEnd. Orphans swept on next SessionStart (6h threshold).

### Files

| File | Created by | Read by | Cleaned by |
|------|------------|---------|------------|
| `current-work-{uuid}.json` | auto-work-creation.py (UserPromptSubmit) | session-summary.py, work-completion-learning.py | session-summary.py at SessionEnd |
| `current-work.json` (legacy) | older versions | older versions | session-summary.py |
| `tab-titles/{uuid}.json` | lib/tab_setter.py (via update-tab-title, set-question-tab) | tab setter, HUD | session-summary.py |
| `algorithms/{uuid}.json` | algorithm-scan.py (SessionEnd) | algorithm-scan.py, /sanity I3 | session-summary.py |
| `session-names.json` | session-auto-name.py | tab setter, HUD | session-summary.py prunes entry |
| `work.json` | lib/work_index.py | HUD, skills, dashboards | rebuilt in place |
| `identity-cache.json` | session-start.py | session-start.py, /sanity F8 | overwritten each SessionStart |
| `README.md` | manual | humans | — |

> **Doc drift to fix:** older `state/README.md` and `ARCHITECTURE.md` attribute the per-session algorithm state file to `algorithm-tracker.py`. That per-PostToolUse hook is retired (only a stale `.pyc` remains). The real writer is **`algorithm-scan.py`**, a single SessionEnd hook. See [09-hooks-reference.md](./09-hooks-reference.md).

### Schema — current-work-{uuid}.json

```json
{
  "session_id": "session-uuid",
  "started_at": "2026-06-14T09:30:00+03:00",
  "work_dir": "03-rai/memory/work/20260614_093000_implement-login-flow",
  "task_description": "implement login flow",
  "files_changed": [],
  "tasks_completed": [],
  "status": "ACTIVE"
}
```

### Schema — session-names.json

```json
{
  "uuid-1": {"name": "implement-login-flow", "created_at": "..."},
  "uuid-2": {"name": "fix-deployment-bug", "created_at": "..."}
}
```

### Schema — algorithms/{uuid}.json

Per-session Algorithm v3.7.0 phase history, written by `algorithm-scan.py` at SessionEnd via `lib/algorithm_state.py`:

```json
{
  "session_id": "...",
  "phase": "complete",
  "phase_history": [
    {"phase": "observe", "started": "...", "ended": "..."},
    {"phase": "think",   "started": "...", "ended": "..."}
  ],
  "criteria": [...],
  "anti_criteria": [...],
  "agents_spawned": [...],
  "effort_level": "extended",
  "rework_cycles": 0,
  "created_at": "...",
  "updated_at": "...",
  "completed_at": "..."
}
```

### Schema — work.json

The master session/task index, rebuilt in place by `lib/work_index.py` (driven by `auto-work-creation.py`, `session-summary.py`, and `work-completion-learning.py`):

```json
{
  "sessions": [
    {
      "id": "...",
      "title": "implement login flow",
      "session_id": "...",
      "status": "COMPLETED",
      "created_at": "...",
      "completed_at": "...",
      "tasks": [
        {
          "task_id": "001",
          "slug": "...",
          "tier": "extended",
          "capabilities_used": [...],
          "isc_total": 12,
          "isc_done": 12,
          "isc_anti_total": 0,
          "isc_anti_done": 0
        }
      ]
    }
  ]
}
```

### Crash recovery

If a session crashes before SessionEnd, the per-uuid state files are orphans. Next SessionStart's sweep cleans them:

1. `session-start.py` calls `lib/state_sweep.py`, which walks `state/`.
2. For each per-uuid file, checks mtime.
3. If mtime is older than 6 hours (`STALE_HOURS=6`): delete.
4. Prunes `session-names.json` for orphan UUIDs.

The 6-hour threshold accommodates long-running sessions that sit idle.

---

## Tier 2 — Work

**Path:** `03-rai/memory/work/{slug}/`
**Lifetime:** Indefinite. Persisted until manually deleted.

One directory per task-session ("work dir"). Slug format: `YYYYMMDD_HHMMSS_kebab-task-description` (underscores). A handful are hand-named, e.g. `greene-curriculum-enhance`, `20260614_news-x-collection-fix`.

> **Slug-format note:** the Algorithm spec writes the slug as `YYYYMMDD-HHMMSS_` (dash before the time), but every timestamped work dir on disk uses `YYYYMMDD_HHMMSS_` (underscore). The on-disk form is what `auto-work-creation.py` actually produces.

### Contents per task (EVOLVED — nested under `tasks/`)

The layout is no longer a flat single PRD. Each work dir holds a session-level `META.yaml` plus one or more numbered subtasks under `tasks/`:

```
work/{session-slug}/
├── META.yaml                       ← session-level status ledger (hook-written)
└── tasks/
    └── {NNN}_{task-slug}/          ← e.g. 001_implement-login-flow
        ├── PRD.md                  ← the PRD (frontmatter + Context/Criteria/Decision Log/Verification/Capability log)
        ├── ISC.json                ← {criteria[], antiCriteria[], satisfaction:{satisfied,partial,failed,total}}
        └── THREAD.md               ← running narrative log
```

`ISC.json` and `THREAD.md` are newer artifacts that did not exist at the old flat-PRD layout. `META.yaml` is the authoritative per-dir status marker that `/rai sanity` walks (Check K1).

### META.yaml schema

This is the hook-written 6-field session ledger (NOT the spec's PRD frontmatter):

```yaml
id: 20260614_093000_implement-login-flow
title: implement login flow
session_id: session-uuid
created_at: 2026-06-14T09:30:00+03:00
status: COMPLETED        # ACTIVE → COMPLETED
completed_at: 2026-06-14T11:14:33+03:00
```

### PRD.md schema

See [06-algorithm-and-prd.md](./06-algorithm-and-prd.md) for the full schema. Recap:

- Frontmatter: `type: prd`, `slug`, `tier` (TBD until set), `status`, `created`, `updated`, `capabilities_used: []`.
- Body: Context, Criteria (atomic ISC, 8-12 words, YES/NO verifiable), Anti-criteria (`ISC-A` prefix), Decision Log table, Verification table, Capability invocation log table.
- AI is the sole writer.
- Hooks read-only.

### Spec-vs-reality drift

This is the dominant story for work dirs, and the manual states it plainly. The Algorithm spec mandates a rich AI-written `PRD.md` (8-field frontmatter + 4 sections + ISC checkboxes). On disk: **513 work dirs, 505 with `META.yaml`, 462 with a `PRD.md`**, and effectively none use the spec's exact YAML frontmatter format. The hook-written `META.yaml` is what tooling reads; the PRD is the human/AI-readable record where it exists. PRD count being lower than dir count is expected — older dirs predate the nested `tasks/` layout or are session-only shells.

### Cleanup

Work directories are not auto-cleaned. They live forever unless explicitly deleted. They keep accumulating via `auto-work-creation.py` (one per task-session). If `memory/work/` accumulates noise, `/rai sanity` Check K1 flags dirs whose `META.yaml` is missing or unparseable.

---

## Tier 3 — File memory

**Paths:**
- `03-rai/memory/learning/`
- `03-rai/memory/relationship/`
- `03-rai/memory/security/`
- `03-rai/memory/ai-calls/` (NEW)

**Lifetime:** Indefinite (some 30-day rotations).

### learning/

Captured learnings, rating signals, and system telemetry.

**Layout:**

```
learning/
├── signals/
│   └── ratings.jsonl                       # response ratings (7 lines)
└── system/
    ├── 2026-02/  2026-04/  2026-05/        # low-rating capture files, bucketed by month
    │   └── low-rating-{N}-{ts}.json        # 7 total across these months
    ├── integrity/
    │   └── change-{YYYYMMDD_HHMMSS}.json   # 50 files; 30-day retention, auto-rotated
    ├── counts-history.jsonl                # time-series of vault counts (appended each SessionEnd)
    ├── hook-errors.jsonl                   # structured hook failures
    └── hook-perf.jsonl                     # per-hook latency log (append-only, ~6MB)
```

**Files:**

| File | Format | Written by | Purpose |
|------|--------|------------|---------|
| `signals/ratings.jsonl` | JSONL | rating-capture.py (UserPromptSubmit) | Every rating John gives (drives `/rai upgrade`) |
| `system/low-rating-{N}-{ts}.json` | JSON per turn | rating-capture.py | Low-rated turns captured for learning |
| `system/counts-history.jsonl` | JSONL | update-counts.py | Snapshot counts over time |
| `system/hook-perf.jsonl` | JSONL | lib/hook_timer.py | Per-hook runtime ms; read by `/sanity` J4 / F6 |
| `system/hook-errors.jsonl` | JSONL | lib/hook_errors.py | Hook failures |
| `system/integrity/change-{TIMESTAMP}.json` | JSON per run | integrity-check.py (SessionEnd) | Per-session file-change report |

**Note on the retired REFLECTIONS log:** older docs reference `learning/REFLECTIONS/algorithm-reflections.jsonl`. That file and directory do **not** exist on disk; `learning/` only holds `signals/` and `system/`. Algorithm execution analysis now lives in `state/algorithms/{uuid}.json` (per-session) via `algorithm-scan.py`.

**Retention:** 30-day rolling (`RETENTION_DAYS=30`) for `system/integrity/change-*.json`. `hook-perf.jsonl` and `hook-errors.jsonl` are append-only. Indefinite for the rest.

### relationship/

Daily user-signal notes. Human-readable. CWD-aware.

**Structure:** `relationship/{YYYY-MM}/{YYYY-MM-DD}.md`. Months present: 2026-02 through 2026-06.

**Written by:** `relationship-memory.py` at SessionEnd.

**Format:** Each file gets per-session blocks `### Session {uuid[:8]} ({HH:MM})` followed by tagged signal lines `- [{tag}]{conf} {text}`. Tags come from `_classify()`:

- **`O`** = preference/opinion ("I prefer/like/want/hate…", "always/never/usually…", "my favorite/preferred…")
- **`W`** = world-fact ("I work/live/moved…", "my team/company/project…", "we're using/building…")
- **`B`** = biographical ("today I…", "yesterday", "last night/week/month…")

Capped at 30 signals per session. CWD-aware: one note per project per day. If John works in `~/helm` and `~/projects/foo` on the same day, two notes are created. (Older rendered logs also show a `[medium]` confidence marker.)

### security/

Security validator event logs.

**Structure:** `security/{YEAR}/{MONTH}/security-{YYYYMMDD}.jsonl` (one JSONL file per day). Year dir `2026/` with months `02` through `06`.

**Written by:** `security-validator.py` (a PreToolUse hook, registered 4× in settings for the Bash/Edit/Write/Read matchers).

**Schema (per JSONL line):**

```json
{
  "ts": "2026-06-14T10:14:33+03:00",
  "event": "blocked|confirmed|allowed|alerted",
  "pattern_matched": "rm -rf /",
  "tool": "Bash",
  "command": "rm -rf /tmp/foo",
  "decision": "blocked",
  "uuid": "session-uuid",
  "cwd": "~/helm"
}
```

These are the secret-scanner / git-commit-guard event trail. Indefinite retention.

### ai-calls/ (NEW — not in older ARCHITECTURE.md)

External-LLM call telemetry plus saved synthesis prompts. Written by the external-model skill `/ask-model` (its `call.sh` / `trio-synth.sh`). This is cost/audit telemetry, not session memory.

**Layout:**
- `{YYYY-MM-DD}.jsonl` — per-call telemetry: `ts, model, alias, task, gen_id, prompt_tokens, completion_tokens, total_tokens, cost, prompt_excerpt`.
- Loose `*.txt` dumps — raw model responses.
- `synth-prompts/` — saved trio-synth prompts.

Models seen: `google/gemini-3.1-pro-preview` (alias `gemini`); the skill set also exposes `GPT-5.5` via OpenRouter. See [07-skills-catalog.md](./07-skills-catalog.md) for `/ask-model`.

---

## Tier 4 — Semantic memory

**Path:** `03-rai/semantic-memory/`
**Lifetime:** Forever.

The vector store for cross-session recall.

### Structure

```
semantic-memory/
├── chromadb/                       ← ACTIVE persistent ChromaDB store (~17M)
│   ├── chroma.sqlite3              ← metadata + fulltext + queue
│   └── {uuid}/                     ← per-collection HNSW vector segment dir
│                                     (data_level0.bin, header.bin, length.bin, link_lists.bin)
├── chroma/                         ← STRAY / DEAD empty store (~184k) — see "dead artifacts" below
│   └── chroma.sqlite3
├── pending/                        ← raw session JSONs awaiting /process-sessions (8 files)
│   └── session_{TIMESTAMP}.json
└── scripts/
    └── py-chroma.sh                ← uv-wrapped python 3.12 + chromadb runner
```

> **Dead artifacts (do not document as active):**
> - `semantic-memory/chroma/` (no `db`) is a STRAY empty store created accidentally (commit `abc1234`). The live store is `chromadb/`. It could be deleted; it holds nothing.
> - Inside the live store there are two collections, but only `memories` is real. `session_summaries` (0 embeddings) is an empty legacy collection. `/sanity` C1 keeps only `memories`.

### The active store

- **chromadb version:** `1.5.9`.
- **Embedding model:** `all-MiniLM-L6-v2` (sentence-transformers), **384-dim**, **cosine** space (`hnsw:space=cosine`). This replaced the old chromadb-default embedder — entries are 384-dim, not 768-dim.

| Collection | Dim | Embeddings | Status |
|-----------|-----|-----------|--------|
| `memories` | 384 | ~734 | LIVE — the canonical store |
| `session_summaries` | (unset) | 0 | dead/legacy, empty |

### Pending queue

`save-memory.py` writes session transcripts to `pending/` at SessionEnd. They sit there until `/rai process-sessions` drains them on the Linux coordinator. `PENDING_WARN=20` — the brain warns once the queue exceeds 20 files. (8 are currently queued.)

**Schema — pending/session_{TIMESTAMP}.json (top-level keys):**

```json
{
  "session_id": "session-uuid",
  "timestamp": "...",
  "context": "helm vault — manual writing",
  "transcript_path": "...",
  "cwd": "~/helm",
  "project_name": "helm",
  "duration_minutes": 92,
  "tools_summary": {"Read": 14, "Write": 8, "Edit": 5},
  "files_modified": ["12-system/manual/00-overview.md"],
  "messages": [
    {"type": "user", "message": "..."},
    {"type": "assistant", "message": "..."}
  ]
}
```

`save-memory.py` computes `duration_minutes` (from transcript timestamps), `files_modified` (Edit/Write paths), `tools_summary` (tool counts), `project_name` (from `.git`/`pyproject.toml`/`package.json`/folder), and `context` (via `context_mapping.json`).

### Drain — /rai process-sessions

Skill `03-rai/skills/rai/process-sessions.md` (`allowed-tools: Bash, Read, Glob`; arg `--dry-run`). Run during an active session so Claude summarizes directly — the cron path can't, because a headless Claude CLI subprocess lacks the OAuth session needed to summarize. In production this runs as part of the Linux coordinator's scheduled maintenance.

For each pending file:
1. Read the JSON, extract metadata.
2. **should_save gate:** Plan-mode session → ALWAYS save. Non-plan with ≥4 user messages → save. Non-plan with <4 user messages → archive **without** a ChromaDB save.
3. Compute a **Content Density Score** (duration is ignored): milestones×3 (≤15), code_snippets×2 (≤6), decisions×2, ideas×1.5, key_quotes×1 (≤5), errors×1 (≤3), user_questions×0.5 (≤1.5), user_messages×0.5 (≤10), edit+write tools (≤10), files_modified (≤5). Outcome multiplier: completed 1.0, partial 0.85, blocked 0.9, exploration 0.7.
4. Score → summary length: 0-5→2-3 sentences, 6-15→4-6, 16-25→7-10, 26-40→10-15, 40+→15-20.
5. Auto-infer `type` (build/explore/debug/planning/brainstorm/learning, from tool ratios), `mood` (low/med/high from sentiment), `outcome`, and `continues` (matching project/cwd in last 7 days).
6. Extract the v3 rich fields.
7. Embed and store in ChromaDB collection `memories` via `py-chroma.sh store_to_chromadb.py`.
8. Move the raw JSON to `13-archive/historical-sessions/` (978 archived to date).

### ChromaDB schema

**Collection:** `memories`. The `id` of each embedding is the session UUID.

**Per-entry document text** = the AI-generated summary, with appended `Questions:`, `Ideas:`, `Decisions:`, `Milestones:`, `Errors:` strings so semantic search hits on that content. Built in `store_to_chromadb.py`.

**Per-entry embedding:** 384-dim vector (all-MiniLM-L6-v2).

**Per-entry metadata (three versions layered, all in `store_to_chromadb.py`):**

*v1 (original):* `date` (YYYY-MM-DD), `context` (mapped from cwd), `type` (brainstorm|debug|planning|learning|build|explore), `mood` (low|med|high), `tags`, `ideas`, `decisions`, `open`, `revisit`.

*v2 (metadata):* `duration_minutes`, `project_name`, `files_modified`, `tools_summary`, `outcome` (completed|partial|blocked|exploration), `continues` (prev session id), `related_to` (auto-filled at ≥0.85 similarity), `cwd`.

*v3 (rich extraction):* `key_quotes` (≤5), `code_snippets` (≤3, 200 chars), `commands_executed` (≤5), `errors_encountered` (≤3), `resources_used` (≤5), `milestones` (≤5), `user_questions` (≤3).

`store_to_chromadb.py` always `get_or_create_collection(name="memories", metadata={"hnsw:space":"cosine"})`, computes `related_to` via `find_related_sessions` (query top-5, keep sim ≥ 0.85, ≤3), then `collection.add(ids=[session_id], documents=[doc], metadatas=[meta])`.

### Recall — /recall history

Router `03-rai/skills/recall/SKILL.md` → leaf `history.md` (`allowed-tools: Bash, Read`). All queries run inline python through `py-chroma.sh` against `client.get_collection('memories')`.

```
/recall history --search "what did I work on with the algorithm last month?"
```

Query modes: `(none)` all · `--recent` (30d) · `--search "q"` (semantic top-50) · `--pending` (revisit due ≤ today) · `--project X` · `--type X` · `--related ID` · `--chain ID` (follow `continues` backward + forward) · `--files "pattern"` (fnmatch on `files_modified`) · `--detailed ID` (all fields). The user can drill into a specific session by UUID (read its full transcript from `13-archive/historical-sessions/`).

### The py-chroma.sh wrapper

`scripts/py-chroma.sh`: `exec uv run --quiet --python 3.12 --with chromadb python3 "$@"`. The system python has no chromadb; chromadb wheels target 3.12; uv caches the ephemeral env in `~/.cache/uv`. Usage: `py-chroma.sh script.py [args]` or `py-chroma.sh -c "…"`. Use it for **all** ChromaDB ops; never call `python3` directly.

---

## The write path and the single-writer rule

### SessionEnd hook chain

From `03-rai/config/settings.json`, SessionEnd fires seven hooks **in order** (see [09-hooks-reference.md](./09-hooks-reference.md)):

`save-memory` → `work-completion-learning` → `session-summary` → `relationship-memory` → `update-counts` → `integrity-check` → `algorithm-scan`.

| Hook | Writes |
|------|--------|
| `save-memory.py` | `semantic-memory/pending/session_*.json` (raw transcript + metadata) |
| `work-completion-learning.py` | updates `work.json` index; learning capture |
| `session-summary.py` | marks `META.yaml`/PRD `status: COMPLETED`; deletes this session's `current-work-*`, `tab-titles/{uuid}`, `algorithms/{uuid}`; prunes `session-names.json` |
| `relationship-memory.py` | `memory/relationship/YYYY-MM/YYYY-MM-DD.md` |
| `update-counts.py` | refreshes counts; appends `learning/system/counts-history.jsonl` |
| `integrity-check.py` | `learning/system/integrity/change-*.json` (30-day rotation) |
| `algorithm-scan.py` | `memory/state/algorithms/{uuid}.json` |

> **Known bug:** `update-counts.py` targets a non-existent `03-rai/settings.json` (the real file is `03-rai/config/settings.json`), so the inline counts block in settings is frozen at 2026-04-18 and is stale. The `counts-history.jsonl` append still works. See [17-config-and-security.md](./17-config-and-security.md).

### Single-writer rule (SYNC-ARCHITECTURE.md, adopted 2026-06-13)

This is the load-bearing rule. **The Linux box (`pc`, Tailscale `100.64.0.2`) is the sole coordinator: the only machine that writes `origin` on GitHub AND the only ChromaDB writer.** The Mac (`100.64.0.3`) is a passive replica reached over keyless Tailscale SSH; it never touches GitHub. Authoritative doc: `03-rai/SYNC-ARCHITECTURE.md`. See [17-config-and-security.md](./17-config-and-security.md).

The consequence for memory: **SessionEnd on either machine writes only the `pending/` queue (plus the local file-memory tiers). The drain into ChromaDB is a separate, Linux-only `/process-sessions` step.** A claim that "SessionEnd writes ChromaDB" is wrong. Because Linux is the only writer, the binary store never hits a merge conflict.

Coordinator pipeline (`run-maintenance-ubuntu.sh`, systemd timer @ 04/10/16/22:00):

```
0. origin fetch + merge --ff-only        (was pull --rebase; changed in abc1234 to end the binary-conflict jam)
1. capture_mac (ssh mac commit; fetch mac; merge -X ours — Linux wins, keeps its ChromaDB)
2. merge-collisions
3. process-sessions  ← drains BOTH machines' pending queues into ChromaDB (Linux only)
4. git commit + push ← the only push anywhere
5. refresh_mac (fast-forward the Mac)
```

Two supporting mechanisms:
- `.gitattributes` rule `03-rai/memory/**/*.jsonl merge=union` — append-only logs never lose entries on merge.
- The SessionStart recall hook opens the ChromaDB store and mutates `chroma.sqlite3` / `*.bin` even on a pure read. So `mac-sync.sh` discards read-induced `chromadb` drift (`git reset`/`checkout -- chromadb`) to keep the Mac a clean read-only replica (abc1234, 2026-06-14).

Brain-repo policy (commit `abc1234`): **nothing informational is gitignored** — sync is fixed via mechanism, never via ignores.

---

## Memory loading at SessionStart

When `session-start.py` runs, it reads memories conditionally based on CWD.

| CWD | Memory scope |
|-----|--------------|
| Inside `~/helm` | Full memory scope (all collections, all dates) |
| Other (e.g., `~/projects/foo`) | 7-day rolling window (recent context only) |

This keeps non-helm sessions fast — code work in a project doesn't need the full vault history loaded.

`session-start.py` also rebuilds `identity-cache.json` (a digest of every identity `.md` file, keyed by the newest mtime across them) and self-heals: if the recorded mtime differs from the filesystem newest, it reloads. On a fresh box the recall hook may log `NotFoundError: Collection [memories] does not exist` — handled gracefully.

## What is NOT in memory

- The user transcripts in raw form during the session (the harness owns those).
- The model's own internal reasoning (not preserved between sessions).
- File content from the vault (read on-demand each session).
- Skill definitions (read at invocation, not preloaded).

Memory is for cross-session signal preservation, not full context replay.

## Cleanup and pruning

| What | When |
|------|------|
| State files (`memory/state/{current-work,tab-titles,algorithms}/{uuid}`) | Cleaned at SessionEnd; orphans swept at SessionStart (>6h) |
| `session-names.json` ghosts | Pruned at SessionStart sweep |
| Pending session JSONs | Moved to `13-archive/historical-sessions/` after `/rai process-sessions` (Linux) |
| `learning/system/integrity/change-*.json` | 30-day rotation |
| `learning/system/hook-perf.jsonl` / `hook-errors.jsonl` | Append-only (no rotation) |
| `relationship/{YYYY-MM}/*.md` | Indefinite |
| `security/{YYYY}/{MM}/*.jsonl` | Indefinite |
| `ai-calls/` | Indefinite |
| `work/{slug}/` and friends | Indefinite (manual delete only) |
| ChromaDB | Indefinite |
| `13-archive/historical-sessions/` | Indefinite |

## Schema migrations

When the memory schema changes (e.g., the v1→v2→v3 layering on ChromaDB metadata), no automatic migration runs. The new schema is applied only to new entries. Existing entries retain their old schema; readers must handle missing fields gracefully.

If a breaking schema change is needed, document the migration in a one-off skill or a hook upgrade. Never silently break existing memory.

## Backups

The brain has no backup system of its own. Backup is delegated to git (text files in the repo) and to the user's OS-level backup (Time Machine for ChromaDB and other binary content).

To back up everything:
- `git push` for text content (notes, PRDs, code) — happens automatically on the Linux coordinator.
- Time Machine or rsync for `semantic-memory/chromadb/`.

## Memory inspection commands

| Want to know | Run |
|--------------|-----|
| Active per-session state files | `ls 03-rai/memory/state/` |
| All tasks ever | `ls 03-rai/memory/work/` |
| Recent sessions (pending) | `ls 03-rai/semantic-memory/pending/` |
| Today's relationship note | `cat 03-rai/memory/relationship/$(date +%Y-%m)/$(date +%Y-%m-%d).md` |
| Recent ratings | `tail -20 03-rai/memory/learning/signals/ratings.jsonl` |
| Recent integrity reports | `ls 03-rai/memory/learning/system/integrity/` |
| Recent security events | `tail -50 03-rai/memory/security/$(date +%Y)/$(date +%m)/security-$(date +%Y%m%d).jsonl` |
| External-LLM call cost | `tail -20 03-rai/memory/ai-calls/$(date +%Y-%m-%d).jsonl` |
| ChromaDB embedding count | `03-rai/semantic-memory/scripts/py-chroma.sh -c "import chromadb; c=chromadb.PersistentClient('03-rai/semantic-memory/chromadb'); print(c.get_collection('memories').count())"` |
| Master work index | `cat 03-rai/memory/state/work.json | jq '.sessions | length'` |
| Full brain healthcheck | `/rai sanity` |

## Memory healthcheck — /rai sanity

`03-rai/skills/rai/sanity.md` runs an 11-tier (A–K) end-to-end brain healthcheck (`--quick`, `--fix`, `--baseline`). Memory-relevant tiers:

| Tier | Asserts |
|------|---------|
| A — Data safety | unpushed=0; no baseline metric dropped >5% (md_count, pending_count, chromadb_bytes) |
| B — Environment | chromadb import works; `py-chroma.sh` is executable |
| C — ChromaDB integrity | only `memories` collection; populated+fresh; ≥5/month coverage; write→read→delete round-trip; semantic query top-sim >0.3 |
| D — Pipeline | pending <10 & `pending-summaries`==0; capture live (<48h); STATE/RELATIONSHIP writes fresh; SessionStart shows Who/Mission/Recent Memory |
| F6 / F8 | hook-perf errors==0; identity-cache mtime drift ≤1s |
| I3 | algorithm state newest <7d (`algorithm-scan.py` firing) |
| J4 | every registered hook seen in hook-perf within 7d |
| K1 / K2 | every work dir has parseable `META.yaml` with `status:`; settings counts vs filesystem drift ≤10% |

Verdicts: **HEALTHY** (all PASS, ≤2 WARN), **DEGRADED** (FAIL in E/F/G/H/J1-3/K), **BROKEN** (FAIL in A/B/C/D/I/J4/J5 — stop everything).

## Common memory issues and fixes

| Issue | Cause | Fix |
|-------|-------|-----|
| `pending/` accumulates | `/rai process-sessions` not run (or Linux coordinator down) | Run `/rai process-sessions` on the coordinator |
| ChromaDB not updating on Mac | Mac is read-only replica by design | Correct — only Linux writes ChromaDB; wait for next coordinator cycle |
| Orphan `current-work-*` files | Session crashed | Wait for next SessionStart sweep (>6h) or manually delete |
| `session-names.json` has ghost UUIDs | Same | Same — auto-pruned at next SessionStart |
| Identity not in context | Cache stale | Touch identity files: `find 03-rai/identity 02-ana/identity -type f -exec touch {} +` |
| Identity loaded but wrong | Cache pointing at deleted file | Delete `memory/state/identity-cache.json`, restart session |
| ChromaDB query returns nothing | Pending not drained, or wrong collection | Check `pending/`; query `memories` (not `session_summaries`); run `/rai process-sessions` |
| ChromaDB query slow | Collection size + cold cache | First query is slow; subsequent are warm |
| Counts block stale | `update-counts.py` writes to wrong path | Known bug; counts-history.jsonl is the live record — see [17-config-and-security.md](./17-config-and-security.md) |
| Work directory exists but no PRD | Expected — 462 PRDs / 513 dirs | Normal; `META.yaml` is the authoritative marker |

Full troubleshooting in [20-troubleshooting.md](./20-troubleshooting.md).
