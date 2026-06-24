---
name: review
description: Periodic (weekly/monthly) investment review + improvement loop — bot performance, risk check, paper-journal lessons, allocation drift, debt-math, and ONE falsifiable challenger change to test on paper. USE WHEN John wants a portfolio/bot review.
allowed-tools: Read, Bash
---

# Investment Review

The reflection loop. Pull the cloud-bot's numbers, grade the paper journal, check allocation drift against the target, restate the debt-math, and propose exactly ONE falsifiable change to test on a paper challenger. Output a dated review note John can save under `reviews/`. This skill never deploys anything to the live bot.

**Guardrails (non-negotiable):** debt-first honesty · paper-first · Sharia-compliant (spot, no leverage/options/futures/shorts/riba) · NEVER flip `dry_run=false`. The review *proposes* a challenger; it does not promote one.

## Instructions

### Step 1: Pull bot performance (cloud, dry-run)

The bot is Freqtrade dry-run on the DigitalOcean droplet. Fetch the freqUI password at runtime — NEVER hardcode it.

```bash
SSH="ssh -i ~/.ssh/spot-bot -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@203.0.113.10"

# Confirm the container is up (restart: unless-stopped)
$SSH "docker ps --filter name=spot-bot --format '{{.Names}} {{.Status}}'"

# Fetch the REST password from the droplet config (never store it in the vault)
PW=$($SSH "grep -A4 api_server /opt/spot-bot/user_data/config.json | grep -o '\"password\": *\"[^\"]*\"' | head -1 | sed 's/.*: *\"\\(.*\\)\"/\\1/'")

# Query the REST API on the droplet's loopback through the same SSH session
$SSH "curl -s -u freqtrader:'$PW' http://127.0.0.1:8080/api/v1/profit"      # cumulative P&L, win rate, best/worst
$SSH "curl -s -u freqtrader:'$PW' http://127.0.0.1:8080/api/v1/balance"     # dry-run wallet
$SSH "curl -s -u freqtrader:'$PW' http://127.0.0.1:8080/api/v1/performance" # per-pair performance
$SSH "curl -s -u freqtrader:'$PW' http://127.0.0.1:8080/api/v1/status"      # open trades
```

Pipe each through `python3 -m json.tool` if you need it readable. Record: total profit %, win rate, trade count, best/worst pair, and the peak-to-current drawdown for the period under review (week or month — ask if unclear). This is **dry-run / paper**; numbers are tuition, not money.

### Step 2: Risk check — the 20% drawdown trip-wire

If the active/satellite sleeve (the bot or any paper conviction picks) is **down ~20% from its peak**, the rule fires: **recommend pulling that strategy back to fresh paper** and re-qualifying it before any further size. State it plainly — drawdown is the signal the rules (or the discipline) broke, per [[risk-management]]. Never rationalize past 20%.

### Step 3: Review the paper-trading journal — by regime

Read `~/helm/02-ana/financial/investment/08-practice/paper-trading-journal.md`. Grade the *decisions*, not the P&L:

- **What worked, by regime** — group trades by market condition (BTC bull leg / chop / down). Which setups actually paid in which regime?
- **Repeated mistakes** — the same losing trade 3+ times is the edge bleeding out. Name it.
- **Emotion column** — flag high-emotion trades (≥7); if the "I'm sure" trades keep losing, the enemy is discipline, not the market.
- **Skips logged** — a logged FOMO-skip is a win; count them.

### Step 4: Allocation drift vs the target

Read `~/helm/02-ana/financial/investment/strategy.md`. in the debt-payoff phase the live target is **~0 real money beyond a small capped learning allocation**, so most "drift" is on paper / in the plan. Still, compare any real holdings (gold ~6K, learning allocation) against the architecture and flag:

- Satellite sleeve over its **≤25% hard cap** → flag for rebalance.
- Real money beyond the learning allocation → guardrail violation, call it out.
- If a holdings note doesn't exist, **say so plainly** — there's no brokerage API; holdings are tracked manually.

Note: real rebalancing belongs to the Freedom-Fund era (a later date). For now, "rebalance" usually means *adjust the paper plan*, not move money.

### Step 5: Restate the debt-math

Every review restates it, no exceptions: the **high-interest cards cost a high APR** — a guaranteed return no branch in `strategy.md` beats. Through the debt-payoff phase (→ a target date), paying them down is the highest-return "investment" available. Real deployment defers to the Freedom-Fund era. If the bot's annualized paper return is below a high rate, say it: paper is for learning, the cards are the real trade.

### Step 6: Champion / challenger — propose ONE falsifiable change

Discipline: the live bot config is the **champion**. Propose exactly **ONE** concrete, falsifiable change to test on a **paper challenger** — never edit the live bot here.

- One variable only (e.g., "tighten `h4_rsi` entry gate from <50 to <40").
- **Falsifiable success criterion** stated up front (e.g., "over 30 days of paper, challenger must beat champion win-rate by ≥5pp at equal-or-lower drawdown — else discard").
- The deploy path is a *separate* dry-run instance/config that John reviews; promotion to the live bot happens only via `/investment ops` with the eyes-open go-live gate (`GO-LIVE-CHECKLIST.md`), never here.

### Step 7: Write the dated review note

```bash
mkdir -p ~/helm/02-ana/financial/investment/08-practice/reviews
date +%F   # the review date
```

Write to `~/helm/02-ana/financial/investment/08-practice/reviews/{YYYY-MM-DD}-review.md`. Match the folder's house style — **no YAML frontmatter**, `# h1` + `>` summary + `**Last updated:**`, tables for numbers, `## Related` wiki-links at the end:

```markdown
# Investment Review — {YYYY-MM-DD} ({weekly|monthly})

> {one-line verdict: is the loop healthy, and what's the single thing to change?}

**Last updated:** {YYYY-MM-DD}

## Bot performance (dry-run)
{profit %, win rate, trades, best/worst pair, peak→current drawdown}

## Risk check
{20% trip-wire: clear, or fired → back to paper}

## Paper journal — by regime
{what worked where · repeated mistakes · emotion flags · skips logged}

## Allocation vs target
{drift, satellite-cap check, guardrail violations — or "no real holdings note; tracked manually"}

## Debt-math
high-interest cards @ a high APR = the guaranteed return that beats every branch. the debt-payoff phase → a target date. {bot annualized vsa high rate}

## Challenger proposal (paper only)
- Change: {one variable}
- Hypothesis: {what improves and why}
- Success criterion (falsifiable): {metric + threshold + window}
- Deploy: paper challenger only — NOT the live bot.

## Related
- [[strategy]] · [[risk-management]] · [[paper-trading-journal]] · [[debt-plan]] · [[order-of-operations]]
```

## Rules

- **Never** flip `dry_run=false` or edit the live bot config. This skill reviews and proposes; promotion runs through `/investment ops` + `GO-LIVE-CHECKLIST.md` with explicit eyes-open confirmation.
- **One challenger per review.** More than one change = you can't tell which one worked.
- Fetch the freqUI password at runtime via SSH grep. Never write it into the note or this file.
- Honest and grounded: if the bot is losing or a guardrail is breached, say it first, not last. Debt before deployment, always.
