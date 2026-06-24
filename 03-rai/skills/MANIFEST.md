# Skills Manifest

35 top-level entries: 30 routers + 5 leaves. Sub-skills live as `.md` files inside router folders. Claude Code discovers `skills/*/SKILL.md` at depth 1; routers dispatch to their sub-skill files internally.

Naming: all folders kebab-case. Router `SKILL.md` has `name:` matching folder. Sub-skill filenames are kebab-case; their `name:` matches the filename stem.

## Top-level layout

| Type | Skill | Sub-skills | Intent |
|------|-------|-----------|--------|
| R | **architecture** | data-architect, solution-architect, system-design, adr-writer, migration-playbook, patterns, create-cli | System design, ADRs, migration, patterns |
| R | **data** | sql-patterns, streaming | Tactical data patterns |
| R | **devops** | docker, cloudflare, kubernetes, ci-cd, monitoring | Infra + ops + observability |
| R | **coding-standards** | python, typescript, go, rust | Per-language style + review |
| R | **testing** | tdd, pragmatic, unit-test, e2e, api-test, load-test, code-review, verify-completion, dependency-audit, tech-debt-map | Test-write + test-review |
| R | **ai** | rag-design, agent-design | AI engineering (RAG + agents) |
| R | **git** | commit, refactor-clean, pr-description, changelog, code-archaeology | Git workflow |
| R | **security** | web-assessment, prompt-injection, security-review, annual-reports, sec-updates | Security testing, review, reports |
| R | **think** | first-principles, iterative-depth, council, red-team, evals, explain-simply, be-creative, prompting, science, world-threat-model-harness, spec-driven, systematic-debug | 12 reasoning modes |
| R | **research** | web-research, extract-wisdom, competitor, literature, market, academic, browser | Info gathering + synthesis |
| R | **investigation** | osint, private-investigator, recon, combo | People + infra due diligence (auth required) |
| R | **scraping** | apify, brightdata | Multi-page extraction |
| R | **content-analysis** | fabric, parser, documents | Pattern + structure mining |
| R | **media** | art, remotion, write-story | Images, video, fiction |
| R | **business** | sales, presentations, pricing | External-facing go-to-market content |
| R | **writing** | arabic, proposals, prds, social-media, blog | Prose craft (anti-AI voice). Shared `references/voice.md`. |
| R | **life** | telos, quote | Self-model + wisdom capture (reads/writes `02-ana/`) |
| R | **routine** | journal, today-prep, tomorrow-prep, weekly-retro | Daily/weekly rhythm (reads/writes `02-ana/`) |
| R | **investment** | status, recommend, screen, review, ops | Sharia-compliant investing — status, recs, screening, review, cloud-bot ops (reads/writes `02-ana/financial/investment/`) |
| R | **mac** | theme, automation, diagnostics, dotfiles-bootstrap, tips | macOS power-user + admin |
| R | **ubuntu** | theme, hyprland, diagnostics, dotfiles-bootstrap, tips | Ubuntu/Hyprland power-user + admin |
| R | **rai** | sanity, process-sessions, compose-agents, create-skill, upgrade | Brain maintenance |
| R | **recall** | history | Past-session retrieval |
| R | **learning** | start-topic, teach, quiz, audit-coverage | Courses + tutorials (reads/writes `06-learning/`) |
| R | **reading** | start-book, teach, audit-coverage | Book curricula — full coverage (reads/writes `07-reading/`) |
| R | **knowledge** | new-topic-note, insight, audit-moc, find-connections | Topic notes, MOCs, insights (reads/writes `10-knowledge/`) |
| R | **ideas** | start-seed, promote, graduate, derive | Idea pipeline Seed→Tree→graduate (reads/writes `09-ideas/`) |
| R | **triage** | process-landing, process-inbox | Capture triage: landing + inbox |
| R | **work** | weekly-planner, meeting-prep | Work rituals (reads/writes `04-work/`) |
| L | **project-init** | — | New project scaffolding (own scripts dir) |
| L | **map-updater** | — | Navigation index refresh (wired to hooks) |
| L | **news-digest** | — | Curated news feed from HN, Reddit, X, Substack, GitHub Trending |
| L | **ask-model** | — | Call Gemini 3.1 Pro Preview or GPT-5.5 via OpenRouter for write/translate/judge/critique/summarize/freeform. JSONL-logged. |

## Groups (conceptual, for orientation)

Groups map clusters of related routers. They are documentation, not directories.

- **Engineering-domain**: architecture, data, devops, coding-standards, testing, ai, security
- **Engineering-workflow**: git, project-init, map-updater
- **Knowledge + content**: research, investigation, scraping, content-analysis, media, business, writing, news-digest, knowledge, learning, reading, ideas, triage
- **Thinking**: think
- **Personal**: life, routine, work, mac, ubuntu, investment
- **Brain maintenance**: rai, recall

## Routers and sub-skills

Routers hold sub-skills as kebab-case `.md` files inside the folder (e.g. `think/council.md`, `testing/tdd.md`, `mac/theme.md`).

## Adding a new skill

1. Scope the workflow. Write it down manually 3 times first. Patterns that don't survive 3 manual uses don't need a skill.
2. Run `/rai/create-skill` — it enforces frontmatter, folder layout, naming.
3. Place in the right router (or promote to top-level if it's a new domain).
4. Update this manifest.
5. If ambiguous which router, the skill probably needs a clearer scope, not a new router.

## Naming rules

- Folder name: kebab-case, matches frontmatter `name:` field exactly (for top-level routers + leaves).
- Sub-skill filename: kebab-case; its `name:` field matches the filename stem.
- `name:` drives `/invocation` when invoked at top level.
- No name collisions between routers and their sub-skills (a router `/research/` must NOT contain `research.md`).
- Sub-skills are invoked via their router — you type `/architecture` and it reads the requested sub-skill file.

## Changes — 2026-06-05 ubuntu router

### Structural
- Created `/ubuntu/` router — sibling of `/mac` for the Ubuntu 26.04 + Hyprland daily driver.
- 5 sub-skills: theme, hyprland, diagnostics, dotfiles-bootstrap, tips
- Canonical Omarchy palettes stay in `mac/references/` — `/ubuntu/theme` reads them cross-router; single source of truth, no fork.
- `hyprland` sub-skill replaces the Mac's `automation` (systemd user units / udev / Hyprland IPC instead of Raycast/KM/Hammerspoon).

## Changes — 2026-05-03 writing router

### Structural
- Created `/writing/` router for prose craft. Distinct from `/business/` (go-to-market content) and `/media/write-story` (fiction).
- 5 sub-skills: arabic, proposals, prds, social-media, blog
- Moved `business/proposals.md` → `writing/proposals.md`
- Moved `business/prds.md` → `writing/prds.md`
- New shared reference: `writing/references/voice.md` (anti-AI-persona ruleset, single source of truth)

### Content
- New sub-skills: `arabic` (MSA + Khaleeji registers), `social-media` (X/LinkedIn/Substack notes), `blog` (johndoe.dev essays)
- Synced `business/SKILL.md` to reflect actual sub-skill set (sales, presentations, pricing — proposals + prds gone)
- All 5 writing sub-skills cite `references/voice.md` as voice mandate

### Rationale
- `/business` previously claimed `proposals`/`prds` as "future specializations" but the files existed. Confusing. Moved them to where prose craft lives.
- `/writing` centralizes the anti-AI-persona voice rules — banned-word list, em-dash rule, sentence rhythm, ownership voice — so updates propagate to all 5 sub-skills.

### Tombstones
- `arabic` voice anchors flagged TBD — needs 3-5 real Arabic samples in `~/helm/02-ana/voice-samples/arabic/` to graduate from "neutral business MSA" defaults.
- `social-media` LinkedIn anchors flagged TBD — drop 2-3 past LinkedIn posts at `~/helm/02-ana/voice-samples/linkedin/`.

## Changes — 2026-04-22 big reorg

### Structural
- Dissolved `/utilities/` (13 sub-skills redistributed across new routers)
- Created 11 new routers: architecture, data, devops, coding-standards, testing, ai, git, life, mac, rai, recall
- Promoted `project-init` to top-level leaf
- Kept `map-updater` at top level (settings.json hooks hardcode its path)
- Moved + renamed: `mac-theme` → `mac/theme`, `rai-upgrade` → `rai/upgrade`, `history-recall` → `recall/history`, `utilities/test` → `testing/unit-test`
- Absorbed top-level leaves into routers: `commit`, `refactor-clean` → `/git/`; `telos`, `journal`, `today-prep`, `tomorrow-prep`, `quote` → `/life/`; `sanity`, `compose-agents`, `process-sessions`, `create-skill`, `upgrade` → `/rai/`

### Content
- Merged `aphorisms` into `life/quote` (CAPTURE + FIND + SEARCH workflows on one storage). Deleted `aphorisms`.
- Added 38 new sub-skills:
  - Business specializations (4): prds, proposals, presentations, pricing
  - Research specializations (4): competitor, literature, market, academic
  - Coding standards (3): typescript, go, rust
  - Architecture (4): system-design, adr-writer, migration-playbook, patterns
  - Data (2): sql-patterns, streaming
  - DevOps (3): kubernetes, ci-cd, monitoring
  - Testing (6): pragmatic, load-test, code-review, verify-completion, dependency-audit, tech-debt-map
  - AI (2): rag-design, agent-design
  - Mac (4): automation, diagnostics, dotfiles-bootstrap, tips
  - Life (1): weekly-retro
  - Git (3): pr-description, changelog, code-archaeology
  - Think (2): spec-driven, systematic-debug
- Investigation: added `combo` workflow sub-skill
- Think: added mode-chaining section + when-not-to-use guardrails
- Fabric: added find-pattern workflow
- Sanity: added Tier F5 template integrity + F6 hooks failure-log checks
- Docker: multi-arch build + secrets management sections
- E2E: external-service mocking
- Solution-architect: microservices, event-driven, saga, compliance (HIPAA, GDPR, GDPR)
- Data-architect: cross-references to `/data/streaming` and `/data/sql-patterns`

### Fixed
- `create-skill` naming rules updated for router + sub-skill layout
- `project-init` path bug: `project_init` underscore → `project-init` kebab
- `sanity` critical-skills check updated for moved paths

### Tombstones
- `rai/upgrade` — reconsider 2026-07-22; delete if not invoked
- `/ai/` — reconsider 2026-06-22; add more sub-skills only if used

## Routers that are intentionally small

- `/business/`, `/research/`, `/data/`, `/ai/`, `/recall/` — single-domain routers where size reflects current scope, not intent. They will grow as sub-skills prove themselves through use.

## Prior reorgs (brief)

- 2026-04-22 Phase A–F: identity/config moves, `/business/` split out, `/utilities/` pruning, GAPS.md creation, MANIFEST as ownership map.
- 2026-04-22 Big Reorg: this document. Developer-domain routers + 38 new sub-skills.
