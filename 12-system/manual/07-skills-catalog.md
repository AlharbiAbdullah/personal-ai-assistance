# 07 — Skills Catalog

> Last updated: 2026-06-14.

The full skill inventory. 35 top-level entries: 31 routers + 4 leaves. The leaves are `ask-model`, `map-updater`, `project-init`, `workflow`. Beneath the top-level entries sit roughly 134 sub-skill files.

Every skill exists at `~/helm/03-rai/skills/{name}/SKILL.md` (router or leaf) or `~/helm/03-rai/skills/{router}/{sub-skill}.md` (sub-skill).

> Source-of-truth note: `skills/MANIFEST.md` is STALE and undercounts. Its header still claims "28 top-level entries: 23 routers + 5 leaves" — the real tree is 35 entries (31 routers + 4 leaves). The MANIFEST table omits 6 routers (ideas, knowledge, learning, reading, triage, work), still shows pre-move sub-skill sets for several routers, and was last touched 2026-06-05. When the MANIFEST and the live `skills/` tree disagree, the live tree wins. This chapter reflects the live tree.

## Discovery and invocation

Claude Code discovers skills by scanning `skills/*/SKILL.md` at depth 1. Sub-skills are not directly discoverable; they are reached through their router.

Invocation:
- Top-level router or leaf: `Skill("name")` or `/name`
- Sub-skill: invoked through the router (e.g., `/research` then "web-research")

Naming rules:
- Folder name is kebab-case and matches frontmatter `name:` exactly.
- Sub-skill filenames are kebab-case; their `name:` matches the filename stem. (One observed exception: `news-digest/weekly_style.md` uses an underscore — it is a house-style reference, not an independently invoked sub-skill.)
- No name collisions between a router and its sub-skills (e.g., `/research/` must NOT contain `research.md`).

## How to read this catalog

For each router: name, purpose, sub-skills, when to invoke. For each leaf: same minus sub-skills.

Skills are grouped by domain in the manifest. The groups are documentation, not directories — every skill is at depth 1 in `skills/`.

---

## Engineering — domain (7 routers)

These routers cover code, systems, infrastructure, and engineering practice.

### /architecture

**Path:** `03-rai/skills/architecture/SKILL.md`
**Intent:** System design, ADRs, migration playbooks, architectural patterns.

**Sub-skills (7):**

| Sub-skill | Purpose |
|-----------|---------|
| `data-architect` | Data systems: warehouses, ETL shape, medallion architecture, modeling |
| `solution-architect` | End-to-end solution design: microservices, event-driven, saga patterns, compliance (HIPAA, GDPR, GDPR) |
| `system-design` | API design, system topology, scaling considerations |
| `adr-writer` | Architecture Decision Records — context, decision, consequences |
| `migration-playbook` | Step-by-step playbook for migrating between systems |
| `patterns` | Architectural patterns reference and selection |
| `create-cli` | Bootstrap a new TypeScript CLI scaffold with type safety |

**When to invoke:** Any system-level design work. For tactical implementation patterns (SQL, streaming), use `/data` instead.

### /data

**Path:** `03-rai/skills/data/SKILL.md`
**Intent:** Tactical data implementation patterns.

**Sub-skills (2):**

| Sub-skill | Purpose |
|-----------|---------|
| `sql-patterns` | Concrete SQL patterns: window functions, CTEs, upserts, anti-joins, optimization |
| `streaming` | Real-time streaming: Kafka, Kinesis, Flink, CDC |

**When to invoke:** Concrete data implementation. For data architecture (warehouse design, medallion), use `/architecture/data-architect`.

### /devops

**Path:** `03-rai/skills/devops/SKILL.md`
**Intent:** Infrastructure, containerization, orchestration, deployment, observability.

**Sub-skills (5):**

| Sub-skill | Purpose |
|-----------|---------|
| `docker` | Multi-arch builds, Dockerfile patterns, compose, secrets management |
| `cloudflare` | Workers, MCP remote servers, Pages |
| `kubernetes` | K8s manifests, Helm, kubectl patterns |
| `ci-cd` | Pipelines: GitHub Actions, GitLab CI, CircleCI |
| `monitoring` | Observability stacks, dashboards, alerts (Grafana/Prometheus) |

**When to invoke:** Anything related to running code in production environments.

### /coding-standards

**Path:** `03-rai/skills/coding-standards/SKILL.md`
**Intent:** Per-language style and review.

**Sub-skills (4):**

| Sub-skill | Purpose |
|-----------|---------|
| `python` | Idiomatic Python — PEP 8, ruff, type hints, testing patterns |
| `typescript` | Idiomatic TypeScript — strict types, exhaustiveness, error handling |
| `go` | Idiomatic Go — error handling, interfaces, concurrency patterns |
| `rust` | Idiomatic Rust — ownership, lifetimes, traits, async patterns |

**When to invoke:** Reviewing or writing code in a specific language and want it to follow that language's idioms.

### /testing

**Path:** `03-rai/skills/testing/SKILL.md`
**Intent:** Test writing and test review.

**Sub-skills (10):**

| Sub-skill | Purpose |
|-----------|---------|
| `tdd` | Test-driven development — red, green, refactor |
| `pragmatic` | Pragmatic testing — what to test, what to skip (anti-TDD companion) |
| `unit-test` | Add tests to existing untested code (document what it does) |
| `e2e` | End-to-end testing with external service mocking |
| `api-test` | API contract tests, request/response validation (black box) |
| `load-test` | Load/stress/soak testing — k6, locust, jmeter patterns |
| `code-review` | Reviewing code (PR or local diff) + pre-review self-checklist |
| `verify-completion` | Confirming acceptance criteria are met before declaring complete |
| `dependency-audit` | Auditing dependencies for outdated versions, CVEs, license conflicts |
| `tech-debt-map` | Mapping technical debt — coupling hotspots, coverage gaps |

**When to invoke:** Writing tests, reviewing code, or auditing the health of a codebase.

### /ai

**Path:** `03-rai/skills/ai/SKILL.md`
**Intent:** Building LLM-powered systems (NOT consuming the Claude API — for that use the harness `claude-api` skill).

**Sub-skills (2):**

| Sub-skill | Purpose |
|-----------|---------|
| `rag-design` | RAG pipeline design — chunking, embedding, retrieval, re-ranking |
| `agent-design` | Multi-agent architecture — roles, handoffs, memory |

**When to invoke:** Designing AI systems. For Claude API code, use the harness `claude-api` skill.

**Note:** `GAPS.md` defers the planned eval-harness and prompt-patterns sub-skills until proven needed.

### /security

**Path:** `03-rai/skills/security/SKILL.md`
**Intent:** Security testing, review, threat analysis, intelligence aggregation.

**Sub-skills (5):**

| Sub-skill | Purpose |
|-----------|---------|
| `web-assessment` | Web application security testing (authorization required) |
| `prompt-injection` | Prompt injection testing for LLM apps |
| `security-review` | Code-level security review (principles checklist, any stack) |
| `annual-reports` | Indexed annual security reports (references/reports-index.json) |
| `sec-updates` | Aggregate security news from multiple sources in parallel |

**When to invoke:** Anything security-related. Some workflows (e.g., investigation) require explicit user authorization.

---

## Engineering — workflow (3 entries)

### /git

**Path:** `03-rai/skills/git/SKILL.md`
**Intent:** Git workflow operations.

**Sub-skills (5):**

| Sub-skill | Purpose |
|-----------|---------|
| `commit` | Divide the working tree into logical commits and push (always splits, never asks approval) |
| `refactor-clean` | Clean dead code + loose files after a session (auto-delete with git backup) |
| `pr-description` | Generate a clear, complete PR description from the diff/branch |
| `changelog` | Generate a structured changelog between two tags/dates |
| `code-archaeology` | Explore an unfamiliar/legacy codebase via git history (log, blame) |

**When to invoke:** Any git operation that benefits from structure.

### /project-init (LEAF)

**Path:** `03-rai/skills/project-init/SKILL.md`
**Intent:** Interactive wizard to bootstrap project-level Claude Code configuration.

**Has its own `scripts/` directory.** Detects existing state (CREATE vs ENHANCE mode), reads project signals (spec.md, plan.md, package.json, pyproject.toml), and generates `.claude/`, CLAUDE.md, MCPs, and hooks. Used during graduation from idea to project.

### /map-updater (LEAF)

**Path:** `03-rai/skills/map-updater/SKILL.md`
**Intent:** Refresh the navigation index.

Always refreshes `.helm-index/helm-index.md`. Also refreshes `.codemap/codemap.md` when run inside a code project. (No `.codemap/` exists in the helm vault itself — it is only created by this leaf inside a code project.)

**Has its own `scripts/` directory, and is wired to hooks.** PostToolUse on Write (`auto-update-codemap.sh`) and Bash (`codemap-on-bash.sh`) silently call it; settings.json hardcodes its path.

---

## Knowledge and content (8 entries)

### /research

**Path:** `03-rai/skills/research/SKILL.md`
**Intent:** Multi-source information gathering and synthesis.

**Sub-skills (7):**

| Sub-skill | Purpose |
|-----------|---------|
| `web-research` | Generalist multi-source gathering in parallel |
| `extract-wisdom` | Mine insights from a single piece of content |
| `competitor` | Structured competitor teardown / head-to-head |
| `literature` | Academic / peer-reviewed paper survey |
| `market` | Market research — sizing, segmentation, trends, sources |
| `academic` | Formal academic research with methodology + citations |
| `browser` | Single-page browser automation with console/network debugging |

**When to invoke:** Researching a topic, comparing options, extracting wisdom from content.

**Note:** The router SKILL.md description still calls competitor/literature/market/academic "future specializations planned" — that text is stale. All four (plus browser) exist as files.

### /investigation

**Path:** `03-rai/skills/investigation/SKILL.md`
**Intent:** People + infrastructure due diligence (auth required).

**Sub-skills (4):**

| Sub-skill | Purpose |
|-----------|---------|
| `osint` | Open-source intelligence — broad public-data investigation |
| `private-investigator` | People-finding via public records (strict scope) |
| `recon` | Infrastructure mapping (DNS, ports, exposed services) |
| `combo` | Combined workflow when the target is BOTH a person AND their infra |

**Public data only.** Some workflows require explicit user authorization before starting.

### /scraping

**Path:** `03-rai/skills/scraping/SKILL.md`
**Intent:** Web and platform data extraction.

**Sub-skills (2):**

| Sub-skill | Purpose |
|-----------|---------|
| `apify` | Social media + business listings via Apify actors |
| `brightdata` | Progressive escalation through 4 tiers for hard-to-reach URLs |

### /content-analysis

**Path:** `03-rai/skills/content-analysis/SKILL.md`
**Intent:** Pattern + structure mining of content.

**Sub-skills (3):**

| Sub-skill | Purpose |
|-----------|---------|
| `fabric` | Apply Fabric named patterns (240+ available) + find-pattern workflow |
| `parser` | Parse unstructured content into clean typed JSON (auto-detects type) |
| `documents` | Process documents across 4 formats (DOCX/PDF/PPTX/XLSX): create, extract, fill forms, convert |

### /media

**Path:** `03-rai/skills/media/SKILL.md`
**Intent:** Image, video, fiction generation.

**Sub-skills (3):**

| Sub-skill | Purpose |
|-----------|---------|
| `art` | Generate visual content via AI image models (FLUX, GPT-Image-1) |
| `remotion` | Programmatic video via Remotion (React-based) |
| `write-story` | Layered fiction writing (7 interconnected layers) |

### /business

**Path:** `03-rai/skills/business/SKILL.md`
**Intent:** External-facing go-to-market content.

**Sub-skills (3):**

| Sub-skill | Purpose |
|-----------|---------|
| `sales` | Sales narratives + pitch decks from product docs/features |
| `presentations` | Presentation / talk / deck design |
| `pricing` | Pricing page / pricing one-pager / packaging narrative |

**Audience:** Customers, prospects, investors, stakeholders.

**Note:** `/business` shrank from 5 sub-skills to 3 on 2026-05-06 — `proposals` and `prds` MOVED OUT into the new `/writing` router (prose craft). For proposals and PRDs, see `/writing`.

### /writing

**Path:** `03-rai/skills/writing/SKILL.md`
**Intent:** Prose craft — drafting text that reads as written by a real person, not an AI. Every sub-skill enforces the shared anti-AI voice rules in `skills/writing/references/voice.md`.

**Sub-skills (5):**

| Sub-skill | Purpose |
|-----------|---------|
| `arabic` | Arabic prose drafting (MSA + Khaleeji registers; cites references/voice.md + arabic-dictionary.md) |
| `proposals` | Client proposals + RFP responses (MOVED from /business 2026-05-06) |
| `prds` | Product Requirements Document drafting (MOVED from /business 2026-05-06) — distinct from algorithm PRDs |
| `social-media` | Short-form posts for X / LinkedIn / Substack notes |
| `blog` | Long-form blog essays for johndoe.dev |

**When to invoke:** Any prose meant for a human reader where voice matters. Created 2026-05-06; absorbed proposals + prds from `/business`.

### /news-digest (LEAF-like router)

**Path:** `03-rai/skills/news-digest/SKILL.md`
**Intent:** Personalized news digest.

**Version:** v5.6 (2026-06-14).

Sources (6): Hacker News, Reddit, X (Twitter — For You + Following), Substack, Medium, GitHub Trending.

Two modes:
- `day` — last 24 hours → `08-bawaba/daily/YYYY-MM-DD.md`
- `week` — last 7 days → `08-bawaba/weekly/YYYY-WWW.md` (the "Bawaba Weekly" magazine)

Runs HEADLESS via `claude -p`, scheduled on Ubuntu via systemd user timers (daily 03:00, weekly Sat 07:00); migrated off Mac launchd. One sub-skill file: `weekly_style.md` (the "Bawaba Weekly — House Style" reference loaded before the week job writes).

Full chapter: [15-news-digest.md](./15-news-digest.md).

---

## Thinking (1 router)

### /think

**Path:** `03-rai/skills/think/SKILL.md`
**Intent:** Reasoning modes for hard decisions, deep analysis, meta-prompting.

**Sub-skills (12):**

| Sub-skill | Purpose |
|-----------|---------|
| `first-principles` | Strip assumptions, derive from foundational truths |
| `iterative-depth` | 2-8 structured passes, each from a different angle |
| `council` | Structured multi-agent debate (3 rounds → transcript + synthesis) |
| `red-team` | Parallel adversarial agents attack ideas before reality does |
| `evals` | Build/run evaluations for AI agents + model outputs |
| `explain-simply` | Make complex ideas land via analogy/diagram/simple language |
| `be-creative` | Generate diverse high-quality ideas across creative angles |
| `prompting` | Design/refine/optimize prompts for LLMs (meta-prompting) |
| `science` | Apply the scientific method to any domain |
| `world-threat-model-harness` | Persistent world model across 11 time horizons |
| `spec-driven` | Spec-Driven Development thinking mode |
| `systematic-debug` | 4-phase root-cause methodology (Observe, Hypothesize, …) |

**When to invoke:** Hard decisions, deep analysis, multi-angle exploration. Includes a "mode-chaining" section + "when not to use" guardrails.

**Note:** The router SKILL.md description says "10 thinking modes" — that text is stale; there are 12 sub-skills.

---

## Personal (5 routers)

### /life

**Path:** `03-rai/skills/life/SKILL.md`
**Intent:** Self-model + wisdom capture for John. All sub-skills read/write `~/helm/02-ana/`.

**Sub-skills (2):**

| Sub-skill | Purpose |
|-----------|---------|
| `telos` | Update self-model — goals, vision, mindset, who-i-am |
| `quote` | Capture + browse meaningful quotes and personal aphorisms |

**When to invoke:** Updating identity, capturing wisdom. Daily/weekly/monthly rhythm lives in `/routine`.

### /routine

**Path:** `03-rai/skills/routine/SKILL.md`
**Intent:** Daily, weekly, and monthly rhythm for John. All sub-skills read/write `~/helm/02-ana/`.

**Sub-skills (5):**

| Sub-skill | Purpose |
|-----------|---------|
| `journal` | Write daily journal entry — ask questions, document answers |
| `today-prep` | Morning day prep; prioritizes last night's plans, fills gaps |
| `tomorrow-prep` | Evening capture of tomorrow's intentions |
| `weekly-retro` | Structured end-of-week personal retrospective |
| `bills` | Monthly bill-pay run; opens every portal in tabs + non-portal reminders (added 2026-05-16) |

**When to invoke:** Time-based rituals — journaling, daily planning, end-of-week review, monthly bill-pay.

### /mac

**Path:** `03-rai/skills/mac/SKILL.md`
**Intent:** macOS power-user and admin.

**Sub-skills (5):**

| Sub-skill | Purpose |
|-----------|---------|
| `theme` | macOS theming end-to-end (audit vs Omarchy, app adapters, wallpapers, keybinds, pairing) |
| `automation` | macOS automation: Shortcuts.app, Keyboard Maestro, Raycast, Hammerspoon |
| `diagnostics` | macOS hardware + software diagnostics |
| `dotfiles-bootstrap` | "Spilled coffee" skill: restore a full dev environment |
| `tips` | macOS power-user tips, hidden settings |

**Note:** `mac/references/omarchy-palettes.toml` is the single source of truth for Omarchy color palettes — `/ubuntu/theme` reads it cross-router (no fork).

### /ubuntu

**Path:** `03-rai/skills/ubuntu/SKILL.md`
**Intent:** Ubuntu 26.04 + Hyprland power-user and admin. Mirrors `/mac` for the Linux daily driver. Created 2026-06-05.

**Sub-skills (5):**

| Sub-skill | Purpose |
|-----------|---------|
| `theme` | Linux theming end-to-end (audit vs Omarchy; adapters incl. Hyprland border, swaybg) |
| `hyprland` | Hyprland + Wayland desktop config (keybinds, waybar, mako, fuzzel) + Linux automation (systemd/udev/cron) |
| `diagnostics` | Ubuntu/Linux hardware + software diagnostics |
| `dotfiles-bootstrap` | "Spilled coffee" for Linux: restore full Ubuntu + Hyprland env |
| `tips` | Ubuntu/Linux power-user tips |

**Note:** Structurally parallel to `/mac`. The `hyprland` sub-skill replaces Mac's `automation`. Shares the Omarchy palettes from `mac/references/` rather than forking them.

### /investment

**Path:** `03-rai/skills/investment/SKILL.md`
**Intent:** Operate John's values-based paper-trading practice. Strictly spot (no leverage/options/futures/shorts), phase-aware, cloud-only runtime. Strategy + branches live in `~/helm/02-ana/financial/investment/`. Created 2026-05-31.

**Sub-skills (6):**

| Sub-skill | Purpose |
|-----------|---------|
| `status` | Read-only snapshot: strategy posture + both cloud paper engines (crypto bot + equity paper-portfolio) + real holdings + tuition-sleeve usage + debt-first reminder |
| `recommend` | Concrete ranked next investing actions inside constraints (DCA, rebalance, screen, go-live readiness) |
| `screen` | rules-screen a ticker/coin — a screening standard verdict (COMPLIANT/NOT/DEBATED) + ratios + purification + "not professional advice" |
| `review` | Periodic (weekly/monthly) review + improvement loop: bot perf, risk, paper-journal lessons, drift, debt-math, one falsifiable challenger |
| `ops` | Operate the cloud trading bot — status/logs/restart/deploy/freqUI tunnel + guarded go-live gate |
| `convene` | Run "The Restraint Gate" — advisory council (14 lenses), default verdict DO NOTHING, rules chair hard veto (added 2026-06-13) |

**When to invoke:** Status of investments / the cloud paper bot, a recommendation on what to do, a rules-screen, a periodic review, or to operate the cloud bot. Cloud runtime is a DigitalOcean droplet; everything is PAPER (Freqtrade DRY-RUN crypto bot + 4-stream equity paper-portfolio). Full subsystem detail lives with the personal Life OS.

---

## External models (1 leaf)

### /ask-model (LEAF)

**Path:** `03-rai/skills/ask-model/SKILL.md`
**Intent:** Call an external frontier LLM via OpenRouter for a specific task. Created 2026-05-16.

Two models available: «Gemini 3.1 Pro Preview» and «GPT-5.5». Task types: write, translate, judge, critique, summarize, freeform. JSONL-logged to `03-rai/memory/ai-calls/`. Reusable across writing, translation, judging, and freeform second-opinion tasks.

**Has its own `scripts/` directory:** `call.sh`, `compare.sh`, `trio-synth.sh` (the trio-synth flow drafts Gemini + GPT in parallel, then Claude synthesizes one final).

---

## Brain maintenance (2 routers)

### /rai

**Path:** `03-rai/skills/rai/SKILL.md`
**Intent:** Rai brain healthcheck and maintenance.

**Sub-skills (5):**

| Sub-skill | Purpose |
|-----------|---------|
| `sanity` | End-to-end brain healthcheck across 11 tiers (A-K: data safety, env, ChromaDB, pipeline, config, vault+identity, memory index, hygiene, algorithm+agents, skills deep-structure + hook firing, work state + protection) |
| `process-sessions` | Drain `semantic-memory/pending/` into ChromaDB; archive transcripts |
| `compose-agents` | Create new specialized agents on demand |
| `create-skill` | Scaffold a new skill (router or sub-skill); enforces frontmatter, layout, naming |
| `upgrade` | Extract upgrade opportunities from sessions and reflections |

**When to invoke:** Maintaining the brain itself. Run `/rai sanity` weekly (retargeted to `~/helm` and dropped its brain-symlink check on 2026-06-05; now passes end-to-end through tier K). Run `/rai process-sessions` whenever pending accumulates — note ChromaDB is single-writer (Linux coordinator only).

**Note:** `upgrade` has a 90-day tombstone — reconsider 2026-07-22 if not invoked.

### /recall

**Path:** `03-rai/skills/recall/SKILL.md`
**Intent:** Past-session retrieval from ChromaDB.

**Sub-skills (1):**

| Sub-skill | Purpose |
|-----------|---------|
| `history` | Semantic + filter queries over ChromaDB session memory |

**When to invoke:** "What did I work on last week?" "Have I tried this before?" "Find that session about X."

---

## Vault rhythm (6 routers — added beyond the MANIFEST table)

These routers operate on specific vault folders and are part of the day-to-day rhythm. The MANIFEST table still omits all six.

### /triage

**Path:** `03-rai/skills/triage/SKILL.md`
**Intent:** Capture pipeline triage.

**Sub-skills (2):**

| Sub-skill | Purpose |
|-----------|---------|
| `process-landing` | Walk `00-landing/` files: promote to inbox or delete |
| `process-inbox` | For each `01-inbox/` file: research + rate + route |

Full chapter: [04-capture-pipeline.md](./04-capture-pipeline.md).

### /ideas

**Path:** `03-rai/skills/ideas/SKILL.md`
**Intent:** Idea pipeline (Seed → Plant → Tree → Graduated).

**Sub-skills (4):**

| Sub-skill | Purpose |
|-----------|---------|
| `start-seed` | Create a new Seed in `09-ideas/` |
| `promote` | Advance to next stage (Seed→Plant, Plant→Tree) with stage-appropriate research |
| `graduate` | Tree → `05-projects/kitchen/{name}/` with PRD |
| `derive` | Find cross-idea connections; propose hybrids/spin-offs |

Full chapter: [05-idea-lifecycle.md](./05-idea-lifecycle.md).

### /knowledge

**Path:** `03-rai/skills/knowledge/SKILL.md`
**Intent:** Topic notes, MOCs, Insight notes in `10-knowledge/`.

**Sub-skills (4):**

| Sub-skill | Purpose |
|-----------|---------|
| `new-topic-note` | Scaffold a new Topic Note (Simplicity Theorem + sections) |
| `insight` | Propose an Insight Note from two existing notes (propose before creating) |
| `audit-moc` | Check a MOC for drift |
| `find-connections` | Scan notes for emergent-insight opportunities |

Full chapter: [12-knowledge-system.md](./12-knowledge-system.md).

### /learning

**Path:** `03-rai/skills/learning/SKILL.md`
**Intent:** Courses, tutorials, skill acquisition in `06-learning/`.

**Sub-skills (4):**

| Sub-skill | Purpose |
|-----------|---------|
| `start-topic` | Create a new learning topic + progress.md |
| `teach` | Generate a mode-aware lesson (Beginner/Mid/Expert) |
| `quiz` | Retrieval practice on recent lessons |
| `audit-coverage` | Verify topic has full coverage before declaring done |

### /reading

**Path:** `03-rai/skills/reading/SKILL.md`
**Intent:** Book curriculum in `07-reading/`. Parallel to `/learning` but for books.

**Sub-skills (3):**

| Sub-skill | Purpose |
|-----------|---------|
| `start-book` | Scaffold a book curriculum + progress.md + tier plan |
| `teach` | Generate a lesson (Chapter / Law / Practice / Synthesis types) |
| `audit-coverage` | Verify full book coverage before declaring done |

### /work

**Path:** `03-rai/skills/work/SKILL.md`
**Intent:** Work rituals in `04-work/`.

**Sub-skills (2):**

| Sub-skill | Purpose |
|-----------|---------|
| `weekly-planner` | Monday ritual — write the ISO-week plan, reading goals.md and last week |
| `meeting-prep` | Pre-meeting briefing and agenda generator from engagement context |

Full chapter: [14-work-and-projects.md](./14-work-and-projects.md).

---

## Visual explainers (1 router)

### /visual

**Path:** `03-rai/skills/visual/SKILL.md`
**Intent:** Render an idea as a single self-contained, animated HTML file you open in a
browser — Excalidraw-style hand-drawn diagrams, a light/dark toggle, and rich interaction.
All six sub-skills share one engine (`references/engine.html`).

**Sub-skills (6):**

| Sub-skill | Purpose |
|-----------|---------|
| `plan` | Plan a NEW feature / messy multi-file change — the HTML *is* the approval gate before code |
| `explain` | Explain something that ALREADY exists (a system, codebase, concept, decision) |
| `teach` | Teach a concept so the reader genuinely learns it (predict / retrieve / build-up) |
| `compare` | Weigh two-or-more options head-to-head — scored matrix + a recommendation |
| `trace` | Walk a bug / incident / request lifecycle — pulse to the failure point + timeline |
| `data` | Explain a schema / dataset / pipeline (ER, medallion layers, lineage) |

**When to invoke:** "visual plan/explain/teach/compare/trace/data", or "explain this visually".
Outputs land in a disposable `visual/` folder at the project root, one HTML file per artifact.

**Note:** Adapted from BuilderIO's `visual-plan` (the idea, not their stack). Earlier releases of
this kit shipped a single `visual-plan` leaf skill; it is now the `plan` sub-skill of this router.

---

## Skill router groups (conceptual orientation)

From `skills/MANIFEST.md`, augmented to include the routers and leaves the MANIFEST omits:

| Group | Routers / leaves |
|-------|------------------|
| Engineering-domain | architecture, data, devops, coding-standards, testing, ai, security |
| Engineering-workflow | git, project-init, map-updater |
| Knowledge + content | research, investigation, scraping, content-analysis, media, business, writing, news-digest |
| Thinking | think |
| Visual explainers | visual |
| Personal | life, routine, mac, ubuntu, investment |
| External models | ask-model, gemini |
| Brain maintenance | rai, recall |
| Vault rhythm (omitted by MANIFEST table) | triage, ideas, knowledge, learning, reading, work |

These groupings are documentation, not directories. Every skill is at depth 1 in `skills/`. The MANIFEST's own group list does not mention the vault-rhythm routers or the two external-model leaves — another MANIFEST drift signal.

## Adding a new skill

From `skills/MANIFEST.md`:

1. **Scope the workflow.** Write it down manually 3 times first. Patterns that don't survive 3 manual uses don't need a skill.
2. **Run `/rai create-skill`** — it enforces frontmatter, folder layout, naming.
3. **Place in the right router** (or promote to top-level if it's a new domain).
4. **Update `skills/MANIFEST.md`.** (Currently behind — bring it current when you touch it.)
5. **If ambiguous which router**, the skill probably needs a clearer scope, not a new router.

## Naming rules (from MANIFEST + create-skill)

- Folder name: kebab-case, matches frontmatter `name:` field exactly (for top-level routers + leaves).
- Sub-skill filename: kebab-case; its `name:` field matches the filename stem.
- `name:` drives `/invocation` when invoked at top level.
- No name collisions between routers and their sub-skills (a router `/research/` must NOT contain `research.md`).
- Sub-skills are invoked via their router — you type `/architecture` and it reads the requested sub-skill file.
- Frontmatter style is mixed in the live tree: some sub-skills carry YAML frontmatter (`name:`/`description:`), others are plain markdown (H1 + summary line, no frontmatter — e.g. `think/council`, `content-analysis/documents`, `security/web-assessment`, `testing/tdd`). Both are valid.

## Skill counts

- Top-level entries: 35 = 31 routers + 4 leaves.
- Routers NEW since 2026-04-22 (4): `writing` (2026-05-06), `ask-model` (2026-05-16), `investment` (2026-05-31), `ubuntu` (2026-06-05). The top-level count is now 35 (31 routers + 4 leaves).
- Leaves (4): `ask-model`, `map-updater`, `project-init`, `workflow`.
- Sub-skill files (depth-2, excludes SKILL.md): ~134.
- Total `.md` files under `skills/`: ~186. Total files of all types: ~635.

The old manual's "22 skills" figure was wrong even for its own date — the 2026-04-22 baseline already had 29 top-level entries.

> **Counts-block caveat:** `settings.json` carries a `counts` block reading `skills: 66` (and `hooks: 22`). That block is FROZEN at its 2026-04-18 snapshot — the `update-counts.py` hook writes to a non-existent `03-rai/settings.json` path (a known bug; the canonical file is `03-rai/config/settings.json`), so the field never refreshes. Ignore it; the live `skills/` tree is the truth.

## Tombstones (deletion candidates)

| Skill | Deadline | If not invoked by deadline |
|-------|----------|---------------------------|
| `rai/upgrade` | 2026-07-22 | Reconsider / delete |

Tombstones live in `skills/GAPS.md`. (The 2026-04-22 `/ai`-router tombstone has lapsed; the router remains, with the eval-harness and prompt-patterns sub-skills deferred in GAPS until proven needed.)

## What goes in GAPS.md

`skills/GAPS.md` tracks deferred work:

- Open backlog items (next deep-work block) — current examples: recall/history compression, news-digest CSS factoring, the deferred AI sub-skills, the Algorithm PRD.md-vs-META.yaml drift, security authorization-block standardization, media/remotion external services.
- Tombstones (deletion candidates with deadlines).
- Resolved items (recently shipped — kept temporarily for cross-reference; most of the 2026-04-22 reorg gaps are marked DONE).

Read GAPS.md when wondering "what skill am I missing?" or "is this skill ready or planned?"

## Common invocation patterns

### Sequential

```
/triage process-landing      # clean up landing
/triage process-inbox        # then process inbox
```

### From inbox to ideas

```
/triage process-inbox        # rates an item as "Idea seed -> 09-ideas/"
/ideas start-seed "name"     # creates the seed
```

### Idea to project

```
/ideas promote my-idea       # seed -> plant
/ideas promote my-idea       # plant -> tree
/ideas graduate my-idea      # tree -> kitchen/
```

### Sanity check

```
/rai sanity                  # full healthcheck (tiers A-K)
/rai process-sessions        # drain pending (Linux coordinator only)
```

### Research → knowledge

```
/research web-research "topic"       # gather sources
/knowledge new-topic-note "topic"    # scaffold note
/knowledge audit-moc                 # check MOCs after adding
```

### Second-opinion / external model

```
/ask-model "critique this draft"     # OpenRouter (Gemini 3.1 Pro / GPT-5.5)
```

### Code change with quality gate

```
[do edits]
/simplify                    # platform capability — review for quality
/git commit                  # commit the change
```

## Where to look when a skill is missing or broken

- `skills/MANIFEST.md` — what routers/sub-skills exist (STALE — undercounts; cross-check against the live tree)
- `skills/GAPS.md` — what is deferred or tombstoned
- `skills/{router}/SKILL.md` — the router itself
- `skills/{router}/{sub-skill}.md` — the sub-skill
- `/rai sanity` — flags missing or broken skill files (its tier validates every `skills/{name}/SKILL.md`)
- `/rai create-skill` — scaffold a new one with correct structure
