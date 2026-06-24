---
name: status
description: Read-only snapshot — "where do I stand?". Strategy posture + both cloud paper engines (crypto bot + equity paper-portfolio) + real holdings + learning-allocation usage, closing with the debt-first reminder
allowed-tools: Read, Bash
---

# Investment Status

A tight, one-screen snapshot. **Read-only** — this skill observes; it never trades, restarts, runs the simulator, or flips anything to real money. Answers "where do I stand?" across strategy posture, the two cloud paper engines, and real holdings.

## Instructions

### Step 1: Strategy posture

Read `~/helm/02-ana/financial/investment/strategy.md` for the **target allocation** and the **current-phase posture** (debt-payoff → a target date: debt-first, real money capped to a a small capped learning allocation, paper-first). That's the yardstick for everything below.

### Step 2: Probe both cloud engines (read-only — ONE bash block)

Run this as a single block. The `s()` helper avoids shell-quoting/word-split issues (don't use a bare `$VAR` for the ssh command — it breaks under zsh). Do NOT run `simulator.py` or restart anything here — that has side effects.

```bash
s(){ ssh -i ~/.ssh/spot-bot -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=15 root@203.0.113.10 "$@"; }

echo "== crypto bot (spot-bot) =="
s "docker inspect spot-bot --format 'Running={{.State.Running}} Restarts={{.RestartCount}}'"
PW=$(s "grep -m1 '\"password\"' /opt/spot-bot/user_data/config.json | sed -E 's/.*: *\"([^\"]*)\".*/\1/'")
for ep in count profit balance; do echo "-- /$ep --"; s "curl -s -u freqtrader:'$PW' http://127.0.0.1:8080/api/v1/$ep"; echo; done

echo "== per-stream portfolio (etf / the local exchange / us_stocks / sukuk) =="
s "cat /opt/paper-portfolio/portfolio_state.json"

echo "== profit->gold skim (ring-fenced account) =="
s "cd /opt/paper-portfolio && ./venv/bin/python gold_skim.py --status"
```

If SSH or an API call fails, say "engine unreachable" plainly — don't guess.

### Step 3: Summarize the crypto bot (3–4 lines)

- **Running?** `Running=true` + restart count (climbing = crash-loop → flag it).
- **Dry-run guard** — confirm it's still paper. If anything hints at real money, STOP and flag loudly.
- **Open trades** (`/count`), **dry-run PnL + simulated balance** (`/profit`, `/balance`).

### Step 4: Summarize the per-stream portfolio

From `portfolio_state.json` — **four equity stream books, each started with a small seed**, each running a trend-following algorithm on its own names. For each stream (`etf`, `the local exchange`, `us_stocks`, `sukuk`):
- Latest `nav_history[].nav_value`, **P/L vs 1,000**, and which tickers it currently **holds**.
- Trend-following moves below-trend names to **cash**, so a stream may hold fewer than its full list (or sit in cash) — that's the algorithm working, not a bug.
- `sukuk` is a modeled hold (~4.5%/yr), no tickers.
- Sum the four = total equity paper (~4,000 USD at start). Crypto is separate (the bot above, ~1,000 USD); gold is manual.

### Step 4b: Profit→gold skim (ring-fenced investment account)

The separate, **ring-fenced** account (debt is OUT of scope here, per your own decision — see [[gold-buffer-sweep]]): 100% of each contribution DCA's into a diversified Sharia core (a diversified mix you define); each up-month, **3% of profit ABOVE the high-water mark** is skimmed into gold, **0 in any down month**. From the `gold_skim.py --status` line, report in 2–3 lines:
- Latest month + **core value** and **contributions to date**.
- **This month's skim** — or "skim 0", which in a down/below-peak month is the *no-sell-into-a-drawdown rail working*, not a fault.
- **Gold pile** (cost / value) and the **growth drag** so far.
- Gold lives in the **your gold custodian**; the core runs at the another venue (**your broker** pending auto-recurring confirmation, else **your broker**). Paper until 2 clean months pass; real money is John's eyes-open call. This account is governed *separately* from the debt-first debt-payoff posture in Step 6.

### Step 5: Real holdings + learning allocation

- **Real holdings** — look for `~/helm/02-ana/financial/investment/holdings.md`. If absent: **"No holdings note — none deployed, paper only."**
- **learning allocation** — real money vs a small cap cap (paper-only = 0 / 500 used).
- **Gold** — note it's manual (your own manual holding), not tracked by either engine.

### Step 6: Close with the debt math (ALWAYS)

> Debt-first: the high-interest cards bleed a high APR — paying them is a **guaranteed** return no branch here beats. Real money stays capped to a small capped learning allocation until the debt is down. Both engines stay **paper/dry-run** — never go real without an explicit eyes-open confirmation + the bot's `GO-LIVE-CHECKLIST.md`.

## Rules

- **Read-only.** No restarts, no orders, no config edits, no running `simulator.py` (it DCAs/writes). For operating, that's `ops.md`.
- **Never echo the freqUI password** — fetch at runtime, use, don't print.
- One screen. Snapshot, not a report. If something can't be confirmed, say so — don't invent numbers.
