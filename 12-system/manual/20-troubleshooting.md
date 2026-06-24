# 20 — Troubleshooting

Last updated: 2026-06-14.

Common failures across the brain. Symptom, cause, fix. CLAUDE.md (root + per-folder) and the subsystem snapshots in `03-rai/SYNC-ARCHITECTURE.md` are the live source of truth; when this chapter and a CLAUDE.md disagree, CLAUDE.md wins.

The two log files you will reach for most often:
- `03-rai/memory/learning/system/hook-errors.jsonl` — structured hook failures (every hook wraps in `lib/hook_errors.py`).
- `03-rai/memory/learning/system/hook-perf.jsonl` — per-hook latency (every hook wraps in `lib/hook_timer.py`).

And two directories worth scanning when something feels off:
- `03-rai/memory/learning/system/integrity/` — file-change records (`change-*.json`, 30-day rotation), written by `integrity-check.py`.
- `03-rai/memory/security/YYYY/MM/` — the `security-validator.py` event trail.

The canonical settings file is `03-rai/config/settings.json` (reached via the symlink `~/.claude/settings.json`). There is no `03-rai/settings.json` — see the "update-counts writes to a non-existent path" failure mode below.

## Session start failures

### Identity not loaded into context

**Symptom:** Rai doesn't seem to know basic facts about John (goals, projects, who-i-am).

**Causes:**
- `session-start.py` timed out (>8s).
- Identity cache is stale and pointing at deleted files.
- `02-ana/identity/` or `03-rai/identity/` was moved or renamed.

**Fix:**
1. Check stderr from session-start.py: look at the output of last SessionStart in the terminal. Healthy output ends with a status line like `[rai] memories=N identity=cached|fresh|none [...] [skills_bad=N]`.
2. Delete the cache to force re-read: `rm 03-rai/memory/state/identity-cache.json`. The cache is keyed by the newest mtime across all identity `.md` files and self-heals, but deleting it forces a clean reload.
3. Touch identity files to bump mtimes: `find 03-rai/identity 02-ana/identity -name '*.md' -exec touch {} +`. Expected counts: `02-ana/identity/` has 13 auto-loaded `.md` files, `03-rai/identity/` has 4 (`ai-steering-rules`, `coding-format`, `dai-identity`, `response-format`). `security-patterns.yaml` is in `03-rai/identity/` but is NOT auto-loaded (non-`.md`).
4. Restart the Claude Code session.
5. If the timeout is recurring, read `03-rai/memory/learning/system/hook-perf.jsonl` for slow operations (`session-start` body p50 ~559ms, but the uv/chromadb wrapper cold-start adds more on top).

### "Collection [memories] does not exist" on a fresh box

**Symptom:** SessionStart logs `NotFoundError: Collection [memories] does not exist` (sometimes alongside a `BrokenPipeError`).

**Cause:** `session-start.py` tried to load memories from ChromaDB before any embedding has been written on this machine. The `memories` collection in `03-rai/semantic-memory/chromadb/` is created lazily on first write, and ChromaDB is single-writer (only the Linux coordinator writes it). On a fresh checkout — or before the first `/rai process-sessions` drain — the collection simply isn't there yet.

**Fix:**
- Nothing to fix. This is an expected, handled state: `load_memories` catches it and returns `[], 0`, so SessionStart still completes and identity still loads. The `BrokenPipeError` (stdout closed early) is likewise non-fatal.
- It resolves itself once the Linux coordinator runs `/rai process-sessions` and the collection is populated (then synced down). If you want to confirm the store is alive, run `/rai sanity` (tier C checks the `memories` collection end-to-end).

### SessionStart slow (5+ seconds)

**Symptom:** The first prompt waits noticeably before Rai responds.

**Causes:**
- ChromaDB read taking long (large collection, cold cache).
- Identity files have grown large.
- State sweep finding many orphans.

**Fix:**
1. Profile via `03-rai/memory/learning/system/hook-perf.jsonl` entries. The two slow hooks are both SessionStart-only: `check-version.py` (p50 ~897ms, dominated by the `npm view` network call) and `session-start.py` (p50 ~559ms plus the uv/chromadb wrapper cold-start). Everything in the prompt/tool hot path is single-digit ms.
2. If ChromaDB is the culprit: nothing to fix on the user side; it gets faster after the first read of the day. The first read also pays the `py-chroma.sh` uv cold-start (it builds an ephemeral python-3.12 + chromadb env).
3. If `check-version.py` is the culprit: it is a network call (`npm view @anthropic-ai/claude-code version`); a slow or offline network shows up here. It exits immediately for subagents and has a 5s SIGALRM cap, so it cannot hang the session.
4. If identity is the culprit: prune `02-ana/identity/*.md` files. Each should be focused; consolidate or split if any has grown unbounded.
5. If sweep is the culprit: many crashed sessions accumulated. Manually `rm 03-rai/memory/state/{current-work-*,tab-titles/*,algorithms/*}` if you trust they are dead.

### check-version.py warning

**Symptom:** Console shows "Brain version mismatch" or similar at SessionStart.

**Cause:** The harness expects a different algorithm version than what is current.

**Fix:**
1. Read `03-rai/algorithm/latest` to confirm current version.
2. If you intentionally changed versions, update the version reference in CLAUDE.md.
3. If unintentional, restore the previous algorithm symlink.

---

## Tool call failures

### Bash command blocked unexpectedly

**Symptom:** "Refused: matches blocked pattern" on a command that should be safe.

**Cause:** A `bash.blocked` (substring → exit 2) or `bash.confirm` (regex → ask) pattern in `03-rai/identity/security-patterns.yaml` matched too broadly. The validator loads patterns via a cascade: `identity/security-patterns.yaml` (user, loaded first) → `03-rai/security-patterns.example.yaml` (fallback) → a hardcoded minimal dict if PyYAML is missing.

**Fix:**
1. Read the validator log: `tail -1 03-rai/memory/security/$(date +%Y)/$(date +%m)/security-$(date +%Y%m%d).jsonl`. Each line records `timestamp, event, tool, detail, blocked`.
2. Identify the matched pattern. `blocked` is a substring match (10 patterns: `rm -rf /`, `mkfs`, `gh repo delete`, etc.); `confirm` is regex (8 patterns: force push, `reset --hard`, `DROP DATABASE`, `terraform destroy`, etc.).
3. Refine the pattern to be more specific in `security-patterns.yaml` (the user file), not the example fallback.
4. Or, if the command is genuinely safe in this context, override via the user prompt and proceed.

Note: `security-validator.py` fails OPEN — any internal error (bad stdin, missing dependency) lets the command through rather than deadlocking the agent. So a "blocked" verdict is a deliberate match, not a crash.

### Secret pattern false positive on a placeholder

**Symptom:** `git commit` blocked with a per-file category summary because staged content matches a pattern in `03-rai/.pai-protected.json`.

**Cause:** `security-validator.py` runs `lib/protected_scan.scan_staged_git_files()` whenever the Bash command matches `\bgit\s+commit\b`. Documentation examples, test fixtures, or — commonly — Arabic prose (the `locale_identity` category catches any Arabic run ≥4 chars) or AI-attribution strings tripped one of the 15 categories.

**Fix:**
1. Inspect the staged files: `git diff --cached`. Or re-run the scanner directly to see exactly what matched: `python3 -m hooks.lib.protected_scan --staged` (run from `03-rai/`).
2. Identify the false-positive content.
3. Prefer the built-in exception mechanism over loosening a regex:
   - Add an allowed-prefix phrase on the same line (the `exception_contexts.allowed_prefixes` list suppresses matches sharing a line with `# Example:`, `placeholder`, `YOUR_`, `EXAMPLE`, `localhost:`, `127.0.0.1`, etc.).
   - For whole files that should never be scanned (e.g. a corpus, a memory subtree), add the path/glob to `.pai-protected.json` `exception_files` (~140 entries already cover `08-bawaba/**`, the Helios backend tree, all memory subtrees, etc.).
4. Retry the commit.

The scanner fails OPEN: if `protected_scan` itself errors, the commit is logged as an alert and allowed. Do NOT widen the allow-lists just to push a commit, and never bypass with `git commit --no-verify` — when the validator blocks a legitimate-but-sensitive file, skip it and warn rather than forcing it through. (Note: do NOT edit `.pai-protected.json` to widen allows purely to land a commit; `autoMode` denies that anyway.)

### Skill blocked by skill-guard

**Symptom:** A `Skill("...")` invocation is blocked with a `{"decision":"block",...}` verdict.

**Cause:** `skill-guard.py` (PreToolUse on Skill) maintains a small `BLOCKED_SKILLS` set — currently just `{"keybindings-help"}`. It exists because `keybindings-help` is first in the skills list and false-fires on aggressive BLOCKING-REQUIREMENT language; the guard stops that misfire.

**Fix:**
- If you genuinely intended `keybindings-help`, invoke it explicitly and the user can confirm.
- If a different skill is being blocked unexpectedly, inspect `03-rai/hooks/skill-guard.py` and its `BLOCKED_SKILLS` set.

### .skill-lock.json (externally-installed skills)

**Symptom:** Confusion about `03-rai/config/.skill-lock.json`.

**Cause:** This is NOT a per-session runtime lock. It is the version-pin lockfile (version 3) for externally-installed skills — e.g. `beautiful-mermaid` from `intellectronica/agent-skills`. It records what was installed from where, not a mutex held by a session.

**Fix:**
- Nothing routine. Inspect with `cat 03-rai/config/.skill-lock.json | jq`. Only edit it when intentionally adding/removing an externally-sourced skill.

### Tool call refused: zero-access path

**Symptom:** "Refused: path is zero-access."

**Cause:** The path matches a `zeroAccess` rule in `security-patterns.yaml`.

**Fix:**
1. Confirm the path is genuinely sensitive (most are: `~/.ssh/`, `~/.aws/`).
2. If genuinely sensitive: do not bypass; find another way.
3. If false positive (rare): adjust the rule to be more specific.

---

## Algorithm and PRD issues

### ISC count gate fails repeatedly

**Symptom:** OBSERVE phase keeps failing the ISC count gate, even after decomposition.

**Causes:**
- Effort tier is too aggressive for the actual work.
- Compound criteria not being properly split.
- Task is genuinely too narrow for the chosen tier.

**Fix:**
1. Re-read the Splitting Test (chapter 06). Apply each test rigorously to each criterion.
2. If criteria genuinely cannot decompose further: the tier is wrong. Drop to the next tier down. Update the PRD frontmatter.
3. Document the tier downgrade in the PRD's `## Decisions` section.

### PRD not updating during EXECUTE

**Symptom:** Tasks complete but the PRD's checkboxes stay unchecked.

**Cause:** The model is forgetting to edit the PRD inline as criteria pass. There is no hook safety net.

**Fix:**
- The model is responsible. Discipline: at each completed criterion, immediately Edit the PRD to mark `- [x]` and update `progress: N/M`.
- For Extended+ tasks, periodic context compaction can drop this discipline. Re-read the PRD at each phase boundary to re-anchor.

### Voice announcements skipped

**Symptom:** No voice plays at phase transitions.

**Causes:**
- The notify endpoint at `http://localhost:8888/notify` is not running.
- A subagent (background) attempted to emit voice and was correctly suppressed (only the primary agent emits).
- The voice curl is timing out.

**Fix:**
1. Confirm the local notify service is running. The Algorithm posts to `http://localhost:8888/notify` (voice_id `fTtv3eikoepIosk8dTZ5`).
2. If service down: start it. Voice announcements are part of the phase ritual.
3. If subagent: confirm only the primary agent is supposed to emit. This is correct behavior — subagents must never call the notify endpoint.

Separately, the SessionEnd/Stop notification channels (`lib/notifications.py` → ntfy/Discord/Twilio) are all DISABLED in the current config (routing map present, every transport `enabled:false`). So absence of an end-of-task push is expected, not a fault.

### Phantom capability — selected but never invoked

**Symptom:** The Algorithm reports "selected /research" in OBSERVE but never invoked it.

**Cause:** The model wrote prose that looked like a research output without actually calling the Skill tool.

**Fix:**
- This is a CRITICAL FAILURE per the spec.
- Either: invoke the capability now (in BUILD/EXECUTE/VERIFY).
- Or: remove it from the selected list with a documented reason.
- If this is recurring, the problem is discipline. Re-read the spec section "Min Capabilities — CRITICAL FAILURE rule."

### Algorithm time budget exceeded

**Symptom:** The Algorithm takes far longer than the tier's budget.

**Causes:**
- Wrong tier chosen in OBSERVE.
- Compaction not happening at phase boundaries.
- Capabilities are too slow (e.g., research with too many sources).

**Fix:**
1. Auto-compress: the spec allows reducing remaining phase work or downgrading tier with note.
2. For future tasks: bias toward smaller tiers. The cost of a too-small tier is just one downgrade; the cost of a too-large tier is wasted time.
3. Compact context at every phase boundary (Extended+).

---

## Memory issues

### pending/ accumulates without drain

**Symptom:** `ls 03-rai/semantic-memory/pending/` shows many session JSONs (SessionStart warns "run /process-sessions" once the count reaches 20 — `PENDING_WARN=20`).

**Cause:** The pending queue is drained only by `/rai process-sessions`, and that drain runs ONLY on the Linux coordinator (it is the sole ChromaDB writer). SessionEnd writes a raw transcript into `pending/`; it does NOT write ChromaDB. The drain is a separate step.

**Fix:**
- On the Linux coordinator the drain runs automatically inside the maintenance pipeline (systemd `rai-maintenance.timer` @ 04/10/16/22:00). If pending keeps growing, the coordinator's maintenance run is failing — check its logs at `~/.local/state/rai-maintenance/` (outside the repo).
- To drain manually during an active session, run `/rai process-sessions`. It summarizes each pending file, inserts one embedding into the `memories` collection, then moves the raw JSON to `13-archive/historical-sessions/`.
- Do NOT run the drain on the Mac. The Mac is a read-only replica; ChromaDB writes must happen only on Linux or you reintroduce the binary-conflict jam (see the sync section below).
- Note the should_save gate: a Plan-mode session always saves; a non-plan session needs ≥4 user messages, otherwise it is archived WITHOUT a ChromaDB embedding. A pending file that "disappears without showing up in recall" was simply too trivial to embed — that is correct behavior, not a bug.

### Orphan state files in memory/state/

**Symptom:** `ls 03-rai/memory/state/` shows many `current-work-{uuid}.json` files.

**Cause:** Sessions crashed before SessionEnd ran, leaving orphans.

**Fix:**
- Wait for next SessionStart — the sweep cleans orphans older than 6 hours.
- If you need to clean now: `rm 03-rai/memory/state/{current-work-*,tab-titles/*,algorithms/*}` (only delete files you trust are dead).

### session-names.json has ghost UUIDs

**Symptom:** `cat 03-rai/memory/state/session-names.json | jq` shows entries for sessions that no longer exist.

**Cause:** Same as orphan state files — SessionEnd didn't fire.

**Fix:**
- Auto-pruned at next SessionStart.
- To clean now: edit the file, remove the ghost entries.

### Identity cache stale

**Symptom:** Rai is using an outdated version of an identity file you just edited.

**Cause:** `session-start.py` cached the digest, and the cache validator missed the update (rare).

**Fix:**
- `rm 03-rai/memory/state/identity-cache.json`. Restart the session.

### ChromaDB query returns nothing

**Symptom:** `/recall history "..."` returns no results.

**Causes:**
- Pending sessions not yet drained (session not yet in ChromaDB).
- Query phrase doesn't semantically match any stored summary.
- ChromaDB is corrupted.

**Fix:**
1. Check `pending/` count. If sessions are pending: `/rai process-sessions` first.
2. Try a simpler or different query.
3. If suspected corruption: see "ChromaDB recovery" below.

### ChromaDB query slow

**Symptom:** `/recall history` takes 5+ seconds for a small collection.

**Cause:** Cold cache. ChromaDB lazy-loads HNSW indices.

**Fix:**
- First query of the day is slow. Subsequent are warm.
- If always slow: collection has grown very large. Consider rotating: archive old summaries, keep recent.

---

## Knowledge and template issues

### MOC drift

**Symptom:** Topic Notes exist in a domain but the corresponding MOC doesn't list them.

**Fix:**
- Run `/knowledge audit-moc` for the affected domain. It reports drift and suggests updates.
- Update the MOC by adding the missing wiki-links to the right section.

### Topic Note missing Simplicity Theorem

**Symptom:** A Topic Note in `10-knowledge/` has no Simplicity Theorem section.

**Fix:**
- This violates the rule. Add the Simplicity Theorem section.
- Apply the constraints: one sentence, simple words, captures the "why it exists." 12-year-old test.

### Wiki-link to a missing note

**Symptom:** `[[note-name]]` doesn't resolve in Obsidian.

**Causes:**
- The note doesn't exist.
- The note was renamed or moved.

**Fix:**
- Either create the missing note, or fix the wiki-link to point to the real note name.

### Note created without a template

**Symptom:** A note in `10-knowledge/` or `09-ideas/` has unique structure not matching any template.

**Fix:**
- Re-do using the right template from `12-system/templates/`.
- Move the original content into the template structure.

---

## Hook issues

### Hook timeout

**Symptom:** A hook took too long and was cut off.

**Cause:** Each hook has its own SIGALRM watchdog and exits 0 on timeout (hooks fail safe). The caps are: 5s default; 8s for `session-start.py`; 10s for `stop-orchestrator.py` and `algorithm-scan.py`.

**Fix:**
1. Read `03-rai/memory/learning/system/hook-perf.jsonl` to see which hook is slow and by how much.
2. Identify the slow hook. In practice only the two SessionStart hooks are ever near their cap (`check-version.py`, `session-start.py`).
3. Reduce the work the hook does. The SIGALRM caps are inline in each hook (`signal.alarm(N)`), not in a central config — change them at the hook if a cap is genuinely too tight.
4. A timed-out hook does not fail the session — it just skips its work for that event. `check-version.py`'s `npm view` call is the usual offender and it is purely advisory.

### Hook silently failing

**Symptom:** Expected hook behavior is missing (e.g., session not auto-named).

**Fix:**
1. Read `03-rai/memory/learning/system/hook-errors.jsonl` for recent errors (each line: hook name, error type, message, traceback, timestamp).
2. Confirm the hook is actually firing: `/rai sanity` tier J4 asserts every registered hook appears in `hook-perf.jsonl` within 7 days. A hook missing there is silently dead.
3. Fix the underlying cause (often a path issue, missing dependency, or a permissions problem). Since the 2026-06-09 cross-platform fix, hook commands self-resolve via `$HOME/helm/03-rai/...` and `lib/paths.py` (no `PAI_DIR` env var) — a broken path on one machine usually means a hardcoded `/Users/...` crept back in.
4. Re-trigger by starting a new session.

### Auto-work-creation over-firing

**Symptom:** `03-rai/memory/work/` has many empty directories from bare prompts.

**Cause:** The detection heuristic is too eager.

**Fix:**
- Run `/rai sanity` to identify empty work directories.
- Manually delete: `find 03-rai/memory/work -maxdepth 1 -mindepth 1 -type d -empty -delete`.
- Tighten the heuristic in `auto-work-creation.py` if this is recurring.

### Frozen counts block — update-counts writes to a non-existent path (KNOWN BUG)

**Symptom:** The `counts` block in `03-rai/config/settings.json` (and anything that reads it) shows stale numbers — `skills: 66, hooks: 22, ratings: 4, work: 27, learnings: 16`, `updatedAt: 2026-04-18`. These never change no matter how many sessions end. The real numbers today are different (e.g. there are 19 `.py` hook files, not 22; ~35 top-level skill entries, not 66).

**Cause:** This is a real, currently-live bug. `update-counts.py` (SessionEnd hook #5) recounts correctly, but writes the result via `lib/paths.get_settings_path()`, which returns `03-rai/settings.json` — a file that DOES NOT EXIST. The canonical settings file is `03-rai/config/settings.json`. So the write silently targets a non-existent path and the `counts` block in the real file is frozen at its last good write (2026-04-18). The append to `03-rai/memory/learning/system/counts-history.jsonl` still works, so the time-series keeps growing even though the cached block does not.

**Fix:**
- Treat the `counts` block in `config/settings.json` as STALE. Do not quote it as authoritative for skill/hook/work counts. The true counts come from the filesystem: count dirs with a `SKILL.md` for skills, `*.py` in `03-rai/hooks/` for hooks.
- The proper fix is a one-line correction in `lib/paths.py` so `get_settings_path()` points at `config/settings.json`. Until that lands, the block stays frozen by design.
- `/rai sanity` tier K2 already flags this (settings counts vs filesystem, drift > threshold). The fresh time-series in `counts-history.jsonl` is the reliable record.

---

## Skill and agent issues

### Skill not found

**Symptom:** `Skill("name")` errors with "skill not found."

**Causes:**
- Misspelled name.
- Skill folder doesn't exist.
- The skill is a sub-skill (must be invoked via its router).

**Fix:**
1. Confirm spelling against `03-rai/skills/MANIFEST.md`.
2. Check `ls 03-rai/skills/` for the folder.
3. If it's a sub-skill, invoke the router instead and let it dispatch.

### Agent not found

**Symptom:** `Task(subagent_type: "name")` errors with "agent not found."

**Causes:**
- Misspelled name.
- Agent file doesn't exist.

**Fix:**
1. Confirm spelling against `03-rai/agents/MANIFEST.md`.
2. Check `ls 03-rai/agents/` for the file.

### Agent attempts a tool not in its allow-list

**Symptom:** An agent tries a tool it isn't permitted to use.

**Cause:** The agent's frontmatter `permissions.allow` doesn't include that tool. Allow-lists VARY per agent — there is no single uniform block. For example: architect/designer/writer/pentester allow 9 tools; artist 8 (no Edit); engineer 8 (no WebSearch); algorithm 7 (no web); researcher 6 (no Bash/Write/Edit); qa-tester and reviewer 5 each (no Write/Edit/Web).

**Fix:**
- Either: have the agent use a different approach within its allow-list.
- Or: update the agent file (`03-rai/agents/{name}.md`) to add the permission.

Note: `agent-execution-guard.py` (PreToolUse on Task) is WARN-ONLY. It never blocks, does not validate that the agent exists, does not read frontmatter, and does not enforce permissions — it only suggests `run_in_background: true` on non-fast Task spawns. So a permission problem surfaces at the agent's actual tool call, not at spawn time.

---

## Capture pipeline issues

### /triage process-inbox doesn't personalize well

**Symptom:** Items get rated A or D when they should be B or C.

**Cause:** `02-ana/identity/goals.md` or `02-ana/identity/who-i-am.md` is stale or vague.

**Fix:**
- Run `/life telos` to update the identity files.
- Re-run `/triage process-inbox`.

### Items keep ending up wrong-routed

**Symptom:** Items go to the wrong destination folder repeatedly.

**Cause:** The routing matrix in `triage/process-inbox.md` may be out of sync with how John categorizes things.

**Fix:**
- Update the SKILL.md to refine the routing logic.
- Add edge cases (e.g., "if X looks like Y, route to Z").

---

## Idea pipeline issues

### Idea graduation creates the wrong PRD

**Symptom:** `/ideas graduate` produces a PRD that doesn't reflect the Tree's content.

**Cause:** The Tree didn't have enough content for the graduate skill to work with.

**Fix:**
- Promote the Plant to Tree more thoroughly first.
- Manually fill in the PRD post-graduation.

### Lineage broken (derived_from / spawned mismatch)

**Symptom:** Idea A says it spawned Idea B, but Idea B doesn't say it derived from A.

**Cause:** Manual lineage tracking missed one direction.

**Fix:**
- Run `/ideas derive` — it surfaces broken lineage.
- Manually update the missing direction.

---

## Project lifecycle issues

### kitchen/ directory still exists after move to active/

**Symptom:** Both `05-projects/kitchen/{name}/` and `05-projects/active/{name}/` exist.

**Cause:** Forgot to remove kitchen after moving to active.

**Fix:**
- Confirm everything from kitchen has been moved to active or to `~/projects/{name}/`.
- Delete the kitchen folder: `rm -rf 05-projects/kitchen/{name}`.

### Code in 05-projects/active/{name}/

**Symptom:** A code file landed in the vault inside `05-projects/active/`.

**Cause:** Forgot to put code in `~/projects/{name}/`.

**Fix:**
- Move the code to `~/projects/{name}/` (outside the vault).
- Keep only non-code artifacts (PRD, design, decisions, notes) in `05-projects/active/{name}/`.

---

## News digest issues

The skill is `/news-digest` (v5.6). Daily output → `08-bawaba/daily/YYYY-MM-DD.md`; weekly "Bawaba Weekly" → `08-bawaba/weekly/YYYY-WWW.md`. Scheduled runs are HEADLESS via `claude -p`, driven by Ubuntu systemd timers (`news-daily.timer` @ 03:00, `news-weekly.timer` Sat @ 07:00) through `03-rai/skills/news-digest/scheduled/run-news-ubuntu.sh`. The Mac launchd/WezTerm path is retired.

### Interactive /news aborts: X collection failed

**Symptom:** An interactive `/news` run stops because X collection failed.

**Cause:** Per the hard rule, no X means no digest. The primary X collector is now `_collect_x_headless.py` (headless Chrome over raw CDP; exit `0` ok / `2` chrome-or-devtools failure / `3` not logged in — and on `3` it writes `x_LOGIN_FAILED.json`). The account `@johndoe` is X Premium, so the old ~1,000/day read cap is no longer the wall.

**Fix:**
1. Read the collector exit / status. Check `.runs/YYYY-MM-DD/x_headless_status.json` (live progress) and, on a dead login, `x_LOGIN_FAILED.json`.
2. Fix the underlying cause: re-login the Chrome profile (exit 3), or a stale headless Chrome holding the CDP port (the script kills by port — `fuser -k 9223/tcp`; never `pkill -f` on the Ubuntu box, the harness shell's argv self-matches and it kills its own shell).
3. Re-run `/news`. The Chrome-MCP scroller ladder still exists as a degraded-day fallback if the headless script's Chrome won't launch.

For an INTERACTIVE run there is no override — the X-dealbreaker rule is hard. (See the scheduled-mode exception below.)

### Scheduled news run produced nothing / hung at the watchdog

**Symptom:** The 03:00 (or Sat 07:00) run left no digest, or the systemd job ran the full 120-minute watchdog and was killed.

**Causes:**
- Background-task trap: under `claude -p` the process terminates the instant the turn ends and background completion does NOT re-invoke. If the agent ended its turn to "wait" for a background X collector, systemd killed the cgroup → zero output. (This is the 2026-06-12 bug.)
- Chrome pairing: while the Mac is signed into the same Claude account it appears as a remote browser; the daily preflight (`list_connected_browsers`, asserts `isLocal:true`) must pin the local one.
- A one-time interactive permission prompt (the reason headless `-p` replaced WezTerm `claude --chrome` in the first place).

**Fix:**
1. Read the run log at `~/.local/state/news-digest/logs/` (OUTSIDE the repo — kept out so per-run logs never create commit churn).
2. The runner auto-retries ONCE on failure (`RETRY_DELAY_SEC` default 600s) with a budget-protecting retry prompt that REUSES the same-day `.runs/` dumps rather than re-collecting — re-scraping X burns the next attempt's read budget. If both attempts fail, the digest genuinely didn't ship that day; gaps are acceptable per `08-bawaba/CLAUDE.md`.
3. Scheduled-mode override (v5.2): when the launch prompt declares SCHEDULED MODE, "ship a digest" outranks the time rule AND the X-dealbreaker rule — a partial-coverage digest beats no digest, because zero output is the only unacceptable outcome under the watchdog. So a thin scheduled digest is the system working as designed, not a failure.
4. `digest_ok` gate (what the runner checks): the file exists, contains no `CLAUDE_FILL`/`<!-- raw:`/`<!-- CLAUDE` placeholders, and is > 2000 bytes (daily) / > 20000 bytes (weekly).
5. Useful env flags for manual recovery: `RECOVERY=1` (skip pull, one attempt, built-in retry prompt), `NO_RETRY=1`, `WATCHDOG_SEC`.

### Digest ships with raw placeholders

**Symptom:** The published digest still contains `<CLAUDE_FILL_*>`, `<!-- raw:`, or `<!-- CLAUDE INSTRUCTIONS -->` lines.

**Cause:** `present_v5.py` emits a SKELETON with placeholders that Claude must fill, then Claude must strip every `<!-- raw: -->` line and delete every instruction block. One of those post-fill steps was skipped.

**Fix:**
- Run the verification greps (all must be 0): `grep -c "CLAUDE_FILL" <file>`, `grep -c '<!-- raw:' <file>`, `grep -c '<!-- CLAUDE' <file>`.
- Fill and strip the offenders, then re-verify. The scheduled runner's `digest_ok` gate already rejects a file with any placeholder, so this surfaces mostly on interactive runs.

### /news produces a bare or low-quality digest

**Symptom:** Digest has very few items, or items don't feel relevant.

**Causes:**
- Slow news day.
- Identity (`02-ana/identity/`) is too vague for the relevance lens.
- Source coverage is incomplete, or enrichment failed (Substack/Medium bodies are MANDATORY — without body text those items score ~0 and never reach the digest; this was the 2026-05-09 "0/0" bug).

**Fix:**
- For slow days: ship anyway, gaps are okay.
- For relevance: refine `02-ana/identity/{goals,who-i-am}.md`.
- For missing Substack/Medium: confirm `_enrich_substack.py` / `_enrich_medium.py` ran (validation thresholds: Substack bodies ≥90%, Medium bodies ≥70%).
- For coverage: all 6 sources are mandatory and the AI does not decide to skip one; check the per-source dump in `.runs/YYYY-MM-DD/`.

### An item the user already saw reappears

**Symptom:** A gem that was in a prior digest shows up again.

**Cause:** The cross-day dedup is the git-tracked, append-only `seen_ledger.jsonl` in the skill dir (~2,800 records). A reappearance means the URL normalized differently or the ledger entry is missing.

**Fix:**
- This replaced the old 3-day digest-parsing dedup (which broke when the presenter archived `daily/` mid-cycle and re-runs found zero priors — the "We're in 1905" symptom). If that old behavior resurfaces, confirm `present_v5.py` is appending to the ledger on success and that same-date records (`first_seen == today`) are being ignored so a re-run never suppresses today's own pool.

---

## Plugin and HUD issues

### Statusline is blank

**Symptom:** No HUD info in the prompt.

**Cause:** The `claude-hud` plugin is not initialized, or `node` couldn't be resolved. The `settings.json` `statusLine` now execs the newest `claude-hud` plugin build under `~/.claude/plugins/cache/claude-hud/claude-hud/*/` via a dynamically-resolved `node` (this replaced the hardcoded-nvm-path statusline on 2026-06-09). The legacy `03-rai/config/statusline.sh` is no longer wired (kept as fallback/reference).

**Fix:**
- Run `/claude-hud:setup` to reinitialize.
- Confirm the plugin is in `03-rai/config/settings.json` `enabledPlugins` (`claude-hud@claude-hud: true`) and that `node` resolves (`command -v node`).

### Statusline shows wrong counts

**Symptom:** HUD shows outdated skill/hook counts that never change.

**Cause:** Same frozen-counts bug as above — the HUD reads the `counts` block in `config/settings.json`, which `update-counts.py` can't refresh because it writes to the non-existent `03-rai/settings.json`.

**Fix:**
- Running `update-counts.py` manually will NOT help until `lib/paths.get_settings_path()` is corrected to point at `config/settings.json` — see "Frozen counts block" under Hook issues. The displayed counts are stale by design.

---

## ChromaDB recovery (advanced)

If ChromaDB is corrupted (rare):

1. Confirm corruption: try a query (always via `03-rai/semantic-memory/scripts/py-chroma.sh` — the uv/python-3.12/chromadb wrapper; never call `python3` directly), look for SQLite errors. The live store is `03-rai/semantic-memory/chromadb/` (collection `memories`, ~734 embeddings, all-MiniLM-L6-v2, 384-dim, cosine). The sibling `03-rai/semantic-memory/chroma/` is a STRAY empty dead store — ignore it; it is not the active store.
2. Do recovery ON THE LINUX COORDINATOR only — it is the sole ChromaDB writer. Recreating the store on the Mac would write the binary store from a replica and reintroduce the sync jam.
3. Back up the existing folder: `cp -r 03-rai/semantic-memory/chromadb 03-rai/semantic-memory/chromadb.bak`.
4. Delete the corrupted folder: `rm -rf 03-rai/semantic-memory/chromadb`.
5. The `memories` collection is recreated lazily on next write. (SessionStart will log the handled `Collection [memories] does not exist` until then — expected.)
6. Re-ingest historical sessions: copy `13-archive/historical-sessions/*.json` back into `pending/`, then run `/rai process-sessions` on Linux.

This is destructive. Only do it if recovery is needed.

---

## Sync issues (single-coordinator Linux/Mac)

Vault sync is SINGLE-COORDINATOR: the Linux box (`pc`, Tailscale `100.64.0.2`, user `john`) is the sole coordinator and the ONLY machine that writes `origin` (GitHub) and ChromaDB. The Mac (`100.64.0.3`, user `johndoe`) is a passive replica over keyless Tailscale SSH and never touches GitHub. Authoritative doc: `03-rai/SYNC-ARCHITECTURE.md`. Coordinator runner: `03-rai/skills/rai/scheduled/run-maintenance-ubuntu.sh` (systemd `rai-maintenance.timer` @ 04/10/16/22:00); Mac runner driven over SSH: `mac-sync.sh`.

### ChromaDB binary-conflict jam / detached HEAD on the coordinator

**Symptom:** The maintenance run stalls or aborts; `git status` on the coordinator shows a half-finished rebase (detached HEAD + `UU` conflicts), often on `chromadb/chroma.sqlite3` or a `*.bin` segment with "Cannot merge binary files." Every subsequent run inherits the poisoned tree.

**Cause:** This is the jam fixed in commit `abc1234` (2026-06-14). The old step-0 pull strategy `git pull --rebase --autostash origin main` replayed unpushed `wip(mac)` churn onto `origin` and choked when a ChromaDB binary file conflicted, stranding a half-rebase. The root cause is that ChromaDB is a binary store git cannot merge, and the SessionStart recall hook mutates the sqlite/bin bytes even on a pure read.

**Fix (current design — usually already in place):**
- Step 0 is now `git fetch origin main` + `git merge --ff-only FETCH_HEAD` — a steady-state no-op that fails cleanly instead of jamming. The coordinator merges Mac churn with `-X ours` (Linux always wins, keeping its authoritative ChromaDB), and `*.jsonl` logs union both sides via `.gitattributes` (`03-rai/memory/**/*.jsonl merge=union`).
- `mac-sync.sh` never syncs read-induced ChromaDB drift: on `commit` it unstages chromadb (`git reset -- chromadb`); on `refresh` it discards it (`git checkout -- chromadb`). The Mac stays a clean read-only replica.

**Recovery if a jam already happened:**
1. On the coordinator, abort the dead operation: `git rebase --abort` (or `git merge --abort`). The runner's `self_heal_git_state` does this and backs up conflicted paths to `~/.local/state/helm-pull-collisions/<ts>/`.
2. If HEAD is detached, return to the branch: `git checkout main`.
3. Discard any read-induced ChromaDB drift so it doesn't re-conflict: `git checkout -- 03-rai/semantic-memory/chromadb` (or `git reset -- 03-rai/semantic-memory/chromadb`).
4. Re-run the maintenance pipeline. Two consecutive hard failures fire a `notify-send` critical and abort before committing a conflicted tree.

Never "fix" this by gitignoring ChromaDB. Policy is "information is NEVER ignored — fix sync via mechanism, not ignores" (only secrets + machine droppings are gitignored). The fix is the mechanism above, not an ignore rule.

### Mac shows "ahead of origin" or won't sync

**Symptom:** The Mac's `git status` claims it is ahead of origin, or a Mac sync errors out.

**Causes:**
- The Mac cannot reach GitHub from a non-interactive SSH session (its creds are in the macOS Keychain, unreachable → error `-25308`). By design, the Mac pulls from the `linux` remote over Tailscale, not from GitHub.
- The Mac was asleep when the coordinator ran (capture + refresh simply skip; it syncs next run it's awake for).

**Fix:**
- This is mostly cosmetic and self-correcting: the coordinator's `refresh_mac` step propagates Linux's real `origin/main` SHA to the Mac (`git update-ref refs/remotes/origin/main <sha>`) so the Mac's status stays honest.
- If the Mac is unreachable, no action — it is a passive replica; the Linux+Mac pair still holds the latest state on disk. Wake the Mac and the next coordinator run captures + refreshes it.
- Do NOT run `git push` from the Mac or run `/rai process-sessions` on the Mac — both violate the single-writer rule.

---

## When all else fails

1. **Read the relevant CLAUDE.md.** It is the live source of truth (root + per-folder). For sync, read `03-rai/SYNC-ARCHITECTURE.md`.
2. **Read the relevant SKILL.md or agent .md.** The skill/agent itself often documents its own failure modes.
3. **Run `/rai sanity`.** It has 11 tier checks A-K (data safety, environment, ChromaDB integrity, pipeline, hooks/errors, identity-cache, work-state, counts). Verdicts: HEALTHY / DEGRADED / BROKEN. Args: `--quick`, `--fix`, `--baseline`.
4. **Read the recent integrity reports.** `ls 03-rai/memory/learning/system/integrity/` (`change-*.json`, 30-day rotation).
5. **Read recent hook errors.** `tail 03-rai/memory/learning/system/hook-errors.jsonl`.
6. **Restart the Claude Code session.** Many transient issues resolve at session boundary — hooks fail safe (SIGALRM timeout + exit 0), so a clean session boundary clears most transient hook state.

If a failure is not in this chapter, capture it (in `02-ana/journal/` or as a new section here) so future-you (or future-Rai) has the answer.
