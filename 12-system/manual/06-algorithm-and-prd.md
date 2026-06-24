# 06 — Algorithm and PRD

The decision framework that governs every non-trivial task. Version 3.7.0. Seven phases. Five effort tiers. One PRD per task — in spec; one `META.yaml` ledger per task in practice.

*Last updated: 2026-06-14. The Algorithm spec is unchanged since the 2026-04-22 baseline — still v3.7.0, zero commits to `~/helm/03-rai/algorithm/` since then. What this revision adds is the spec-vs-reality picture: the runtime hook, the actual on-disk artifacts, and the handful of spec-referenced files that do not exist.*

## What the Algorithm is

A structured 7-phase loop that Rai runs for any non-trivial request. The point: transition from CURRENT STATE to IDEAL STATE using verifiable criteria (ISC), so the user gets work that is *actually* what they wanted — what the spec calls "Euphoric Surprise" (9-10 ratings).

Trivial requests (greeting, lookup, single-word answer) skip the Algorithm entirely. The Algorithm has overhead; that overhead pays off only when the task has shape, scope, and verification.

## Where it lives

```
~/helm/03-rai/algorithm/
├── latest          ← plain-text pointer file (10 bytes), contains the literal "v3.7.0.md"
└── v3.7.0.md       ← canonical spec (383 lines, 26,443 bytes)
```

Always read `03-rai/algorithm/latest` (names the active spec version). The spec is the source of truth. This chapter is a compiled summary for daily reference.

Note on `latest`: it is a flat text file containing the version filename, NOT a symlink on this machine. `03-rai/ARCHITECTURE.md` draws it with symlink notation (`latest -> v3.7.0.md`), but the `/rai sanity` check (Tier I, check I1) explicitly handles both forms — symlink or plain-text pointer.

The summary is also injected into every session via `03-rai/CLAUDE.md` (reached through the symlink `~/.claude/CLAUDE.md → ~/helm/03-rai/CLAUDE.md`) — that is how Rai knows to run the Algorithm without explicitly being told each time. CLAUDE.md carries only the operationally critical summary (the tier table + the capability rule + the one-line PRD contract); the spec file holds the rest.

## The seven phases

```
1. OBSERVE   →  Reverse-engineer wants. Set effort tier. Generate ISC. Select capabilities.
2. THINK     →  Pressure-test ISC. Premortem. Refine criteria.
3. PLAN      →  Architecture, file structure, sequence. (EnterPlanMode for Advanced+)
4. BUILD     →  Invoke selected capabilities. Prepare execution.
5. EXECUTE   →  Do the work. Update PRD as criteria pass.
6. VERIFY    →  Test each criterion. Mark passes. Capture evidence.
7. LEARN     →  Reflection. Append JSONL log. Set phase: complete.
```

Each transition fires a voice announcement (`curl http://localhost:8888/notify`) and updates the PRD frontmatter.

### Phase budget per tier

```
TIME CHECK at every phase. If elapsed > 150% of budget, auto-compress.
```

Budgets are total wall-clock for the whole Algorithm, distributed across phases. The exact split is judgment-based, but rough heuristic: OBSERVE 25%, THINK 10%, PLAN 10%, BUILD+EXECUTE 40%, VERIFY 10%, LEARN 5%.

## Effort tiers

The tier sets three things at once: time budget, ISC count floor, minimum capabilities to invoke.

| Tier | Budget | ISC range | Min capabilities | When to use |
|------|--------|-----------|------------------|-------------|
| **Standard** | <2 min | 8-16 | 1-2 | Normal request (DEFAULT) |
| **Extended** | <8 min | 16-32 | 3-5 | Quality must be extraordinary |
| **Advanced** | <16 min | 24-48 | 4-7 | Substantial multi-file work |
| **Deep** | <32 min | 40-80 | 6-10 | Complex design |
| **Comprehensive** | <120 min | 64-150 | 8-15 | No time pressure |

The tier is chosen in OBSERVE based on the reverse engineering of the user's request — explicit asks, implied asks, urgency signals, and complexity.

## The ISC count gate

Cannot proceed past OBSERVE without meeting the tier's ISC floor. If under the floor:

1. Re-read each criterion.
2. Apply the Splitting Test (below).
3. Decompose compound criteria.
4. Recount.
5. Repeat until floor is met.

This gate exists because (per the spec) "analysis of 50 production PRDs showed 0 out of 10 Extended PRDs ever hit the 16-minimum, and the single Deep PRD had 11 criteria vs 40-80 minimum. The gate is the fix."

## ISC decomposition methodology

Each ISC criterion = one atomic verifiable thing. If a criterion can fail in two independent ways, it's two criteria.

### The Splitting Test (apply to every criterion)

| Test | What to check | If yes |
|------|---------------|--------|
| **And/With test** | Contains "and", "with", "including", "plus" joining two verifiable things | Split into separate criteria |
| **Independent failure test** | Can part A pass while part B fails | They are separate criteria |
| **Scope word test** | Contains "all", "every", "complete", "full" | Enumerate what "all" means |
| **Domain boundary test** | Crosses UI / API / data / logic boundaries | One criterion per boundary |

### Decomposition by domain

| Domain | Decompose per | Example |
|--------|---------------|---------|
| **UI/Visual** | Element, state, breakpoint | "Hero visible" + "Hero text readable at 320px" + "Hero CTA clickable" |
| **Data/API** | Field, validation rule, error case, edge | "Name field max 100 chars" + "Name field rejects empty" + "Name field trims whitespace" |
| **Logic/Flow** | Branch, transition, boundary | "Login succeeds with valid creds" + "Login fails with wrong password" + "Login locks after 5 attempts" |
| **Content** | Section, format, tone | "Intro paragraph present" + "Intro under 50 words" + "Intro uses active voice" |
| **Infrastructure** | Service, config, permission | "Worker deployed to production" + "Worker has R2 binding" + "Worker rate-limited to 100 req/s" |

### Atomic vs compound — a worked example

**Coarse (8 ISC — wrong for Extended+):**
```
- [ ] ISC-1: Blog publishing workflow handles draft to published transition
- [ ] ISC-2: Markdown content renders correctly with all formatting
- [ ] ISC-3: SEO metadata generated and validated for each post
```

**Atomic (showing one of those decomposed):**
```
Draft-to-Published:
- [ ] ISC-1: Draft status stored in frontmatter YAML field
- [ ] ISC-2: Published status stored in frontmatter YAML field
- [ ] ISC-3: Status transition requires explicit user confirmation
- [ ] ISC-4: Published timestamp set on first publish only
- [ ] ISC-5: Slug auto-generated from title on draft creation
- [ ] ISC-6: Slug immutable after first publish
```

The coarse version hides 6+ verifiable sub-requirements behind ISC-1. The atomic version makes each independently testable. Always write atomic.

### Anti-criteria (ISC-A prefix)

Sometimes the criterion is "this thing must NOT happen." Use the `ISC-A` prefix:

```
- [ ] ISC-A1: No customer email addresses in any error log
- [ ] ISC-A2: No write to production database in dry-run mode
```

Anti-criteria count toward the ISC floor.

## Capability selection — the binding rule

In OBSERVE, the model selects capabilities (skills + agents + platform tools) it will invoke during BUILD or EXECUTE. The number selected must match the tier's minimum.

### The CRITICAL FAILURE rule

> Listing a capability without invoking it = CRITICAL FAILURE. Worse than not listing it. Reason: dishonest.

Selection creates a binding commitment. Every selected capability MUST be invoked via the `Skill` tool or `Task` tool. Writing prose that *resembles* the skill's output is NOT invocation — it is theater. If during execution a capability turns out to be unnecessary, *remove it from the selected list with a reason* rather than leaving it as a phantom.

### Where to look when selecting

The model considers two inventories:

1. **PAI skills** — listed in the system prompt at session start (the skill manifest).
2. **Platform capabilities** — Claude Code built-ins beyond skills.

### Platform capabilities table (verbatim from the spec)

| Capability | When to select | Invoke |
|------------|----------------|--------|
| `/simplify` | After code changes — 3 agents review quality, reuse, efficiency | `Skill("simplify")` |
| `/batch` | Parallel changes across many files with worktree isolation | `Skill("batch", "instruction")` |
| `/debug` | Session behaving unexpectedly — reads debug log | `Skill("debug")` |
| `/review` | Review a PR for quality, security, tests | Describe: "review this PR" |
| `/security-review` | Analyze pending changes for security vulnerabilities | Describe: "security review" |
| Agent Teams | Complex multi-agent work needing coordination + shared tasks | `TeamCreate` + `Agent` with team_name |
| Worktree Isolation | Parallel dev work — each agent gets isolated file system | `Agent` with `isolation: "worktree"` |
| Background Agents | Non-blocking parallel research or exploration | `Agent` with `run_in_background: true` |
| Competing Hypotheses | Debugging with multiple possible causes | Spawn N agents, each testing one theory |
| Writer/Reviewer | Code quality via role separation | One agent writes, separate agent reviews |

`/simplify` should be near-default for any code-producing run. `/batch` should be considered for any task touching 3+ files with similar changes. Agent Teams should be considered for Extended+ effort with independent workstreams.

## The PRD — system of record (spec contract)

Every Algorithm run writes a PRD. In the spec, the PRD is the only durable record of the task and the AI is its sole writer. (How this differs from what actually runs on disk is covered in the next section — read both.)

### Path

```
03-rai/memory/work/{slug}/PRD.md
```

Where the spec says `slug` is `YYYYMMDD-HHMMSS_kebab-task-description`. **In practice every timestamped work dir on disk uses underscore separators** — `YYYYMMDD_HHMMSS_kebab` (507/507 dirs). The spec's dash-time form is not what gets minted.

### Schema (per spec)

**Frontmatter (8 required fields, 1 optional):**

```yaml
---
task: [8-word task description]
slug: 20260614_093000_implement-login-flow
effort: standard | extended | advanced | deep | comprehensive
phase: observe | think | plan | build | execute | verify | learn | complete
progress: 3/8                   # criteria done / criteria total
mode: interactive | background
started: 2026-06-14T09:30:00+03:00
updated: 2026-06-14T09:32:14+03:00
iteration: 2                    # optional, only for rework
---
```

A stub PRD (frontmatter-only — `effort: standard`, `phase: observe`, `progress: 0/0`, `mode: interactive`) is written immediately at Algorithm entry, then filled phase by phase.

**Body (4 sections, only when populated):**

```markdown
## Context
[Why this task matters. What was requested. What was not requested. Risks.]

### Risks
[Premortem findings — added in THINK phase.]

### Plan
[Technical approach for Advanced+ — added in PLAN phase.]

## Criteria
- [ ] ISC-1: criterion text
- [x] ISC-2: another criterion text
- [ ] ISC-A1: anti-criterion text
...

## Decisions
[Non-obvious decisions made during BUILD. Each with brief rationale.]

## Verification
[Per criterion, evidence that it passed. Captured in VERIFY phase.]
```

The spec says the full field spec lives in `~/.claude/PAI/PRDFORMAT.md`. **That file does not exist on disk** (see "Spec references that do not exist," below). This chapter is the working reference for the PRD shape.

### AI is the sole writer (per spec)

> The AI writes ALL PRD content directly using Write/Edit tools. PRD.md in `memory/work/{slug}/` is the single source of truth. The AI is the sole writer — no hooks, no indirection.

What the AI writes:
- YAML frontmatter (all fields)
- All prose sections
- Criteria checkboxes (`- [ ]` and `- [x]`)
- Progress counter (`progress: 3/8`)
- Phase transitions (`phase: execute`)

What the spec says hooks do (read-only): a PostToolUse hook (`PRDSync.hook.ts`) fires on Write/Edit of PRD.md and syncs frontmatter + criteria to `work.json` for a dashboard. **This hook does not exist on disk either** — there is no `PRDSync` (or `PRDStateSync`) hook anywhere in `03-rai/hooks/`. The spec contract is aspirational on this point.

### The ISC update discipline

When a criterion passes during EXECUTE, the AI immediately:

1. Edits the PRD: changes `- [ ]` to `- [x]` for that criterion.
2. Updates frontmatter `progress: N/M` to reflect the new count.

This is the AI's responsibility. There is no hook safety net. If the AI does not update the PRD, the PRD does not get updated.

## What actually runs — the META.yaml reality

The spec describes a rich, AI-written `PRD.md`. The live system mostly does something lighter and hook-driven. A faithful operator should know both.

On disk, `03-rai/memory/work/` holds **513 directories**, one minted per session by the `auto-work-creation.py` UserPromptSubmit hook. Of those:

- **505 contain a `META.yaml`** — the actual authoritative per-task ledger.
- The nested layout is `work/{slug}/META.yaml` plus `tasks/{NNN}_{task}/{PRD.md, ISC.json, THREAD.md}`; the nested `PRD.md` stubs come from the template and **none use the spec's YAML-frontmatter + ISC-checkbox format**.
- Exactly **one** top-level hand-written `PRD.md` exists in the whole vault (`work/20260614_news-x-collection-fix/`, created 2026-06-14) — and even it is *freeform markdown* (Problem / Root cause / numbered ISC list / Approach), not the spec's frontmatter form.

The `META.yaml` schema is hook-written, not AI-written, and has 6 fields:

```yaml
id: 20260602_150606_run-news-digest-skill-now-generate-today
title: Run News-digest Skill
session_id: cef71f29-0014-42e2-99b5-10a9b922feb0
created_at: 2026-06-02T12:06:06.250344+00:00
status: COMPLETED
completed_at: 2026-06-02T12:21:57.318338+00:00
```

No ISC checkboxes, no phase, no effort, no progress — a lightweight session ledger, not the rich spec PRD. `META.yaml` is the file `/rai sanity` walks (Tier K) to assess work-state health, precisely because that is what is on disk. Sanity check K1 documents the gap in plain terms: "The Algorithm spec references PRD.md but current work dirs use `META.yaml`. Sanity checks what's actually on disk."

The takeaway for the operator: the Algorithm's *thinking discipline* (reverse-engineering, ISC, the count gate, the capability rule, verification) is real and load-bearing in the conversation. The spec's *durable PRD.md artifact* is largely unrealized — the durable trace that survives is the 6-field `META.yaml` plus the session itself (drained to ChromaDB via `/rai process-sessions`). Treat the PRD shape above as the in-session structure to follow; do not expect to find rich PRD.md files when auditing past work.

## Phase-by-phase walkthrough

> **Glyph carve-out.** The phase output-format blocks below (and the worked example at the end) reproduce the emoji from the Algorithm spec's mandatory output format *verbatim* — the magnifier (REVERSE ENGINEERING), flexed bicep (EFFORT LEVEL), bow-and-arrow (CAPABILITIES), brain (RISK / LEARNING), triangle-ruler (PLANNING), and check-mark (VERIFICATION). They are load-bearing format tokens, not decoration, so they stay despite this manual's no-emoji convention (README) — the same way chapter 01 keeps status icons inside its verbatim format blocks. Outside these reproduced spec formats, the manual remains emoji-free.

### Phase 1 — OBSERVE (1/7)

**First action:** Voice announce "Entering the Observe phase," then edit PRD frontmatter `updated: {timestamp}`.

**Activities (thinking only, minimal tool use):**

1. **Reverse engineer the request** — explicit wants, implied wants, explicit not-wanted, implied not-wanted, common gotchas, previous work.
2. **Set effort tier** — based on complexity + urgency.
3. **Generate ISC criteria** — write directly into PRD's `## Criteria` section.
4. **Apply the Splitting Test** to every criterion.
5. **ISC count gate** — if below floor, decompose more.
6. **Select capabilities** — skills + platform tools, matching tier minimum.
7. **Write context** — fill in `## Context` section in PRD.

Output to user (verbatim format from spec):

```
🔎 REVERSE ENGINEERING:
 🔎 [explicit wants]
 🔎 [explicit not-wanted]
 🔎 [implied wants]
 🔎 [implied not-wanted]
 🔎 [speed factor]

💪🏼 EFFORT LEVEL: [tier] | [8-word reasoning]

[ISC criteria from PRD]

🏹 CAPABILITIES SELECTED:
 🏹 [each capability + phase + 8-word reason]
 🏹 [12-24 word rationale for the set]
```

### Phase 2 — THINK (2/7)

**First action:** Voice "Entering the Think phase," edit PRD frontmatter `phase: think`.

**Activities:**

1. **Risk surfacing** — riskiest assumptions (2-12), premortem (2-12), prerequisites check.
2. **ISC refinement** — re-read every criterion through the Splitting Test. Add criteria for premortem-discovered failure modes.
3. **Write to PRD** — add `### Risks` subsection under `## Context`.

Output:

```
🧠 RISKIEST ASSUMPTIONS: [list]
🧠 PREMORTEM: [list]
🧠 PREREQUISITES CHECK: [list]
```

### Phase 3 — PLAN (3/7)

**First action:** Voice "Entering the Plan phase," edit PRD frontmatter `phase: plan`. EnterPlanMode if effort is Advanced+.

**Activities:**

1. **Validate prerequisites.**
2. **Update ISC** if planning surfaces new criteria.
3. **Reanalyze capabilities** — add any newly needed.
4. **Write to PRD** — for Advanced+, add `### Plan` subsection to `## Context`.

Output:

```
📐 PLANNING:
[technical approach + key decisions]
```

### Phase 4 — BUILD (4/7)

**First action:** Voice "Entering the Build phase," edit PRD frontmatter `phase: build`. **Invoke each selected capability via tool call.**

> Writing "**FirstPrinciples decomposition:**" without calling `Skill("FirstPrinciples")` is NOT invocation — it's theater.

**Activities:**

1. Any preparation needed before execution.
2. Invoke selected skills via `Skill` tool.
3. Invoke selected agents via `Task` tool.
4. Write non-obvious decisions to PRD's `## Decisions` section.

### Phase 5 — EXECUTE (5/7)

**First action:** Voice "Entering the Execute phase," edit PRD frontmatter `phase: execute`. Perform the work.

**Activities:**

1. Execute the plan.
2. As each criterion is satisfied, immediately edit the PRD: `- [ ]` → `- [x]` and update `progress:`.
3. Do NOT wait for VERIFY.

### Phase 6 — VERIFY (6/7)

**First action:** Voice "Entering the Verify phase," edit PRD frontmatter `phase: verify`.

**Activities:**

1. For each ISC criterion: test that it is actually complete.
2. For each criterion: edit PRD to mark `- [x]` if not already, add evidence to `## Verification` section.
3. Capability invocation check — for each capability selected in OBSERVE, confirm it was actually invoked. If any was not, flag as failure.

Output:

```
✅ VERIFICATION:
[per-criterion evidence]
```

### Phase 7 — LEARN (7/7)

**First action:** Voice "Entering the Learn phase," edit PRD frontmatter `phase: learn`.

**Activities:**

1. Reflect:
   - What should I have done differently?
   - What would a smarter algorithm have done?
   - What capabilities should I have used that I didn't?
   - What better algorithm should this become?
2. Set frontmatter `phase: complete`.
3. **Append a structured JSONL entry** to `~/.claude/memory/learning/REFLECTIONS/algorithm-reflections.jsonl` (per spec).

The JSONL append (mandatory for Standard+):

```json
{"timestamp":"...","effort_level":"...","task_description":"...","criteria_count":N,"criteria_passed":N,"criteria_failed":N,"prd_id":"...","implied_sentiment":N,"reflection_q1":"...","reflection_q2":"...","reflection_q3":"...","within_budget":true|false}
```

(`implied_sentiment` is the AI's own 1-10 estimate of how the user feels, not a value read from `ratings.jsonl`.) The spec says this feeds the `MineReflections`, `AlgorithmUpgrade`, and `Upgrade` workflows downstream.

**Reality check:** neither the `REFLECTIONS/` directory nor `algorithm-reflections.jsonl` exists on disk. `03-rai/memory/learning/` contains only `signals/` and `system/`. The structured runtime trace that *does* get written at session end is `state/algorithms/{session_id}.json` (see "Runtime infrastructure," below), not this reflections JSONL. The LEARN reflection is still worth producing in-conversation; just do not assume it lands in a persisted reflections log.

Output:

```
🧠 LEARNING:
[Q1 answer]
[Q2 answer]
[Q3 answer]
[Q4 answer]
```

## Voice announcements

At Algorithm entry and every phase transition, the primary agent calls:

```bash
curl -s -X POST http://localhost:8888/notify \
  -H "Content-Type: application/json" \
  -d '{"message": "MESSAGE", "voice_id": "fTtv3eikoepIosk8dTZ5", "voice_enabled": true}'
```

Messages:
- Algorithm entry: `"Entering the Algorithm"`
- Each phase: `"Entering the {phase_name} phase."`

These are direct synchronous calls. Do not background.

**Critical:** Only the primary agent emits voice curls. Subagents and background agents skip voice entirely. If a subagent reads this spec, it must skip the voice ritual.

## Runtime infrastructure (what actually executes)

The spec is the contract; a small amount of hook code is the runtime. There is exactly one Algorithm hook and one state library.

| Component | Path | Event | Role |
|-----------|------|-------|------|
| `algorithm-scan.py` | `03-rai/hooks/algorithm-scan.py` (142 lines) | **SessionEnd** (wired at `03-rai/config/settings.json` line 284) | Parses the transcript once at session end, extracts `TaskCreate` ISC criteria + `Task` agent spawns + the final phase hint, writes one `state/algorithms/{session_id}.json`, then calls `algorithm_end()` (phase → COMPLETE). 10-second SIGALRM timeout; fails open. |
| `lib/algorithm_state.py` | `03-rai/hooks/lib/algorithm_state.py` (117 lines) | (library) | Owns the per-session state JSON. PHASES list is **9 states** — `IDLE, OBSERVE, THINK, PLAN, BUILD, EXECUTE, VERIFY, LEARN, COMPLETE` (the 7 named phases bookended by IDLE + COMPLETE). State schema tracks `phase`, `phase_history`, `criteria`, `anti_criteria`, `agents_spawned`, `effort_level`, `rework_cycles`. `phase_transition()` detects rework (re-entering OBSERVE after COMPLETE/LEARN) and increments `rework_cycles`. |

This is a rewrite from the prior design: the per-PostToolUse `algorithm-tracker.py` was **retired** and replaced by the single SessionEnd `algorithm-scan.py`. Only a stale `.pyc` of the old tracker remains; `03-rai/memory/state/README.md` still names the dead `algorithm-tracker.py` as the writer (documentation rot — the real writer is `algorithm-scan.py`).

The state output lives in `03-rai/memory/state/algorithms/{session_id}.json` (UUID-keyed, ~8 files present at survey). These are short-lived: deleted at SessionEnd by `session-summary.py`, and orphans older than 6h are swept at SessionStart by `lib/state_sweep.py`.

The `/rai sanity` skill (Tier I, "Algorithm + Agents") verifies this subsystem: I1 confirms the `latest` pointer + spec file, I2 confirms phase definitions + effort tiers are present, I3 checks `state/algorithms/` freshness (WARN if newest file is 7-30 days old, escalating past 30 days as "`algorithm-scan.py` has regressed").

## Spec references that do not exist on disk

The spec (and some READMEs) name several mechanisms that are not present. Do not present these as live when operating or documenting.

| Referenced path / name | Referenced in | Status |
|------------------------|---------------|--------|
| `~/.claude/PAI/PRDFORMAT.md` | spec OBSERVE / PRD Format | MISSING — no `PRDFORMAT*` anywhere in the vault |
| `PRDSync.hook.ts` (PRD → work.json) | spec PRD-as-record / context recovery | MISSING — no such hook |
| `PRDStateSync` hook | spec context recovery | MISSING |
| `~/.claude/memory/learning/REFLECTIONS/algorithm-reflections.jsonl` | spec LEARN | MISSING — `learning/` has only `signals/` and `system/` |
| `algorithm-tracker.py` (per-PostToolUse tracker) | `state/README.md` | RETIRED — replaced by `algorithm-scan.py`; only a stale `.pyc` lingers |

None of these gaps weaken the Algorithm's in-conversation discipline — they only mean some of the spec's persistence plumbing was never built (or was rebuilt under a different name). The thinking framework above is fully real; the durable artifacts are `META.yaml` + `state/algorithms/{session_id}.json` + the session in ChromaDB.

## Critical rules (zero exceptions)

From the spec:

1. **Mandatory output format** — every response uses one of the formats from CLAUDE.md (ALGORITHM, NATIVE, ITERATION, MINIMAL). No freeform.
2. **Response format before questions** — complete the format output first, then ask questions. Never replace format with a bare question.
3. **Context compaction at phase transitions** — for Extended+ effort, if accumulated tool outputs and reasoning exceed ~60% of working context, self-summarize before proceeding. Preserve ISC status, key results, next actions. Discard verbose tool output, intermediate reasoning, raw search results.
4. **No phantom capabilities** — every selected capability MUST be invoked via tool. Text-only output is NOT invocation.
5. **No silent stalls** — ensure no processes are hung (background agents not returning, etc.).
6. **PRD is YOUR responsibility** — no hook safety net. If you don't edit, it doesn't update.
7. **ISC Count Gate is mandatory** — cannot exit OBSERVE with fewer ISC than the tier floor.
8. **Atomic criteria only** — every criterion must pass the Splitting Test.

## Context recovery

If after compaction you don't know your current phase or criteria status:

1. Read the most recent work artifact from `memory/work/` (by mtime). In spec this is the PRD frontmatter; in practice it is the `META.yaml` ledger (`id`, `title`, `session_id`, `created_at`, `status`, `completed_at`).
2. The spec's PRD frontmatter has phase, progress, effort, mode, task, slug, started, updated; the on-disk `META.yaml` has the 6 fields above.
3. A spec PRD body has criteria checkboxes, decisions, verification evidence (rarely present on disk).
4. `memory/state/algorithms/{session_id}.json` holds the runtime state machine (phase, criteria, anti_criteria, agents_spawned, effort_level, rework_cycles) written by `algorithm-scan.py` at session end — this is the most reliable machine-readable trace.

The spec also names `~/.claude/memory/state/work.json` (populated by read-only `PRDSync`/`PRDStateSync` hooks) as the session registry. Those hooks do not exist on disk; rely on `META.yaml` per dir and the `state/algorithms/` JSON instead.

## When NOT to run the Algorithm

Trivial tasks skip the Algorithm. The signal:

- Greeting, casual chat
- Direct lookup ("what is X?", "where does Y live?")
- Single-line edit with obvious correctness
- Asking a question that does not require investigation
- Acknowledging or saying thank you

When in doubt, run a lightweight Standard tier rather than skip entirely. Skipping is for genuinely trivial cases.

## Iteration mode

If a task needs rework after `phase: complete`, the iteration field is incremented:

```yaml
iteration: 2
phase: observe
```

The PRD body sections accumulate (each iteration adds context, refined criteria, new decisions, verification updates). The slug stays the same.

## Failure modes and recoveries

| Failure | Recovery |
|---------|----------|
| ISC floor not met | Decompose, rewrite Criteria, recount |
| Capability selected but not invoked | Either invoke now (BUILD/EXECUTE/VERIFY) or remove from selection with reason |
| PRD not edited mid-execute | Edit it now; explain delay in Decisions section |
| Phase transition voice skipped | Add it now; do not skip again |
| Time budget exceeded by 50%+ | Auto-compress. Reduce remaining phases or downgrade tier with note |
| Context bloat | Summarize at phase boundary; preserve ISC + decisions + next actions |
| Subagent emitted voice curl | Stop the subagent; flag the violation; the primary agent owns voice |

## A worked example — Standard tier

User asks: "rename the function `fooBar` to `processOrder` in the order service"

```
🔎 REVERSE ENGINEERING:
 🔎 explicit: rename a function across one service
 🔎 implied: keep all callers working
 🔎 not-wanted: don't refactor anything else
 🔎 not-wanted: don't add tests beyond what exists

💪🏼 EFFORT LEVEL: Standard | Single-file rename, callers limited to one service

ISC Criteria (8 — meets floor):
- [ ] ISC-1: function definition renamed in src/order-service/index.ts
- [ ] ISC-2: all callers within src/order-service/ updated
- [ ] ISC-3: import statements that reference fooBar updated
- [ ] ISC-4: existing test for fooBar passes after rename
- [ ] ISC-5: typecheck passes (no broken references)
- [ ] ISC-6: linter passes
- [ ] ISC-7: no remaining "fooBar" string in src/order-service/
- [ ] ISC-A1: no changes outside src/order-service/

🏹 CAPABILITIES SELECTED:
 🏹 testing/unit-test (VERIFY phase) — run tests after rename
 🏹 simplify (VERIFY phase) — quick review of changes for accidents
 (1 + 1 = 2, meets floor of 1-2)

[THINK is brief — single risk: a caller in a sibling service]
[PLAN is brief — Edit, then run tests]
[BUILD: prepare]
[EXECUTE: edits + run tests, mark criteria as they pass]
[VERIFY: confirm each criterion]
[LEARN: short reflection, JSONL append]
```

A worked example for Deep tier would be 5x longer. The structure is the same; the depth at each phase scales with the tier.
