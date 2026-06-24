# 13 — Personal OS

`02-ana/` — John's Life OS. Identity, journal, todos, quotes, family, health, financial, admin, travel, shopping, soul, voice-samples. The personal counterpart to Rai's brain.

> Last updated: 2026-06-14.

## Philosophy

From `02-ana/CLAUDE.md`:

> Everything about John lives here: identity, family, health, finances, admin, travel, journal, todos, quotes, shopping, soul, voice-samples.

Plus the auto-load contract:

> `02-ana/identity/` is auto-loaded at session start.

Thirteen identity files load into every session. The rest of `02-ana/` is read on demand.

## Subfolder map

| Subfolder | Contents | Auto-loaded | Skill |
|-----------|----------|-------------|-------|
| `identity/` | Self-model + reference (13 files) | Yes | `/life telos` |
| `journal/` | Daily journal entries | No | `/routine journal` |
| `todos/today-plans/` | Today's priorities | No | `/routine today-prep` |
| `todos/tomorrow-plans/` | Tomorrow's priorities | No | `/routine tomorrow-prep` |
| `quotes/` | Captured quotes | No | `/life quote` |
| `soul/` | Reflective writing (own CLAUDE.md) | No | Manual or `/routine weekly-retro` |
| `family/` | People closest to John | No | Manual |
| `health/` | Overview, medications, recovery, specialists, supplements, quit-tracker | No | Manual |
| `financial/` | Assets, budget, debt-plan, bills, subscriptions, **investment/** | No | Manual + `/investment` |
| `admin/` | Documents, maintenance | No | Manual |
| `travel/` | Trips, bookings, bucket list | No | Manual |
| `shopping/` | Purchase plans | No | Manual |
| `voice-samples/` | Arabic voice anchor corpus | No | Read by `/writing arabic` |

The personal OS has 13 content subfolders (plus `02-ana/CLAUDE.md`). `voice-samples/` is the newest, seeded 2026-05; `financial/` now hosts a large `investment/` subtree (see "The investment subsystem" below).

## The identity/ folder — auto-loaded

Thirteen files. Every session loads them into context.

| File | Contents |
|------|----------|
| `who-i-am.md` | Self-definition. Who John is at the core. |
| `goals.md` | Current goals. Read by inbox triage and weekly planner. |
| `vision.md` | Long-term vision. The 5-10 year horizon. |
| `mindset.md` | Values and mindset. How John thinks. |
| `story.md` | Personal narrative. The arc up to now. |
| `wrong.md` | Things John believes are commonly misunderstood. Contrarian positions. |
| `projects.md` | Active and committed projects. |
| `ideas.md` | Top-ideas shortlist. Graduated ideas committed to pursuit. |
| `contacts.md` | Key relationships. People who matter. |
| `definitions.md` | Domain-specific definitions. How John uses words. |
| `environment.md` | Living and work environment. |
| `tech-stack.md` | Tools and technologies. What John uses. |
| `rai-public.md` | Public-persona source of truth for `https://johndoe.dev` (NEW). |

### rai-public.md — the public-facing identity

`rai-public.md` (added 2026-05) is the single source of truth for John's public persona on `https://johndoe.dev`. It is auto-loaded like the rest of `identity/`, but it is also the *input* to a publish pipeline:

- Edit `02-ana/identity/rai-public.md`.
- Run `npm run sync-persona` in the site repo.
- The script writes `src/lib/rai-persona.ts`, mapping each section header 1:1 to a TypeScript export (`RAI_NAME`, etc.).

The sync script **refuses to publish** if it detects any private marker: your name, family names, employer, any `$`+number, or your birth year/date. This is the public/private firewall in code — the rest of `02-ana/` never leaves the vault.

### How to add to identity

Drop a `.md` file in `02-ana/identity/`. Auto-loads next session. No code change.

### How to remove from identity

Move the `.md` file out of `02-ana/identity/`. The next session won't see it.

The `02-ana/identity/` folder is the "always-on context" mechanism. Everything in it shapes every session.

### What lives in `identity/` vs other 02-ana subfolders

The bar for `identity/`:
- It defines who John is, what he wants, or how he operates.
- It is true across most sessions, not session-specific.
- Rai needs it to make personalized decisions (rating an inbox item, planning a week, suggesting an idea).

Things that do NOT belong in `identity/`:
- A specific journal entry (goes to `journal/`).
- A todo for tomorrow (goes to `todos/tomorrow-plans/`).
- A quote (goes to `quotes/`).
- A health appointment note (goes to `health/`).

## journal/

Daily journal entries.

**Location:** `02-ana/journal/{YYYY-MM-DD}.md`

**Skill:** `/routine journal`

The skill prompts for one section (or several) and writes the entry. Style preference (from memory): "1-2 sentences per section, direct and honest (not flowery)."

### Common journal sections

- What happened today
- What I am thinking about
- What is bothering me
- What I am proud of
- What I want to do tomorrow
- Notes for future-me

These are not enforced. The journal is loose. The skill adapts.

## todos/today-plans/ and todos/tomorrow-plans/

Daily plans.

**Locations:**
- `02-ana/todos/today-plans/{YYYY-MM-DD}.md`
- `02-ana/todos/tomorrow-plans/{YYYY-MM-DD}.md`

**Skills:**
- `/routine today-prep` — Run in the morning. Reads goals, ongoing projects, yesterday's plan. Writes today's priorities.
- `/routine tomorrow-prep` — Run at end of day. Looks ahead. Writes tomorrow's priorities.

Style preference (from memory): "Day prep: Work priorities first, then personal."

### Why two plans?

- `today-plans/` is what John is doing now.
- `tomorrow-plans/` is what he is preparing for tomorrow.

When tomorrow becomes today, the previous tomorrow-plan is read by `/routine today-prep` and either rewritten or carried forward.

## quotes/

Captured quotes.

**Location:** `02-ana/quotes/{author or topic}.md`

**Skill:** `/life quote`

Use the Quote template (`12-system/templates/Quote.md`). The on-disk template is minimal: frontmatter is `captured:` + `tags: []` only (no `type:`, no `source:`, no author line), and the body is a single blockquote. The `/life quote` skill captures either an external quote or one of John's own aphorisms, filed by theme.

## soul/

Reflective long-form writing.

**Location:** `02-ana/soul/{topic or date}.md`

**Templates:**
- `12-system/templates/Soul Note.md` — short reflections.
- `12-system/templates/Personal Chapter.md` — long-form narrative.

**Skill:** Manual creation or `/routine weekly-retro` (which produces a soul-style weekly reflection).

`soul/` has its own CLAUDE.md. The folder is for writing that is more reflective than a journal entry — beliefs, worldview, life chapters, lessons internalized.

## voice-samples/ — the Arabic voice anchor corpus

**Location:** `02-ana/voice-samples/arabic/`

A reference corpus of Arabic writing that anchors Rai's Arabic voice. It is NOT auto-loaded — it is read on demand by `/writing arabic` when drafting serious Arabic prose.

The corpus is tiered (per the Arabic-voice memory):
- **Lumen = north star** (`formal--lumen-*` reference pieces — `example.com/articles` is the golden standard).
- **Secondary niche references:** columnist-a, columnist-b, columnist-c, columnist-d, plus a couple of informal samples.

Companion files `CORPUS.md` and `README.md` describe the tiers and provenance. This corpus is the data layer behind the `/writing arabic` voice-matching rules.

## family/, health/, admin/, travel/, shopping/

These subfolders are loose. They hold whatever John writes about them.

**No skill automation.** Manual writing.

**Convention:**
- One file per subject (not one file per day).
- Frontmatter optional.
- Update in place; do not create a new file every time.

### Examples

```
family/sam.md            ← notes about Sam
family/jane.md            ← notes about Jane
family/zoe.md          ← notes about Zoe
family/shared.md          ← household scratchpad
family/calendar.md        ← family calendar
health/medications.md     ← current medications
health/recovery-plan.md   ← if recovering from anything
health/quit-tracker.md    ← nicotine cold-turkey logs
admin/documents.md        ← important docs (passport, license, etc.)
travel/bucket-list.md     ← places to go
travel/log.md             ← trip log
shopping/mini-pc-plan.md  ← desktop replacement plan
shopping/monitor-plan.md  ← monitor selection (BenQ MA270S)
```

The `financial/` subfolder is no longer "loose" — it has its own structure (split bills/subscriptions docs) and a large automated subsystem. See the two sections below.

## financial/ — bills, subscriptions, and the split

`02-ana/financial/` holds the money layer: `assets.md`, `budget.md`, `cash-flow.md`, `debt-plan.md`, `plan.md`, `review-calendar.md`, `transactions.md`, `reviews/`, and the two files split out of `budget.md`:

| File | Holds |
|------|-------|
| `bills.md` | Fixed monthly bills paid TO providers (utilities, telecom, household). |
| `subscriptions.md` | Recurring services (Claude, Gemini, X Premium, etc.) on a card. |

The **bills vs subscriptions split** is deliberate: `bills.md` is fixed bills to providers; `subscriptions.md` is services. They are paid and tracked differently.

- `bills.md` totals your fixed monthly bills paid to providers (utilities, telecom, household help).
- `subscriptions.md` tracks recurring services (your AI assistants, X Premium that powers `/news-digest`, etc.) on a chosen card.

`plan.md` is the steady-state cash-flow model: income in (salary plus any other sources), fixed bills, savings, and an operating cap out. If you carry high-interest debt, this is the context the `/investment` skill's debt-first posture defers to.

## The investment subsystem — `02-ana/financial/investment/`

An optional, self-contained subsystem operated entirely by the `/investment` skill group. It is a **paper-trading practice ground** — a knowledge base, strategy docs, screening rules, and optional cloud-bot config — living under `02-ana/financial/investment/`. This deliberately overrides the usual "code goes in `~/projects/`" rule, because it is an extension of your financial life, not a standalone project. Secrets never enter the vault: live keys live only on the host's gitignored `.env`; the in-vault config stays dry-run and key-less.

The design principles are generic and worth keeping whatever your approach:

- **Capital preservation first; the system says NO by default.** The Restraint Gate (`/investment convene`) runs a proposed decision through a panel of investor lenses whose default verdict is DO NOTHING, plus a fixed buy funnel (timing → your hard-rule screen → edge honesty → portfolio fit → your explicit sign-off). Any single NO rejects.
- **Rule-based screening you define.** Screen candidates against your own ruleset (e.g. values-based / Sharia-compliant, ESG, or sector exclusions) before anything enters the book, and keep a screening log.
- **Paper before real.** Everything runs dry-run/paper first; deploying real money is always an explicit, eyes-open decision. If you carry high-interest debt, paying it down is the guaranteed return that comes first.
- **Optional cloud bot.** A self-hosted paper-trading bot (e.g. Freqtrade in DRY-RUN on a small cloud host) plus a per-stream equity paper-portfolio can run your strategies on a cron. Replace the host, key, and tickers with your own — or skip it entirely.
- **Honesty ledger.** A `strategy-graveyard.md` records what was tried and killed, with the real numbers. Killing a losing strategy in the open is the point.

Populate the subtree with your own strategy, rules, and watchlist; the `/investment` sub-skills (`status`, `recommend`, `screen`, `review`, `ops`, `convene`) operate on whatever you put there.

## The /life, /routine, and /investment skill groups

```
/life                          /routine                       /investment
├── telos  ← self-model        ├── journal       ← daily      ├── status     ← where do I stand
└── quote  ← wisdom capture    ├── today-prep    ← morning    ├── recommend  ← ranked next actions
                               ├── tomorrow-prep ← evening     ├── screen     ← a screening standard rules-screen
                               ├── weekly-retro  ← weekly      ├── review     ← periodic portfolio review
                               └── bills         ← MONTHLY     ├── ops        ← operate the cloud bot
                                                               └── convene    ← run The Restraint Gate
```

All three read/write `02-ana/`. `/life` holds the slow-moving self-model and wisdom; `/routine` holds the daily/weekly/**monthly** cadence; `/investment` operates the investment subsystem. The daily/weekly/monthly cadence used to live in `/life` — it was split out into `/routine`, so `/life` now holds only `telos` + `quote`.

### /life telos

Updates the self-model. Specifically the four pillar files:
- `identity/goals.md`
- `identity/vision.md`
- `identity/mindset.md`
- `identity/who-i-am.md`

Run when John's self-understanding evolves — usually monthly or quarterly.

### /routine weekly-retro

Saturday ritual. Reads:
- The week's journal entries.
- The week's today-plans.
- This week's `04-work/work-plans/{YYYY-WNN}.md` (if it exists).
- Recent ratings.

Produces:
- A retrospective in `02-ana/soul/` (or `02-ana/journal/` — depends on style).
- Highlights, struggles, lessons, focus for next week.

### /routine bills — the monthly bill-pay run (NEW)

The monthly cadence sub-skill, added 2026-05-16. It runs when salary lands (~26-27th) and pays every recurring bill in one sitting.

- Opens the provider portals via `open`: `electricity.example.com` (electricity), `water.example.com` (water), `internet.example.com` (internet), `phone.example.com` (both phone lines from one login).
- Surfaces the non-portal bills (e.g. household help) for manual payment.
- Reads and updates the `## Monthly tracker` in `02-ana/financial/bills.md`.
- Flags any bill more than 20% above its running average.

### /investment status

The read-only "where do I stand?" entry point. Reports strategy posture, both cloud paper engines (crypto bot + the 4-stream equity portfolio), any real holdings, the tuition sleeve (0/500), and the standing debt reminder. the current phase aware: it keeps pointing at the cards before any deployment. Use the other five sub-skills for action: `recommend` (ranked next moves), `screen` (rules-screen a ticker/coin), `review` (periodic portfolio review + one falsifiable challenger), `ops` (operate the cloud bot — status/logs/restart/deploy/go-live gate), `convene` (run The Restraint Gate council on a decision).

## Reading patterns by skill

| Skill | Reads |
|-------|-------|
| `/routine journal` | Yesterday's journal entry (for continuity) |
| `/routine today-prep` | `02-ana/identity/goals.md`, `02-ana/identity/projects.md`, yesterday's plan, tomorrow-plan from yesterday |
| `/routine tomorrow-prep` | Today's plan, calendar (if integrated), open tasks |
| `/routine bills` | `02-ana/financial/bills.md` (the monthly tracker) |
| `/life telos` | Current `identity/{goals,vision,mindset,who-i-am}.md` |
| `/life quote` | (Optional: existing quote files for de-duplication) |
| `/routine weekly-retro` | The full week's journal + plans + work-plan |
| `/investment status` | `02-ana/financial/investment/` strategy + cloud paper state + `financial/plan.md` debt math |
| `/writing arabic` | `02-ana/voice-samples/arabic/` (voice anchors) |
| `/work weekly-planner` | `02-ana/identity/goals.md`, last week's `04-work/work-plans/`, open project files |
| `/triage process-inbox` | `02-ana/identity/goals.md`, `02-ana/identity/who-i-am.md` |

## The two ideas repos

This is important. The vault has two places where ideas live:

| Location | Role |
|----------|------|
| `09-ideas/` | Nursery — every idea, all states, all domains. Includes rejected and abandoned. |
| `02-ana/identity/ideas.md` | Top-ideas shortlist — graduated ideas committed to pursuit. Auto-loaded into every session. |

A graduated idea in `09-ideas/` does NOT automatically appear in `02-ana/identity/ideas.md`. It only gets there when John explicitly commits to pursuing it. That commitment is what makes it identity-level (always-on context for Rai).

## Rules (verbatim from 02-ana/CLAUDE.md)

> Write in English. Never Arabic.

> One source of truth per fact — update in place, don't duplicate.

> Before creating a new file, check if it fits in an existing one.

The third rule is especially important. The personal OS degrades fast if every observation becomes a new file. Most updates should append to or edit an existing file.

(Note: the "write in English" rule governs `02-ana/` prose. The `voice-samples/arabic/` corpus is the deliberate exception — it is Arabic reference material, not John's own notes, read by `/writing arabic`.)

## Cross-references

- The full identity auto-load contract: [02-architecture.md](./02-architecture.md)
- How `/routine today-prep` reads goals.md: [01-folder-map.md](./01-folder-map.md)
- How inbox triage personalizes via `02-ana/identity/`: [04-capture-pipeline.md](./04-capture-pipeline.md)
- How weekly-planner uses `02-ana/identity/goals.md`: [14-work-and-projects.md](./14-work-and-projects.md)
- Full skills inventory (including `/investment`, `/routine`, `/writing`): [07-skills-catalog.md](./07-skills-catalog.md)

## Cadence

| Cadence | Action |
|---------|--------|
| Daily | `/routine today-prep` morning, `/routine journal` end of day, `/routine tomorrow-prep` last action |
| Daily as-needed | `/life quote` when a quote lands; `/investment status` to check posture |
| Weekly (Saturday) | `/routine weekly-retro`; `/investment review` (periodic) |
| Monthly (salary day ~26-27th) | `/routine bills` to pay all recurring bills; `/investment review` (monthly) |
| Monthly or quarterly | `/life telos` if the self-model evolved; `/investment screen` re-screen of the universe |
| As-needed | Manual writes to `family/`, `health/`, `travel/`, etc.; `/investment convene` on a real decision |

## Why the personal OS lives in the same vault

The vault could have been split: knowledge and skills in one repo, personal data in another. It is not split because:

- The auto-load contract requires `02-ana/identity/` to be co-located (same machine, same file system).
- Skills like `/triage process-inbox` need read access to `02-ana/identity/goals.md` for personalization.
- The `/life`, `/routine`, and `/investment` skill groups need unified access to `02-ana/`.
- One repo means one git history, one backup story, one search surface.

The trade-off: the vault contains personal data (and now financial-strategy detail) that should never be shared externally without confidentiality care.

## Confidentiality

- The vault is private. Do not share `02-ana/` content in any external context.
- `02-ana/identity/rai-public.md` is the ONE exception — but only its sanctioned sections, published through `npm run sync-persona`, which refuses to emit private markers (family names, employer, "Acme Corp", dollar figures, birth date).
- The `04-work/` folder also has a confidentiality rule (no AI mentions in any output that lands there — see [14-work-and-projects.md](./14-work-and-projects.md)).
- `.pai-protected.json` includes local entity name patterns and identity markers — those are scrubbed from any output.
- Investment secrets never enter the vault: live API keys live only on the cloud droplet's gitignored `.env`; the in-vault `config.json` is dry-run and key-less.
- When publishing snippets from the vault (e.g., a blog post about the brain), redact `02-ana/` entirely except the published `rai-public.md` sections.

## What the personal OS does NOT contain

- Code (lives in `~/projects/`) — with ONE deliberate exception: the investment bot code lives under `02-ana/financial/investment/02-crypto/spot-bot/`, because it is part of John's financial life.
- Project planning (lives in `05-projects/kitchen/`, `active/`, `completed/`).
- Algorithm task PRDs (live in `03-rai/memory/work/{slug}/`).
- News digest (lives in `08-bawaba/`).
- Knowledge notes (live in `10-knowledge/`).
- Skill or agent definitions (live in `03-rai/`).

The personal OS is the *life* layer. Everything else is operational. The live source of truth for every fact here is the relevant CLAUDE.md (`02-ana/CLAUDE.md` and `02-ana/financial/investment/CLAUDE.md`); this chapter is a snapshot.
