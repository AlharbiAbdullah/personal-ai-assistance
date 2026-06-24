---
name: recommend
description: Give concrete, ranked next investing actions inside the constraints. USE WHEN John asks "what should I do" — DCA, rebalance, what to screen, what the bot should watch, or go-live readiness.
allowed-tools: Read, Bash, WebSearch
---

# Investment Recommend

Hand John a short, ranked list of next actions — never an essay. Every line is rule-compliant (spot only), debt-first, and paper-first by construction. the debt-payoff phase runs to a target date: the high-interest cards @ a high APR are a guaranteed return no branch beats, so deploying real capital before they are gone is almost always the wrong move.

## Instructions

### Step 1: Load the target

Read the master strategy for the branch list and target allocation:

```bash
cat ~/helm/02-ana/financial/investment/strategy.md
```

Read the relevant branch doc only if a recommendation needs its detail (e.g. `order-of-operations.md` for sequencing, `risk-management.md` for position-sizing, `sharia-screening.md` for the 3 ratios). Check for a holdings note (e.g. `~/helm/02-ana/financial/investment/08-practice/holdings.md`). If none exists, say so plainly — do not invent positions.

### Step 2: Optional — pull live status

If the ask is "what now" rather than a pure plan question, glance at the bot before recommending. Confirm it is still DRY-RUN, then summarize.

```bash
SSH="ssh -i ~/.ssh/spot-bot -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@203.0.113.10"
$SSH "docker ps --filter name=spot-bot --format '{{.Names}} {{.Status}}'"
$SSH "grep -m1 dry_run /opt/spot-bot/user_data/config.json"
# REST API password lives in the config — fetch at runtime, never hardcode it
PW=$($SSH "grep -m1 -oE '\"password\"[^,]*' /opt/spot-bot/user_data/config.json")
$SSH "curl -s -u freqtrader:\${PW##*: } http://127.0.0.1:8080/api/v1/profit" 2>/dev/null
```

If `dry_run` is anything but `true`, STOP and flag it loudly before any other recommendation.

### Step 3: Lead with the honest #1 move (the debt-payoff phase)

The top of every list, until the cards are cleared, is some flavor of:

1. **Kill the high-interest cards / hold the emergency-fund line before deploying real capital.** Frame the guaranteed a high APR return vs. any market expectation. No branch here beats it.

Only soften this if John has explicitly told you the debt is handled or asks you to assume a post-debt-payoff world.

### Step 4: Paper / learning actions

The actionable middle of the list. Pick the 2–4 highest-leverage of:

- **DCA on paper** toward the draft target allocation in `strategy.md` — name the under-weight sleeve(s) and the instrument (ETF / the local exchange name / sukuk / gold), as a *paper* entry, not a buy.
- **Sharia-screen a candidate** before it ever enters the paper book. Prefer the `halalterminal-claude-skills` plugin (`/rule-compliant-setup` for a free key) for an AAOIFI verdict; else compute the 3 ratios from SEC EDGAR / FMP per `sharia-screening.md`. End every verdict with: *"not professional advice — confirm with a qualified advisor."*
- **What the bot should be watched for** this week — a pair behaving oddly, drawdown creeping, a strategy assumption to validate against the dry-run trades.

### Step 5: Real-money actions (only if real money exists)

Skip this block entirely if the holdings note is empty or a small capped learning allocation is untouched. If real positions exist:

- **Rebalance** toward target only when a sleeve drifts past its band (see `risk-management.md`) — name the trim/add, spot only.
- **Position-size** any new real entry against a small learning cap (fully losable). Never size into a position that the cards'a high rate would out-earn.

### Step 6: Go-live readiness (only if asked)

If John asks about flipping the bot to real money, do NOT change `dry_run`. Point him at the checklist and require an explicit, eyes-open confirmation:

```bash
cat /opt/spot-bot/GO-LIVE-CHECKLIST.md 2>/dev/null || \
  echo "No GO-LIVE-CHECKLIST.md on the droplet — going live is blocked until it exists."
```

State plainly: real money stays off until the checklist passes AND he confirms in full knowledge.

### Step 7: Output

A ranked list, newest constraint at the top:

```markdown
## Recommendations — {date}
1. {Debt-first #1 move — guaranteed-return framing}
2. {Highest-leverage paper/learning action}
3. {Next paper action / screen candidate}
4. {Bot watch item or real-money rebalance, if applicable}
```

Keep it to 3–5 lines. No essay.

## Rules

- rule-compliant by construction: spot only, no options / futures / leverage / shorts / riba. Never recommend an excluded instrument.
- Debt-first: until the high-interest cards are cleared, #1 is always the cards / emergency fund, not the market.
- Paper-first: real money is capped to a small capped learning allocation. Default every "buy" to a paper entry.
- NEVER flip the bot to real money (`dry_run=false`) — that needs an explicit eyes-open confirmation AND a passing `GO-LIVE-CHECKLIST.md`.
- Fetch the freqtrade REST password at runtime via ssh; never hardcode it here.
- No holdings note = say so. Do not fabricate positions or numbers.
- Every Sharia verdict ends with: "not professional advice — confirm with a qualified advisor."
