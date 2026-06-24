# 19 — Glossary

Every term used in the manual, defined.

Last updated 2026-06-14. Live source of truth for any folder's rules is its `CLAUDE.md`; when this glossary and a `CLAUDE.md` disagree, the `CLAUDE.md` wins.

## A

**Active (project state)** — Stage in the project lifecycle after `kitchen/`. Code lives in `~/projects/{name}/`; non-code artifacts in `05-projects/active/{name}/`. (The `active/` directory is created on demand; it does not always exist on disk.)

**Agent** — A persona with its own context window. Invoked via `Task(subagent_type: "name")`. Defined at `03-rai/agents/{name}.md`. Used for parallelism, isolation, or specialist work. 12 agents exist (10 specialists + 2 methodology).

**Agent Breadcrumbs** — Required section in every MOC. A place where Rai (or future-John) leaves navigation hints for future sessions.

**Algorithm** — Rai's structured 7-phase problem-solving framework. Version 3.7.0. Phases: OBSERVE → THINK → PLAN → BUILD → EXECUTE → VERIFY → LEARN.

**Anti-criterion (ISC-A)** — A criterion stating what must NOT happen. Prefix `ISC-A1`, `ISC-A2`, etc. Counts toward the ISC floor.

**ask-model** — Leaf skill at `03-rai/skills/ask-model/`. Calls an external frontier LLM via OpenRouter — Gemini 3.1 Pro Preview or GPT-5.5 — for a write/translate/judge/critique/summarize/freeform task. Telemetry logged to `03-rai/memory/ai-calls/`. Added 2026-05-16.

**Auto-load** — The contract that every `.md` file in `02-ana/identity/` and `03-rai/identity/` is read into context at every SessionStart. 17 files total (13 in `02-ana/identity/` + 4 in `03-rai/identity/`).

## B

**Bawaba** — Arabic for "gateway." `08-bawaba/` is the news-digest output folder. Daily runs write `08-bawaba/daily/YYYY-MM-DD.md`; weekly runs write `08-bawaba/weekly/YYYY-WWW.md` (see Bawaba Weekly).

**Bawaba Weekly** — The weekly news-digest magazine produced by `/news week`. An 8-department magazine (Editor's Letter, Cover Story, Model State, The Lesson, The Stack, The Workshop, Reading Shelf, Closing Wisdom, plus a "The Fold" scan block), not a recap. Its v3 design system was sealed 2026-06-13. Inputs are the week's raw dumps in `13-archive/news/dumps/` plus the seven dailies; it never opens a browser. Output: `08-bawaba/weekly/YYYY-WWW.md`. House style in `news-digest/weekly_style.md`.

**BUILD** — Phase 4 of the Algorithm. Where selected capabilities are invoked via Skill or Task tool calls.

## C

**Capability** — A skill or platform tool the Algorithm selects in OBSERVE and binds itself to invoke during BUILD or EXECUTE. Selecting without invoking = CRITICAL FAILURE.

**Capture pipeline** — The flow `00-landing → 01-inbox → destination`. Triggered by `/triage process-landing` and `/triage process-inbox`.

**Cheatsheet** — Chapter 21. One-page reference for the impatient.

**ChromaDB** — The vector store at `03-rai/semantic-memory/chromadb/`. Persistent SQLite + HNSW indices. Holds session memories (collection `memories`, ~734 embeddings, all-MiniLM-L6-v2, 384-dim) for cross-session recall. SINGLE-WRITER: the Linux coordinator (`pc`) is the only machine that writes it; the Mac replica discards any read-induced drift.

**CLAUDE.md** — Live source of truth for a folder's rules. Each numbered folder owns its CLAUDE.md. The vault root has one too. Loaded into every Claude Code session.

**.codemap/** — Auto-maintained code project map. Created by `/map-updater` only when running inside a code project. It does NOT exist in the helm vault (the vault gets `.helm-index/` instead).

**combo** — `/investigation combo` sub-skill. Combined investigation workflow over the OSINT, private-investigator, and recon lenses.

**Compaction** — At Algorithm phase boundaries (Extended+ effort), if context exceeds ~60%, self-summarize. Preserve ISC + decisions + next actions; discard verbose tool output.

**Completed (project state)** — Final stage of the project lifecycle. `05-projects/completed/{name}/` holds the retrospective and diagrams. 8 retrospectives currently on disk.

**Continuation** — Optional ChromaDB metadata field marking that a session continues a previous session.

**convene** — `/investment convene` sub-skill. Runs the Restraint Gate / advisory council before any investment action. Added 2026-06-13.

**Coordinator** — In the vault-sync model (since 2026-06-13), the Linux box `pc`. It is the sole maintenance runner, the only machine that writes to GitHub (origin), and the sole ChromaDB writer. Runs `run-maintenance-ubuntu.sh` at 04/10/16/22:00. Authoritative doc: `03-rai/SYNC-ARCHITECTURE.md`. See also Replica, Tailscale SSH sync.

**Council** — `/think council` sub-skill. Multi-agent debate. (Distinct from the investment advisory council reached via `/investment convene`.)

**CWD-aware** — Behavior that changes based on current working directory. Example: `session-start.py` loads full memory inside `~/helm/`, 7-day window elsewhere.

## D

**Delete over archive** — Vault rule: only session JSONs are archived; everything else is deleted when no longer live. Git log is the archive for text content. Two standing exceptions (John-approved): `13-archive/news/` and `13-archive/learning/` are never purged.

**derived_from** — Frontmatter field in idea files. Wiki-link array pointing to parent ideas this came from.

**dotfiles** — `.helm-index/`, `.obsidian/`, `.gitignore`, `.gitattributes`, `.pai-protected.json`, etc. Hidden folders/files at the vault root. (`.codemap/` is NOT among them — it only appears inside code projects.)

## E

**Effort tier** — One of Standard, Extended, Advanced, Deep, Comprehensive. Set in OBSERVE phase. Determines time budget, ISC count floor, and minimum capabilities to invoke.

**effortLevel** — The reasoning-intensity key in `03-rai/config/settings.json` (reached via `~/.claude/settings.json`). The on-disk value at HEAD is `xhigh` — this is the canonical, current setting (quote `xhigh` as canonical; see chapter 17). The value churned during the 2026-06-13/14 window (brief dips `xhigh → high → medium`, commit abc1234) but settled back to `xhigh`. Those lower values were transient history, not the standing default.

**Engagement** — A paid client or employer relationship. Each gets a subfolder in `04-work/{engagement}/`. Current engagements: client-alpha, helios, tableau. (Helios is its own engagement at `04-work/helios/`, a peer to client-alpha.)

**Euphoric Surprise** — The Algorithm's stated goal: 9-10 user satisfaction ratings. The bar.

**EXECUTE** — Phase 5 of the Algorithm. Where the work actually happens.

**Extended** — Effort tier. <8 min budget, 16-32 ISC, 3-5 capabilities. For "quality must be extraordinary."

## F

**File memory** — The structured memory at `03-rai/memory/{learning,relationship,security}/` (plus `state/`, `work/`, `ai-calls/`). JSONL and dated MD files. Fast to read, distinct from semantic memory (ChromaDB).

**Frontmatter** — YAML block at the top of a Markdown file, between `---` delimiters. Used for metadata.

## G

**GAPS.md** — `03-rai/skills/GAPS.md`. Open backlog of deferred skill work and tombstones (deletion candidates).

**gem feed** — The news-digest output model: the daily digest is a curated feed of roughly 80-100 "gems" (v5.6 target, per `gems_total_target [80,100]` in config.yaml / chapter 15; was 40-50 in the older v3 design) presented in feed style, not a newspaper. News items are one-liners; the gems are the product. Established in the "v3 gems redesign," now formalized into sections rather than a flat list.

**Graduated (idea state)** — Final state of an idea before it becomes a project. Frontmatter `status: graduated`. Marked when `/ideas graduate` runs.

## H

**.helm-index/** — Auto-maintained navigation index at the vault root. Refreshed by `/map-updater`. The vault analog of `.codemap/`.

**Hook** — Event-driven script that fires on Claude Code events. Wired in `03-rai/config/settings.json` (reached via the `~/.claude/settings.json` symlink). Code in `03-rai/hooks/*.py`. 19 distinct `.py` scripts, 24 wired invocations. (Two PostToolUse codemap handlers are shell scripts under `03-rai/skills/map-updater/scripts/`, not in `hooks/`.)

## I

**Identity** — Auto-loaded `.md` files in `02-ana/identity/` (John, 13 files) and `03-rai/identity/` (Rai, 4 files: ai-steering-rules, coding-format, dai-identity, response-format). 17 files total. The "always-on context" mechanism. Non-`.md` files in `identity/` (e.g. `security-patterns.yaml`) are NOT auto-loaded.

**Identity cache** — `03-rai/memory/state/identity-cache.json`. Mtime-validated. Avoids re-reading identity files when source mtimes haven't changed.

**Inbox** — `01-inbox/`. The research queue. Contains items promoted from `00-landing/` awaiting research.

**Insight Note** — A `10-knowledge/` note that captures an emergent connection between two existing notes. Frontmatter `type: insight, emerged_from: [[a]], [[b]]`. Proposed before created.

**investment** — `/investment` router at `03-rai/skills/investment/`. Operates John's values-based paper-trading practice in `02-ana/financial/investment/`. 6 sub-skills: status, recommend, screen, review, ops, convene. Strictly spot-only (no leverage/futures/options/shorts), phase-aware, cloud-only runtime on a DigitalOcean droplet. All paper, real money deferred. Added 2026-05-31. See Restraint Gate, values-based paper-trading.

**Iteration** — Optional PRD frontmatter field. Increments when a task needs rework after `phase: complete`.

**ISC (Ideal State Criteria)** — Atomic verifiable criteria that define when a task is done. Written into the PRD's `## Criteria` section. Format: `- [ ] ISC-1: criterion text`.

**ISC count gate** — Cannot exit OBSERVE without meeting the effort tier's ISC floor (Standard: 8, Extended: 16, Advanced: 24, Deep: 40, Comprehensive: 64).

## K

**Kitchen** — `05-projects/kitchen/`. Project planning stage. PRDs, architecture, design. No code yet. Current kitchen projects: cloud-lab, open-kit.

## L

**Landing** — `00-landing/`. The parking lot for manual drops. Claude must NOT create files here.

**LEARN** — Phase 7 of the Algorithm. Reflection + JSONL append + set `phase: complete`.

**Leaf (skill)** — A skill with no sub-skills. `03-rai/skills/{name}/SKILL.md` only. Four exist: `ask-model`, `map-updater`, `project-init`, `visual-plan`, `workflow`. (Contrast Router.)

**Lineage (idea)** — The graph of `derived_from:` and `spawned:` wiki-links across ideas in `09-ideas/`. Walked by `/ideas derive`.

## M

**methodology agent** — One of the two non-specialist agents (`algorithm`, `researcher`) that encode a way of working rather than a domain skill. `algorithm` wraps the 7-phase ISC framework; `researcher` does multi-source research synthesis with query decomposition and cited findings. The other 8 agents are specialists.

**MOC (Map of Content)** — `10-knowledge/_mocs/{Name} MOC.md`. A topic hub that aggregates Topic Notes for a domain. Required Agent Breadcrumbs section.

**Model** — The LLM Rai uses. `opus` for reasoning-heavy work, `sonnet` for execution-heavy. No model pin is set in `settings.json` (a Fable-5 pin was added then dropped) — opus with 1M context is the harness default, not a configured pin. Agents declare their own model: all 12 agents run `opus` at `effort: xhigh`. No agent uses sonnet or haiku.

## N

**News digest** — `/news-digest` (a.k.a. `/news`) skill. Outputs to `08-bawaba/` (`daily/` + `weekly/`). Sources (all 6 mandatory): HN, Reddit, X, Substack, Medium, GitHub Trending. Currently v5.6. Two modes: "day" (last 24h) and "week" (Bawaba Weekly magazine). Runs headless via `claude -p`, scheduled on Ubuntu via systemd timers (daily 03:00, weekly Sat 07:00).

## O

**OBSERVE** — Phase 1 of the Algorithm. Reverse-engineer wants, set effort tier, generate ISC, select capabilities.

**Orphan (state file)** — Per-session file in `memory/state/` from a crashed session that never ran SessionEnd. Swept at next SessionStart (6h threshold).

## P

**.pai-protected.json** — `03-rai/.pai-protected.json`. 388 lines of regex for secret redaction (version `rai-1.0`). Read by `lib/protected_scan.py` via `security-validator.py`, but only on `git commit` (pre-commit secret/PII scan), not on every Write/Edit. Path-level Write/Edit gating is done by `security-patterns.yaml`, not this file.

**PAI_DIR** — Formerly an environment variable in `~/.claude/settings.json` pointing at `03-rai/`. REMOVED 2026-06-09 (cross-platform fix); the `env` block is now empty. Hooks self-resolve their paths to `$HOME/helm/03-rai` via `lib/paths.py`.

**PAI** — The original name of the system Rai is built on. Stands for "Personal AI." Rarely surfaced in current rules; lingers in env vars, some legacy file names, and the Algorithm entry banner.

**Pending** — `03-rai/semantic-memory/pending/`. Queue of session JSONs awaiting summarization and ingestion into ChromaDB. Drained only on the Linux coordinator.

**Plant (idea state)** — Stage 2 of the idea lifecycle. A researched Seed with Q&A and market validation. Frontmatter `status: plant`.

**PLAN** — Phase 3 of the Algorithm. Architecture, file structure, sequence. EnterPlanMode for Advanced+.

**PRD (Product Requirements Document)** — The system of record for a task. Two types:
- **Project PRD** — durable, in `05-projects/kitchen/{name}/PRD.md`. Edited by user.
- **Task PRD** — per-task, in `03-rai/memory/work/{slug}/PRD.md`. Edited by Algorithm.

**PreToolUse / PostToolUse** — Claude Code events that fire before and after each tool call. Matched by tool type (Bash, Edit, Write, Read, Task, Skill, AskUserQuestion).

**Process-sessions** — `/rai process-sessions` skill. Drains `pending/` into ChromaDB. Runs only on the Linux coordinator.

**Promote (idea)** — `/ideas promote` skill. Advances an idea Seed → Plant → Tree.

**Protected scan** — `lib/protected_scan.py`. Reads `.pai-protected.json` and matches against content. Used by security validator.

## R

**Rai** — The AI assistant operating the brain. The other principal alongside John. Identity at `03-rai/identity/`. A public-facing self-description also lives in `02-ana/identity/rai-public.md`.

**Rating** — A user satisfaction signal (1-10 or qualitative). Captured by `rating-capture.py` UserPromptSubmit hook to `memory/learning/signals/ratings.jsonl`.

**Recall** — `/recall history` skill. Queries ChromaDB for past sessions semantically.

**References (12-system)** — Documentation snapshots at `12-system/references/`. Distinct from templates. Snapshots, not source of truth.

**Reflection** — Algorithm LEARN-phase output. 4 questions, plus a JSONL log entry.

**Relationship memory** — Daily user-signal notes at `03-rai/memory/relationship/{YYYY-MM}/{YYYY-MM-DD}.md`. Written by `relationship-memory.py` at SessionEnd.

**Replica** — In the vault-sync model (since 2026-06-13), the Mac. A passive replica: it refreshes from the Linux coordinator over Tailscale SSH and never touches GitHub. It discards any read-induced ChromaDB drift. See also Coordinator, Tailscale SSH sync.

**Restraint Gate** — The investment advisory council reached via `/investment convene`. 14 elite-investor lenses whose default verdict is DO NOTHING; an action must clear a 4-gate buy funnel (Debt/Timing → rules-based → Edge Honesty → Portfolio Fit) plus a final explicit John sign-off. A deliberate brake against impulse trades.

**Retrospective** — `05-projects/completed/{name}/retrospective.md`. Written when a project completes, using the Project Retrospective template (frontmatter `type: project-retrospective`).

**Router (skill)** — A top-level skill folder containing sub-skill `.md` files. Routes user intent to the right sub-skill. 30 routers exist (out of 35 top-level skill entries; the other 4 are leaves).

## S

**Sanity** — `/rai sanity` sub-skill. Healthcheck the brain end-to-end across tiers (templates, hooks, skills, memory, semantic-memory, work-state, errors). Verdicts HEALTHY / DEGRADED / BROKEN.

**Scratch board** — `~/helm/scratch-board.md`. Loose weekly plan in markdown. Not a structured artifact.

**Seed (idea state)** — Stage 1 of the idea lifecycle. Raw idea, minimal effort to capture. Frontmatter `status: seed`.

**seen-URL ledger** — `seen_ledger.jsonl` in the news-digest skill. A git-tracked, append-only record of every URL already shown in a digest (per source), used for cross-run deduplication. Replaced the older 3-day digest-parsing dedup. Carries thousands of records across X, Reddit, web, Substack, GitHub, Medium, and HN.

**Semantic memory** — `03-rai/semantic-memory/`. ChromaDB vector store + pending queue + scripts. Long-term cross-session recall.

**SessionEnd** — Claude Code event when a session ends. Triggers 7 hooks in order: save-memory → work-completion-learning → session-summary → relationship-memory → update-counts → integrity-check → algorithm-scan.

**SessionStart** — Claude Code event when a session begins. Triggers 2 hooks: session-start.py (chroma + identity + sweep) and check-version.py.

**values-based paper-trading** — The investment practice operated by `/investment`. Strictly values-based: spot only, no leverage/futures/options/shorts. Entirely paper (no real money yet); a crypto bot (Freqtrade DRY-RUN) and a per-stream equity engine run on a DigitalOcean droplet. Governed by the Restraint Gate. See investment.

**Simplicity Theorem** — Required first section of every Topic Note. One sentence (the "aha"). 2-3 sentences of body. No jargon. A 12-year-old could understand.

**Skill** — A capability defined at `03-rai/skills/{router}/SKILL.md` (router/leaf) or `{router}/{sub-skill}.md` (sub-skill). Invoked via `Skill("name")` or `/name`. 35 top-level skills (30 routers + 5 leaves), ~128 sub-skill files.

**SKILL.md frontmatter validation** — A check folded into `session-start.py` (added 2026-05-13). It regex-validates the frontmatter of every `skills/{name}/SKILL.md` at session start and surfaces a `skills_bad=N` count in the `[rai]` startup footer. Keeps the skill catalog well-formed.

**.skill-lock.json** — `03-rai/config/.skill-lock.json`. Version-pin lockfile (version 3) for externally-installed skills (e.g. `beautiful-mermaid` from intellectronica/agent-skills). NOT a per-session concurrency mutex.

**Slug** — Format `YYYYMMDD_HHMMSS_kebab-task-description`. Used as the directory name in `03-rai/memory/work/{slug}/`. (The spec writes a dash between date and time; on-disk dirs use an underscore.)

**spawned** — Frontmatter field in idea files. Wiki-link array pointing to ideas or projects this idea created.

**Splitting Test** — Four tests applied to every ISC criterion: and/with test, independent failure test, scope word test, domain boundary test. Compound criteria must be split.

**Standard** — Default effort tier. <2 min budget, 8-16 ISC, 1-2 capabilities. For normal requests.

**State** — Per-session runtime state at `03-rai/memory/state/`. Cleaned at SessionEnd; orphans swept at SessionStart.

**State sweep** — `lib/state_sweep.py`. SessionStart cleanup of orphan per-session files older than 6 hours.

**Stop** — Claude Code event on user interruption. Triggers `stop-orchestrator.py`.

**Story arcs** — `08-bawaba/story-arcs.md`. Multi-day (and multi-week) news threads tracked as a single named arc; fed into Bawaba Weekly.

**Sub-skill** — A skill file inside a router (e.g., `skills/think/council.md`). Not directly invocable; reached via the router.

**SYNC-ARCHITECTURE.md** — `03-rai/SYNC-ARCHITECTURE.md`. The authoritative doc for the single-coordinator vault sync over Tailscale SSH (Linux coordinator / Mac replica). Added 2026-06-13. See Coordinator, Replica, Tailscale SSH sync.

## T

**Tailscale SSH sync** — The vault-sync mechanism since 2026-06-13. The Linux coordinator pushes refreshes to the Mac replica over keyless Tailscale SSH; the Mac never touches GitHub. The coordinator is the sole origin writer and sole ChromaDB writer. Authoritative doc: `03-rai/SYNC-ARCHITECTURE.md`.

**Task PRD** — See PRD.

**Task tool** — Claude Code's tool for invoking an agent. `Task(subagent_type: "name", description: "...", prompt: "...")`.

**Telos** — `/life telos` sub-skill. Updates the self-model files (`identity/{goals,vision,mindset,who-i-am}.md`).

**THINK** — Phase 2 of the Algorithm. Pressure-test ISC. Premortem. Refine criteria.

**Tier (effort)** — See Effort tier.

**Tombstone** — A skill marked for deletion review with a deadline (in `skills/GAPS.md`).

**Topic Note** — A `10-knowledge/` note providing comprehensive coverage of a topic area. Required structure: Simplicity Theorem → Diagram → Why It Matters → Sections → Toolbox → Connections → Trade-offs.

**Tree (idea state)** — Stage 3 of the idea lifecycle. A fully planned Plant with requirements, architecture sketch, schedule, dependencies. Frontmatter `status: tree`.

**Triage** — `/triage` router with sub-skills `process-landing` and `process-inbox`. The capture pipeline driver.

## U

**ubuntu** — `/ubuntu` router at `03-rai/skills/ubuntu/`. Mirrors `/mac` for the Hyprland Linux daily driver. 5 sub-skills: theme, hyprland, diagnostics, dotfiles-bootstrap, tips. Added 2026-06-05. Shares Omarchy palettes from `mac/references` (no fork); the `hyprland` sub-skill replaces Mac's `automation`.

**UserPromptSubmit** — Claude Code event before the model sees a user prompt. Triggers 4 hooks: rating-capture, auto-work-creation, session-auto-name, update-tab-title.

**update-config** — Claude Code-built-in skill for editing `~/.claude/settings.json`. Use it for hook wiring, permissions, env vars.

## V

**VERIFY** — Phase 6 of the Algorithm. Test each ISC criterion. Capture evidence. Check capability invocation.

**Voice announcement** — Curl to `localhost:8888/notify` at Algorithm entry and each phase transition. Only the primary agent emits; subagents skip.

## W

**Weekly retro** — `/routine weekly-retro` sub-skill. Saturday ritual. Reads the week's journal, plans, ratings; produces a retrospective in `02-ana/soul/`. (Lives under `/routine`, not `/life`.)

**Weekly planner** — `/work weekly-planner` sub-skill. Monday ritual. Writes the new ISO-week plan in `04-work/work-plans/{YYYY-WNN}.md`.

**weekly_style** — `news-digest/weekly_style.md`. The house-style guide for Bawaba Weekly. Added 2026-06-13. Its presence makes `news-digest` carry a sub-skill file even though the MANIFEST still classes it as a leaf.

**writing** — `/writing` router at `03-rai/skills/writing/`. Prose craft that should read as written by a person, not an AI. 5 sub-skills: arabic, proposals, prds, social-media, blog. Created 2026-05-06; it absorbed `proposals` + `prds` out of `/business` (which shrank to sales, presentations, pricing). Every sub-skill enforces the shared anti-AI voice rules.

**WezTerm** — A terminal emulator. Historically John's primary terminal and the surface the tab-title hooks (`update-tab-title.py`, `set-question-tab.py`) target. As of 2026-06-10 the Mac primary terminal is Ghostty; the tab-title hooks remain, and news runs are now headless (`claude -p`) rather than driven through WezTerm.

**Wiki-link** — Obsidian-style link `[[note-name]]`. Used in prose for connections, in idea frontmatter for lineage, in Topic Note Connections section.

**Work index** — `03-rai/memory/state/work.json`. Master registry of all tasks. Rebuilt in place by `lib/work_index.py` (invoked by the work hooks — auto-work-creation / session-summary / work-completion-learning — and manual/`/rai` runs), not by `update-counts.py` and not a dedicated SessionEnd hook job. `update-counts.py` only recounts skills/hooks/ratings and appends `counts-history.jsonl`.

**Work-plans** — `04-work/work-plans/{YYYY-WNN}.md`. Weekly plans across all engagements. Written by `/work weekly-planner`. (Documented in `04-work/CLAUDE.md` but the directory is created on demand.)

**Workflow** — A markdown playbook in `11-workflows/`. Different from a skill — workflows are step-by-step prose for humans; skills are programmatic capabilities for Rai. 8 numbered playbooks (01-project … 08-weekly-review).

## X

**xhigh** — A value of the `effortLevel` setting in `03-rai/config/settings.json` (high reasoning intensity). It is the on-disk value at HEAD and the canonical, current setting (quote `xhigh` as canonical; see chapter 17). The value churned during the 2026-06-13/14 window (brief dips to `high`/`medium`) but settled back to `xhigh`; those lower values were transient history, not the standing default. See effortLevel.

**X (Twitter)** — Required source for `/news`. The skill aborts if X collection fails. Media must be hidden via CSS before scrolling. As of v5.6 the account is X Premium and collection runs via a headless CDP collector (`_collect_x_headless.py`), with the Chrome-MCP scroller demoted to fallback.

## Y

**YAML** — The format for frontmatter blocks at the top of Markdown files. Between `---` delimiters.

## Z

**Zero-access path** — A path category in `security-patterns.yaml`. The validator refuses to read or write these. Examples: `~/.ssh/id_*`, `~/.aws/credentials`.
