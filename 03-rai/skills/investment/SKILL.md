---
name: investment
description: >
  Investment router. USE WHEN John wants the status of his investments / the cloud
  trading bot, a recommendation on what to do (DCA, rebalance, opportunities), a Sharia
  screen on a ticker or coin, a periodic portfolio review, or to operate the cloud bot.
  Strictly Sharia-compliant (spot, no leverage), debt-payoff-phase aware (debt-first),
  cloud-only runtime. Strategy + branches live in `~/helm/02-ana/financial/investment/`.
---

# Investment

John's investing command center. Strictly Sharia-compliant, debt-first during the debt-payoff phase, cloud-only runtime. The master plan is `~/helm/02-ana/financial/investment/strategy.md`; rules are in that folder's `CLAUDE.md`.

## Routing table

| Task | Sub-skill | File to Read |
|------|-----------|--------------|
| "Where do I stand?" — portfolio + cloud-bot snapshot | status | `status.md` |
| "What should I do?" — actions, DCA targets, rebalancing | recommend | `recommend.md` |
| "Is X rule-compliant to invest in?" — AAOIFI screen of a ticker/coin | screen | `screen.md` |
| Weekly/monthly portfolio + bot review | review | `review.md` |
| Operate the cloud bot — logs, restart, tunnel, go-live gate | ops | `ops.md` |
| Run the council's Restraint Gate on a decision (buy/sell, strategy change, reweight, new candidate) | convene | `convene.md` |

## How to use

1. Pick the sub-skill by task.
2. `Read` the matching file in this directory.
3. Follow its instructions — and always honor the guardrails: **Sharia-compliant (spot/no-leverage), debt-first, paper-first.** Real money never exceeds the learning allocation without an explicit, eyes-open go-live (see `strategy.md` + the bot's `GO-LIVE-CHECKLIST.md`).
