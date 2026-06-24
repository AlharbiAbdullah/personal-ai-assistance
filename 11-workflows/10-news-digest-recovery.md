# News Digest Recovery

**Triggered by:** "news didn't fire" / "digest is placeholders" / "no news today"
**Cadence:** Ad-hoc — when the 03:00 UTC Ubuntu run failed or shipped a partial/placeholder digest.
**Done when:** a real, complete digest for the date exists in `08-bawaba/daily/{date}.md` AND the root cause is fixed-forward so the next scheduled run succeeds.

The news spine runs unattended on the Ubuntu coordinator. When it misses or ships
placeholders, this playbook is the triage order + the hard-rule gate — the actual
collection is the `/news-digest` skill. This runs on Ubuntu; from the Mac, drive it
over Tailscale SSH.

```
Triage unit → Identify failed source → Manual recovery run → HARD-RULE gate → Verify real → Fix-forward → Coordinator commits
```

> **Hard-rule frame (non-negotiable):** X is REQUIRED — no X, abort, never ship
> without it. All 6 sources are mandatory; the AI does not decide to skip. Fully
> autonomous (zero prompts). Retry up to 10 attempts: Chrome → fresh Chrome →
> Playwright. These override every other consideration.

---

## Steps

### 1. Triage — timer, run, or source?

- [ ] All work happens on the coordinator. From the Mac, reach Ubuntu over keyless
      **Tailscale SSH** (`pc`). Never run the collection locally on the Mac.
- [ ] Run **`/ubuntu → diagnostics`** to inspect the unit:
      `systemctl --user status news-daily.timer` (did it fire?),
      `journalctl --user -u news-daily` (did the run start / how did it exit?).
- [ ] Read the run logs in `~/.local/state/news-digest/logs/` for the date.

> **Decision Point**: where did it break?
> - **Timer never fired** (inactive/masked, missing graphical session) → unit problem, jump to step 6 after the recovery run.
> - **Run started but exited non-zero** → a source failed → step 2.
> - **Run "succeeded" but digest is placeholders** → silent source failure → step 2.

### 2. Identify the failed source

- [ ] The 6 mandatory sources: **HN, Reddit, X, Substack, Medium, GitHub Trending**.
- [ ] From the logs, find which source(s) returned empty or errored. Common culprits:
      X tab state / login, Reddit JSON 403 (needs RSS), background-tab scroll freeze.

> **Decision Point**: was **X** the failure?
> - X failed → the whole run is invalid. Do not patch around it. Fix X access, then re-run.
> - A non-X source failed → still mandatory; recovery must collect all 6, not 5.

### 3. Manual recovery run

- [ ] Re-run the scheduled runner with the recovery flag:
      `RECOVERY=1 03-rai/skills/news-digest/scheduled/run-news-ubuntu.sh daily`.
- [ ] Or, for full manual control, invoke **`/news-digest`** directly (day mode) on Ubuntu.
- [ ] Keep the scraping tab the sole/active tab — background tabs freeze scroll drivers.

### 4. HARD-RULE gate (the one that bites)

- [ ] **X present?** No X → ABORT the run. Never ship a digest without X.
- [ ] **All 6 sources collected?** Missing one → not done. The AI does not skip sources.
- [ ] **Fully autonomous?** Zero permission prompts during collection.
- [ ] **Retries exhausted properly?** Up to 10 attempts per source: Chrome → fresh
      Chrome → Playwright. Only after 10 real attempts is a source declared dead.

### 5. Verify the digest is genuinely real

- [ ] Open `08-bawaba/daily/{date}.md`. Confirm it is **populated, not placeholder** —
      no empty sections, no "TODO"/scaffold text, gems in feed style with real items.
- [ ] Spot-check that For You covers the full identity (max 2 items per topic) and that
      X content is present and text-only.

> **Decision Point**: still placeholders or thin after recovery?
> - Yes → a source is still failing silently → back to step 2; do not accept a partial.
> - No, real + complete → done with collection; proceed to fix-forward.

### 6. Fix-forward the root cause

- [ ] If the break was the **systemd unit/env** (timer not firing, missing PATH/python
      deps, no graphical session), fix the unit forward via **`/ubuntu → diagnostics`**
      so the NEXT 03:00 UTC scheduled run succeeds unattended.
- [ ] `requests` missing on system python 3.9? `pip install --user requests`.
- [ ] Archiving of the prior digest to `13-archive/news/` is handled by the news skill — no manual move.

### 7. Sync (leave for the coordinator)

- [ ] The digest is written + **committed by the coordinator's** maintenance run
      (04/10/16/22:00 UTC) — not from the Mac. Vault edits stay **local**.
- [ ] **Do not `git push` from the Mac** — single-writer rule, `03-rai/SYNC-ARCHITECTURE.md`.

---

## Gating facts (verified, sourced)

| Fact | Value | Source |
|------|-------|--------|
| Daily timer | 03:00 UTC | `news-daily.timer` |
| Weekly timer | Sat 07:00 | `news-weekly.timer` |
| Runner | `run-news-ubuntu.sh [daily\|weekly]`, env `RECOVERY=1` | `03-rai/skills/news-digest/scheduled/` |
| Logs | `~/.local/state/news-digest/logs/` | live |
| Output | `08-bawaba/daily/{date}.md` | live |
| Mandatory sources | HN, Reddit, X, Substack, Medium, GitHub Trending | hard rule |
| X | required — no X, abort | hard rule |
| Retries | 10 attempts: Chrome → fresh Chrome → Playwright | hard rule |

---

## Connections

- Collection engine: `/news-digest`
- Unit / timer / env diagnostics: `/ubuntu → diagnostics`
- Generic system triage: [[04-debugging]]
- Single-writer sync: `03-rai/SYNC-ARCHITECTURE.md`
