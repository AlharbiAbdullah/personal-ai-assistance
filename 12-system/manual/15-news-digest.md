# 15 — News Digest

*Last updated: 2026-06-14.*

`/news` produces a personalized digest of what is worth attention from across the major tech and culture sources. Two outputs: a **daily digest** (a curated social feed of gems) and a **weekly magazine** ("Bawaba Weekly"). Output lands in `08-bawaba/`. The skill is at **v5.6**, runs fully unattended on the Ubuntu box via systemd timers driving headless `claude -p`, and dedups forever against a git-tracked seen-URL ledger.

This chapter describes the live skill. The source of truth is the skill itself (`03-rai/skills/news-digest/SKILL.md`, ~1200 lines) and the output folder rules (`08-bawaba/CLAUDE.md`). When this chapter and those files disagree, they win.

## Skill

**Name:** `/news` (alias for `news-digest`)
**Path:** `03-rai/skills/news-digest/SKILL.md` (v5.6 header)
**Type:** Router with a single sub-skill file (`weekly_style.md`, the Bawaba Weekly house-style guide). No longer a pure leaf.

The skill directory carries its full machinery, not just a prompt:

| File | Purpose |
|------|---------|
| `SKILL.md` | Full workflow spec, v5.6. Single source of truth for process. |
| `config.yaml` | All tunable inputs: source targets, scroll tuning, retry ladder, scoring weights, relevance tiers, caps, dedup, cross-helm context, weekly knobs. `format_version: "v5.5"` (skewed — not bumped to v5.6). |
| `present_v5.py` | Daily presentation engine (~76 KB). Scores, dedups vs ledger, ranks, enforces diversity + X-share rebalance, emits the markdown skeleton with fill placeholders. |
| `weekly_mine.py` | Weekly miner. Buckets a Sun→Sat week of raw dumps into department briefs. Read-only over dumps. |
| `weekly_style.md` | Bawaba Weekly house-style guide (v3). Device budgets, banned-words ledger, structure contract, grep-gated self-review. |
| `seen_ledger.jsonl` | Persistent cross-day dedup ledger. Git-tracked, append-only, never pruned (~2,831 records / 446 KB at survey). |
| `_collect_x_headless.py` | Primary X collector (v5.6). Headless Chrome over raw CDP. |
| `_collect_curl.py` | Curl collector for HN + Reddit + GitHub Trending. |
| `_collect_reddit_rss.py` | Reddit Atom-RSS fallback for when the JSON API 403s. |
| `_enrich_substack.py` / `_enrich_medium.py` | Mandatory body/engagement/date enrichment. |
| `_backfill_ledger.py` | One-off v5.4 migration that seeded the seen-URL ledger from prior digests. |
| `substack_subscriptions.json` | Cache of John's Substack subs (77 feeds). |
| `chrome_snippets/` | Browser observers (`x_observer.js`, `substack_observer.js`, `medium_observer.js`) injected via `javascript_tool`. |
| `scheduled/run-news-ubuntu.sh` | The active automation runner (Ubuntu headless `claude -p`). |

`scheduled/run-news.sh` (the old Mac WezTerm runner) and `recovery-prompt.txt` (an old X-scroller diagnostic prompt) are retired but kept in-repo as rollback reference.

## Output destination

```
08-bawaba/
├── CLAUDE.md
├── daily/
│   └── YYYY-MM-DD.md          ← daily digest (current day only; priors auto-rotate to archive)
├── weekly/
│   └── YYYY-WWW.md            ← Bawaba Weekly magazine (e.g. 2026-W24.md; ISO week)
├── story-arcs.md             ← named multi-week narrative threads (feeds the weekly's "The Fold")
├── scraping/                 ← Playwright auth profile + .venv (fallback-collection infra)
└── .scratch/                 ← debug capture JSONs
```

The flat `YYYY-MM-DD.md` / `YYYY-MM-DD-weekly.md` layout of the previous manual is gone. Output is now split into `daily/` and `weekly/` subfolders, and the weekly file is named by ISO week (`YYYY-WWW.md`), keyed to the Saturday it covers.

`_graduated.md` (the gem-graduation log) is documented in `SKILL.md` and `08-bawaba/CLAUDE.md` but is currently absent from disk — it was dropped in a cleanup commit and is recreated on the first graduation.

## Sources

The skill collects from **6 sources** (X's two phases count as one source):

| # | Source | Method (v5.6) | Target | Cap |
|---|--------|---------------|--------|-----|
| 1a | **X For You** | `_collect_x_headless.py` (headless CDP, primary) | 1000 | uncapped |
| 1b | **X Following** | same headless run, `--phase following` | 500 | uncapped |
| 2 | **Substack** | Chrome MCP (`substack_observer.js`), Load-more loop on `/inbox` | 200 | uncapped |
| 3 | **Medium** | Chrome MCP (`medium_observer.js`), one "More" click on `/me/following-feed/all` | 30 | 5 daily / 10 weekly |
| 4 | **Hacker News** | curl/Python (`topstories` day / `beststories` week) | 100 | 10 daily / 15 weekly |
| 5 | **Reddit** | curl JSON API across 18 subs (RSS fallback) | ~200 | uncapped |
| 6 | **GitHub Trending** | curl/Python (HTML parse) | 20 | 4 in digest |

**Accounts:** X = `@johndoe` (now **X Premium**); Substack = `@johndoe`; Medium = Google SSO.

The 18 Reddit subreddits (config `reddit_subs`): dataengineering, devops, ClaudeCode, LocalLLM, ollama, mcp, AI_Agents, aiagents, MachineLearning, mlops, PromptEngineering, Rag, learnmachinelearning, dataops, datascience, softwarearchitecture, artificial, ExperiencedDevs.

Each run's raw dumps land in `.runs/YYYY-MM-DD/` (one JSON per source) and are then copied to `13-archive/news/dumps/YYYY-MM-DD/` (git-tracked, synced) — every collected item is kept forever, not just the ~100 displayed. That durable dump archive is the weekly miner's primary input.

## The X Premium + headless CDP collector (v5.6)

This is the headline change since the manual was last written. The recurring X under-collection (≈189 collected vs a 600 target) was never a scroll bug — it was the **free account's ~1,000/day per-account read cap**, often pre-burned before the 3am run.

- `@johndoe` is now **X Premium**: read cap raised from ~1,000/day to ~10,000/day. The target stopped being the wall.
- X collection now runs via `_collect_x_headless.py` as the **primary** path, not the Chrome MCP scroller. It clones live Chrome cookies into a throwaway profile, drives `google-chrome --headless=new` over **raw CDP**, and runs a Python-driven humanized scroll. No MCP extension pairing (the #1 cause of 3am hangs) and no 45-second `javascript_tool` CDP cap.
- Run via `uv` (the `websocket-client` dep is supplied by inline script metadata; system python is never touched):

```bash
uv run ~/helm/03-rai/skills/news-digest/_collect_x_headless.py \
  --date YYYY-MM-DD --target 1000 --following-target 500 --phase both
```

- It is a blocking foreground call (ideal under `claude -p`), writes `x_foryou.json` + `x_following.json`, and streams progress to `x_headless_status.json`.
- **Exit codes:** `0` ok · `2` chrome/devtools failure · `3` not logged in (also writes `x_LOGIN_FAILED.json`). It never silently ships zero X.
- **Reload-cycle recovery:** a fresh page load serves ~10–19 tweets even when scroll pagination is starved, so the collector harvests across reload cycles rather than spinning.
- **Gentle on purpose:** target 1000 is ~10% of the Premium cap, not a 2000-tweet burst (that burst pattern soft-flagged the account into a throttle on 2026-06-13/14).
- The Chrome-MCP detached scroller and its W1–W6 burn-recovery ladder are kept only as a degraded-day fallback (interactive runs, or if the script's Chrome won't launch). On Premium they are mostly obsolete.

## Two modes

| Mode | Window | Output |
|------|--------|--------|
| `day` | Last 24 hours | `08-bawaba/daily/YYYY-MM-DD.md` |
| `week` | Last 7 days | `08-bawaba/weekly/YYYY-WWW.md` |

Default is `day`. Invoke `/news` or `/news day`; invoke `/news week` for the magazine. Two more triggers exist:

| Trigger | Behavior |
|---------|----------|
| `/news chat` | Companion mode — discuss today's items. Surfaces canonical chat prompts from config. |
| `graduate gem N, N` | Save gems for Saturday review (appends to `_graduated.md` + the run's `graduations.json`). |
| `/news review` | Saturday walkthrough of graduated gems (part of `11-workflows/08-weekly-review.md`). |

## Scoring algorithm (6 axes)

Each item is scored 0–5 on six axes, weighted in `config.yaml`:

```
gem_score = teaches*3.0 + tool_discovery*2.0 + artifact*2.0
          + discussion_quality*1.5 + contrarian_evidence*1.0 + postmortem*2.0
```

Max `gem_score` is **57.5**. Then two multipliers:

- **Relevance multiplier** (best-fit bucket): `1.0` data engineering / system design / distributed systems / product shipping / startup thinking · `0.9` AI research / agents / RAG / benchmarks / local-regional / energy / regional tech · `0.7` career / culture / interviews / Claude Code / AI tools · `0.3` frontend / mobile / gaming / unrelated.
- **Project bonus** `× 1.2` for a genuine active-project connection. Active projects (as listed in config): Taskflow, Helios, OpenKit, Dataforge, Rai, GeoContext, Matchbox.

> Known drift (config, stale project names): this list is what `config.yaml` carries, but two entries are no longer current. **Taskflow** was canonicalized to **helios** and **Matchbox** was deleted as an idea in May 2026 (see [chapter 14](./14-work-and-projects.md)). They are flagged here rather than rewritten in the config because the skill reads this list verbatim; the same stale pair appears in the Link tags below.

`final = gem_score × relevance_mult × project_mult`. Theoretical max = `57.5 × 1.0 × 1.2 = 69`; real daily max ≈ 40.

A **source affinity** multiplier folds in afterwards (re-clamped to [0,100]): x_foryou 1.4, x_following 1.4, hn 1.1, substack 1.1, medium 1.0, reddit 0.9, github 0.7.

**Letter grades** for display (against the real ≈40 ceiling): **≥35 S · 25–34 A · 18–24 B · 12–17 C · <12 filtered.**

Each gem carries a hidden HTML comment recording its full score breakdown (`<!-- scores: t=5 td=3 a=4 ... final=46.2 -->`).

Note that Claude Code is bucketed at `0.7` relevance, not the top tier — a deliberate guard against recency bias. The earlier "Claude Code is MEDIUM not HIGH" rule survives as this multiplier.

## Personalization — the relevance lens

Before scoring, the skill loads `cross_helm_context` from config: `.helm-index/helm-index.md`, `02-ana/identity/who-i-am.md`, `02-ana/tech-stack.md`, `02-ana/telos.md`, `05-projects/active/*/Brief.md`, `09-ideas/*.md`, `10-knowledge/_mocs/*.md`. **`04-work/` is explicitly excluded** (work content does not belong in the news feed).

> Known drift (config, stale paths): three of those `cross_helm_context` entries no longer match the vault. `05-projects/active/*/Brief.md` resolves to nothing — there is no `05-projects/active/` directory on disk, and auto-generated `Brief.md` is a retired pattern (see [chapter 14](./14-work-and-projects.md) and `05-projects/CLAUDE.md`). `02-ana/telos.md` does not exist either — telos is a `/life` sub-skill that writes to `02-ana/identity/{goals,vision,mindset,who-i-am}.md`, not a single file. These are config the skill actually reads, so they are flagged as drift here rather than silently rewritten in the skill; the surviving entries (helm-index, who-i-am, tech-stack, ideas, MOCs) still load and carry the relevance lens.

The "For You" intent — that the digest reflects John's full identity rather than a generic tech-news ranking — is enforced structurally:

- **Top Shelf diversity:** max 4 per topic, max 8 per source, ≥50% identity-matched, score ≥12, anti-cluster reorder.
- Per-source caps (Hacker News, Medium, GitHub) prevent any single source from flooding.
- The global `max_source_pct` is 0.35.

## Daily digest format — 6 sections

The header is compact: YAML frontmatter holds only `date` (one Obsidian Properties row). Counts live in a body markdown table (`collected` / `in digest` per source) plus one `Sections:` line. The "Run notes" telemetry footer was removed in v5.5.

The body is six sections in fixed order:

1. **News Wire** (≤15) — a general tech-world brief, trend-ranked, X-majority (~55%+), **no identity scoring** and no local/project guarantees. Each item is one neutral wire-service sentence. (Changed in v5.4: News Wire used to be personalized; it is now deliberately general.)
2. **Hot Topics** (0–3, Claude-filled) — a theme qualifies only if ≥5 items converge. Skipped on quiet days.
3. **Top Shelf** (~20–30 gems) — cross-source ranked with the diversity rules above.
4. **Feed** (~60 gems) — score order, then X-share rebalance.
5. **Wisdom** (0–3 quotes) — Model + Insight filled by Claude.
6. **Deep Dive** (1 essay + 0–2 "also considered").

**Citation IDs** are per-source in display order: `hn-`, `r-`, `x-`, `gh-`, `sub-`, `m-`.

**Link tags:** identity = `[AI] [Data Eng] [System Design] [DevOps] [local]`; projects = `[Helios] [Dataforge] [Rai] [OpenKit] [GeoContext] [Matchbox] [Taskflow]`; quality = `[Postmortem]`. (Same stale-name drift as the Scoring section: `[Taskflow]` is now `helios` and `[Matchbox]` is a deleted idea — see the drift note under [Scoring algorithm](#scoring-algorithm-6-axes).)

**X-share target band** (`x_share_target: [0.40, 0.55]`, v5.5): X is the primary channel, so the body (Top Shelf + Feed) is pushed toward the upper end (~55% X). The Feed flexes via `rebalance_x_share()` in `present_v5.py`: when under-band, it swaps the weakest non-X Feed items for the best unused on-beat X (AI / DE / SysDesign / DevOps / projects — never regional / finance / viral). News Wire and Top Shelf are untouched. On throttled-X days it stops short rather than padding.

**Hook craft spec (v5.4):** a hook is one claim — lead with the non-obvious thing, ground it in interest areas (not project name-drops), end with a so-what, and pass a "cover-the-title" test. Title-restating, "This post…" openers, and hedge filler are banned. A mandatory self-review pass enforces this.

This is still the gem-feed model the prior manual described — a curated social feed of gems, not a newspaper — now formalized into these sections rather than a flat 40–50-item list. Output knobs (`config.yaml`): `gems_total_target [80,100]`, `top_shelf_count [20,30]`, `news_wire_count [10,15]`, `feed_count 60`, `github_max 4`, `deep_dive.candidates 3`, `wisdom.max_items 3`.

## The seen-URL ledger (cross-day dedup, v5.4)

`seen_ledger.jsonl` lives in the skill directory. It is git-tracked, append-only, and never pruned (~25 KB/day; 2,831 records at survey). One JSON record per displayed item, forever.

- Record shape: `{"u": <normalized url>, "t": <normalized title>, "a": <author>, "src": ..., "first_seen": "YYYY-MM-DD", "published": "YYYY-MM-DD"|null}`.
- Two matchers (either one drops an item): URL-normalized (lowercase host, strip trailing slash, drop fragment + tracking query params), and exact normalized title+author (only when both have an author). O(1) lookups.
- **Same-date safety:** records with `first_seen == today` are ignored, so re-runs never suppress today's own pool.
- **Old-once rule:** an unseen item passes once even if months old; if its `published` date is older than `dedup.stale_label_days` (=3) it renders with a `published YYYY-MM-DD` note, then is ledgered and never returns.

This replaced the old 3-day digest-parsing dedup, which broke because the presenter archived `daily/` mid-cycle — re-runs found zero priors and resurfaced a stale April item for four-plus days. The ledger was backfilled from ~40 prior digests via `_backfill_ledger.py` (seeding ~2.6k records). Dedup is skipped in week mode.

## Weekly magazine — "Bawaba Weekly" (`/news week`)

`/news week` produces a magazine, not a recap. It is described in-repo as "the most important output of the whole skill" — John reads the weekly more than the daily. The design system is **v3**, sealed 2026-06-13 from a 50-agent redesign. Reference issues: 2026-W23 and 2026-W24 (W24 is the quality bar).

**The beat (in scope):** AI, agents / agent engineering, data engineering, data broadly, system design, DevOps / infra. **Out of beat (never their own thread):** security-as-a-subject, regional / local / geopolitics, sports, general world news.

**Departments (fixed order, v3 layout):**

1. **The Fold** — a ≤90-second scan block (week-in-one-line, three things with `#anchor` jumps, number of the week, if-you-read-one-thing, the one decision, read time, previously / next-watch, tag legend).
2. **Editor's Letter** — what the week was about, prose only.
3. **Cover Story** — the week's story as a real feature; fetch the announcement page, never relay secondhand.
4. **Model State** — every model released or updated; opens with a diffable register (same columns weekly + Δ + trajectory arrow), a durable Routing Card, and a comparison table.
5. **The Lesson** — the masterclass (the explicit reason the magazine exists); ends with a concrete how-to (decision tree / checklist / template).
6. **The Stack** — the beat's home: data-eng / data / system-design / DevOps craft (patterns and practice, not industry news). Carries the "cost-per-task not cost-per-call" frame.
7. **The Workshop** — tools and repos of the week grouped by job, with "who needs this" verdicts.
8. **Reading Shelf** — 3–5 long reads as an annotated list (read the full text from the dumps first).
9. **Closing — Wisdom** — the best quote of the week expanded into a reflective essay; carries the reference diagram (Mermaid / ASCII of the week's production stack).

The issue is wrapped by a masthead (`BAWABA WEEKLY · No. WWW · Sun Mon D → Sat Mon D, YYYY`), the standing creed *"Not a recap. The work around the model."*, a visible cut-line (*"Cut this week: X, because Y."*), and a `<details>` footer (Coverage · Methodology · Revision log).

**v3 contract devices:** every department carries a one-sentence italic deck (its single falsifiable claim) plus a decision footer (`BUILD-NOW` / `DECIDE` / `WATCH` / `AVOID`). Tags everywhere — decay (`[durable]` / `[perishable]` / `[shelf ~Mon DD]`) and confidence (`[primary]` / `[vendor-claim]` / `[1-practitioner]` / `[projection]`). No word floor; per-department ceilings plus the cut-line keep it tight.

**Inputs (no browser, ever):**

1. **Raw dumps** — `13-archive/news/dumps/YYYY-MM-DD/` for the recent Sun→Sat week (the primary source: topic gravity over everything collected).
2. **The 7 dailies** — from both `08-bawaba/daily/` and `13-archive/news/daily/` (prefer `daily/`).
3. **Web enrichment** — `WebSearch` / `WebFetch` only, cap ~10 fetches (`weekly.web_enrichment`). Fact-hardening is mandatory (a past issue shipped a likely-fabricated claim by under-using its fetch budget).

**Pipeline:** load `weekly_style.md` + `story-arcs.md` → `python3 weekly_mine.py [--week YYYY-WWW]` writes department briefs to `.runs/weekly-YYYY-WWW/` → read briefs + dailies → pick subjects → enrich and harden (fetch primary sources) → write `08-bawaba/weekly/YYYY-WWW.md` → grep-gated self-review → update `story-arcs.md` → rotate the prior weekly to `13-archive/news/weekly/`.

`config.yaml` weekly knobs: `word_target [8000,10000]`, `read_target_min 60`, plus mining thresholds (`lesson_min_days 3`, `cluster_min_items 5`, `model_min_items 2`, etc.).

> Known skew: `config.yaml weekly.departments` still lists the old 7-department set and omits "The Stack". `weekly_style.md` and `SKILL.md` (the v3 authority) are correct. Treat the config block as stale.

## Headless execution via `claude -p`

The skill runs unattended on the Ubuntu box. The runner `scheduled/run-news-ubuntu.sh` drives the skill via:

```bash
claude -p --chrome --dangerously-skip-permissions --output-format text
```

No terminal multiplexer and no WezTerm — John moved to Ghostty, and the WezTerm interactive layer was deleted 2026-06-09. The old interactive `claude --chrome` path hit a one-time "Bypass Permissions → Yes, I accept" prompt that blocks unattended sessions forever; `-p` shows no such prompt and the Skill tool works under it.

**The critical `-p` rule** (`HEADLESS_NOTE`, injected into every scheduled prompt): under `claude -p` the process terminates the instant the turn ends, background-task completion does not re-invoke, and any spawned background process is killed. So the agent must **never end its turn to wait for a background collector** — it polls from the foreground with a blocking loop. (This is the 2026-06-12 bug: the agent ended its turn to "wait" for a background X collector 12 seconds before it hit 2003 tweets, and systemd killed the cgroup, producing zero output.)

**Watchdog and retry:** `WATCHDOG_SEC` defaults to 7200s (120 min). `synthesis_reserve_min: 35` means collection must end by start+85min. On failure the runner auto-retries once after `RETRY_DELAY_SEC` (default 600s) with a **budget-protecting retry prompt** that reuses the same day's `.runs/` dumps instead of re-collecting — X's read budget is account-level and does not reset within the day, so re-scraping would burn the retry's coverage.

**`digest_ok` gate:** the output file must exist, contain no fill placeholders (`CLAUDE_FILL` / `<!-- raw:` / `<!-- CLAUDE`), and exceed 2000 bytes (daily) or 20000 bytes (weekly).

A **pairing preflight** (daily only) probes `mcp__claude-in-chrome__list_connected_browsers` and asserts a local browser, restarting Chrome up to twice — aborting in minutes rather than hanging. Caveat: while the Mac is signed into the same Claude account it appears as a remote browser, so the prompt best-effort selects the local one.

## Scheduling — Ubuntu systemd timers (migrated off Mac launchd)

News automation moved off the Mac entirely. The Mac launchd jobs and the WezTerm interactive path are retired; scheduling now lives on the Ubuntu box (`pc`) as systemd **user** timers:

| Timer | When | What |
|-------|------|------|
| `news-daily.timer` | 03:00 daily | Drives local logged-in Chrome (X via headless collector + Substack/Medium via MCP); writes `daily/`. |
| `news-weekly.timer` | Saturday 07:00 | No browser — runs `weekly_mine.py` + reads dailies + WebSearch/WebFetch; writes the magazine to `weekly/`. |

The `.timer` / `.service` unit files are not checked into the helm repo — only `run-news-ubuntu.sh` is. The units live in the Ubuntu user's systemd directory. Run logs go to `~/.local/state/news-digest/logs/` (outside the repo, to avoid per-run log-commit churn).

This fits the vault's sync topology: since 2026-06-13 the Ubuntu box is the sole coordinator and only origin writer, while the Mac is a passive replica over Tailscale SSH. The news jobs run on Ubuntu, which is also where the dumps and digests are committed. See `03-rai/SYNC-ARCHITECTURE.md`.

## Daily pipeline (in order)

```
0. Load cross-helm context (identity, tech-stack, ideas, MOCs; 04-work excluded)
   (config also names telos.md + active/*/Brief.md — both stale, see Personalization drift note)
1. Collect:
   Phase 1 (browser, sequential): X (headless, primary) → Substack → Medium
   Phase 2 (curl, parallel): Reddit + Hacker News + GitHub
1.4 Enrich Substack + Medium (MANDATORY — bodyless items score ~0 and never reach the digest)
1.5 Dedup vs seen-URL ledger (skipped in week mode)
1.6 Cross-source dedup (merge the same story across HN/Reddit/X/Substack)
2. Filter + score (6 axes) + per-source caps + order descending
3. Synthesize: python3 present_v5.py --date YYYY-MM-DD --out YYYY-MM-DD.md
   (emits a SKELETON with <CLAUDE_FILL_*> + <!-- raw: --> + <!-- CLAUDE INSTRUCTIONS --> blocks)
4. Claude fills: News Wire → Hot Topics → Top Shelf hooks → Feed hooks → Wisdom → Deep Dive
   → hook self-review pass → update section counts → strip ALL raw/instruction blocks
5. Save to 08-bawaba/daily/YYYY-MM-DD.md
6. Post-run cleanup (every exit path): close all MCP/Playwright tabs; never touch the main Chrome
```

The synthesis step splits work between a deterministic Python script (scoring, dedup, ranking, skeleton) and Claude (editorial fills). A verification gate must pass before the digest is considered done — all three greps must return 0:

```
grep -c "CLAUDE_FILL" <file>     # 0
grep -c '<!-- raw:'   <file>     # 0
grep -c '<!-- CLAUDE' <file>     # 0
```

`present_v5.py --test` writes `.runs/<date>/preview.md` and skips both the archive rotation and the ledger append.

## Hard rules (North Star)

The skill enforces 7 user rules (set 2026-05-06, overriding everything including wall-time) plus legacy rules:

1. **Time and speed are irrelevant** — John reads 10+ hours later; never optimize for "fresh."
2. **Per-source count matters** — hit the targets.
3. **Humanize — be cautious** — random delays, jitter, dwell.
4. **Fully automated** — zero permission prompts during collection.
5. **Quality is non-negotiable** — 6-axis scoring, ruthless filter.
6. **No overlap — two dedup layers** — cross-day ledger + cross-source merge.
7. **Understand the user** — Step 0 context load is mandatory.

Legacy rules #8–#14: never skip a source · X is a dealbreaker (no X → abort with a marker) · 10-attempt retry ladder · one Chrome tab per source · Playwright is the final fallback · partial ≥90% counts as success · the AI does not negotiate with itself (it does not decide to skip a source).

### X is required

> No X, no news. If X collection fails, abort the whole run. Never ship a digest without X.

X is the highest-signal source. If X collection fails in an interactive run, the digest is incomplete and the run aborts.

### Scheduled-mode override (v5.2)

When the launch prompt declares **scheduled mode**, **"ship a digest" outranks rule 1 (time) and rule 9 (X dealbreaker)** — a partial-coverage digest beats no digest, because the watchdog kills the session at the deadline and zero output is the only unacceptable outcome. Interactive `/news` runs ignore this override and use the full ladder.

### Hide media on X

> Hide all videos/images via CSS before scrolling X. Read text only, never view media.

The X collector reads text only — no media is fetched or rendered. This keeps the scroll fast and avoids attention-tax from autoplay.

### Zero permission prompts

> /news must run fully autonomous, zero permission prompts during collection.

Collection happens without asking. All required permissions are pre-allowed in the canonical settings file (`03-rai/config/settings.json`, reached via `~/.claude/settings.json`), and the scheduled runner passes `--dangerously-skip-permissions`.

## story-arcs.md and gem graduation

### story-arcs.md

`08-bawaba/story-arcs.md` tracks named multi-week narrative threads that play out over many issues (e.g. a model-family rollout, a retrieval-architecture debate). It is maintained by `/news week` and feeds the weekly's "The Fold" department (the previously / next-watch lines). At survey there were 5 active threads (e.g. Mythos-class rollout, retrieval reckoning, economics-vs-capability gap, open-weight floor, layering tax) and 0 resolved.

### Gem graduation

When a digest item is more than just news — an idea seed, a knowledge nugget, a project lead — it gets graduated:

1. During the week, `graduate gem N, N` appends the item to `_graduated.md` and the run's `graduations.json`.
2. On Saturday, `/news review` (part of `11-workflows/08-weekly-review.md`) walks the graduated gems.
3. Survivors move on: `09-ideas/{name}.md` via `/ideas start-seed` for an idea seed, or `10-knowledge/{domain}/` for a knowledge nugget that fits a Topic Note.

The original digest entry stays in `08-bawaba/` — digests are immutable.

## Rules from CLAUDE.md (08-bawaba/)

> Generated content only. This folder is the output target of the `/news` skill.

> Digests are immutable after creation. A daily digest reflects what was relevant on that date. Do not retroactively edit.

> Gaps are okay. If a day was skipped, leave the gap. Do not backfill.

> Never delete the live `daily/` files. (A 2026-06-11 maintenance run wrongly deleted the live `daily/` digest plus the archive exceptions and it all had to be restored.)

### Why immutability

A digest is a time capsule. Editing past digests destroys the historical record of "what mattered when." If the analysis was wrong, the response is a new entry in a future digest, not a retro-edit.

### Why no backfilling

Backfilling produces fake history. If `/news` was not run on a given day, that day is genuinely missing. The gap is honest and useful.

## Archiving

Prior dailies and weeklies do not stay in `08-bawaba/` — they rotate into `13-archive/news/`, which is a standing never-purge exception (John-approved 2026-06-10):

| Archive path | Contents |
|--------------|----------|
| `13-archive/news/daily/` | Rotated daily digests (41 at survey). |
| `13-archive/news/weekly/` | Rotated weekly issues. |
| `13-archive/news/dumps/YYYY-MM-DD/` | Full raw collected JSONs per run (23 day-dirs at survey) — the weekly miner's primary input. |

These are git-tracked and synced. The dumps archive keeps every collected item forever, not just the ~100 displayed in any digest.

## Failure modes

| Failure | What happens |
|---------|--------------|
| X collection fails (interactive) | Abort. Do not ship the digest. Write an abort marker. |
| X collection fails (scheduled mode) | Ship a partial digest — zero output is the only unacceptable outcome. |
| X collector exit 3 (not logged in) | Writes `x_LOGIN_FAILED.json`; never silently ships zero X. |
| One source fails (e.g. Substack) | Retry up to 10 attempts (chrome → fresh chrome → Playwright), then continue with the rest. |
| Substack/Medium not enriched | Items score ~0 and never reach the digest — enrichment is mandatory, not optional. |
| Scoring produces 0 S/A items | Continue; ship with B and C. |
| Background collector under headless `-p` | Never end the turn to wait — poll from the foreground or systemd kills the cgroup. |
| Permission prompt during collection | Fail-closed; the scheduled runner passes `--dangerously-skip-permissions`. |

## Scratch artifacts

`.runs/YYYY-MM-DD/*.json`, `08-bawaba/.scratch/`, and `x_headless_status.json` are debug captures. They are useful for verifying what was scraped, reproducing scoring decisions, and debugging output format. Per the current gitignore policy ("nothing informational is gitignored"), informational dumps are tracked — only secrets (`twscrape.db`, `.env`) and machine droppings (`__pycache__/`, `*.pyc`, `.DS_Store`) are ignored.

## Known inconsistencies (current)

- `config.yaml format_version` reads `"v5.5"` while `SKILL.md` is `v5.6` (the v5.6 commit bumped targets and `SKILL.md`, not the format-version string).
- The `SKILL.md` inner ladder and per-source spec rows still show the old `600 / 180` X numbers; the top-of-file Sources table and prose are correct at `1000 / 500`. The ladder mechanics are explicitly marked obsolete on Premium.
- `config.yaml weekly.departments` lists 7 departments and omits "The Stack".
- `_graduated.md` is documented but currently absent (recreated on first graduation).
- `config.yaml cross_helm_context` names two stale paths: `05-projects/active/*/Brief.md` (no `active/` dir; `Brief.md` is a retired pattern) and `02-ana/telos.md` (telos writes to `02-ana/identity/` files, not a single file). See the Personalization drift note.
- The project-bonus list and `[Taskflow]`/`[Matchbox]` link tags name retired/renamed projects: `Taskflow` → `helios`, and `Matchbox` is a deleted idea (May 2026). See the Scoring drift note.

## Cross-references

- Folder rules: [01-folder-map.md](./01-folder-map.md)
- The skill in the catalog: [07-skills-catalog.md](./07-skills-catalog.md)
- Promoting to ideas: [05-idea-lifecycle.md](./05-idea-lifecycle.md)
- Sync topology (why news runs on Ubuntu): `03-rai/SYNC-ARCHITECTURE.md`

## What /news does NOT do

- It does not push notifications. Output is in the vault; reading is on the user's schedule.
- It does not edit past digests.
- It does not auto-promote items to ideas/knowledge — graduation is a human decision.
- It does not consume audio or video. Text-only.
- It does not generate the news; it curates external sources.
- It does not ship without X (except under scheduled-mode override).
- It does not pull in `04-work/` content — work is excluded from the relevance lens.

## What does the digest replace

The digest replaces doomscrolling X, browsing Hacker News every day, subscribing to too many Substacks, and manually checking GitHub Trending and Medium. The user reads one file per day — pre-filtered, pre-scored, identity-relevant — and one magazine per week. The news layer becomes a tool instead of a tax.
