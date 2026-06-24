---
name: bills
description: Monthly bill-pay run. Opens every bill-pay portal in browser tabs so all recurring bills can be paid in one sitting. Also surfaces non-portal bills (household help, a household helper) as reminders.
allowed-tools: Bash, Read
---

# Bills

Monthly cadence. Run when salary lands (~26-27th) or whenever bills are due. Opens every customer portal at once, then walks John through `bills.md` to tick each one off.

## Instructions

### Step 1: Read the manifest

Read `~/helm/02-ana/financial/bills.md` for the current state — amounts, account numbers, which lines are on autopay, the current month's tracker.

If the current month's tracker block doesn't exist yet, **append a fresh dated block** to `bills.md` under `## Monthly tracker`:

```markdown
### {{YYYY-MM}} ({{Month name}})

- [ ] SE (electricity) — _amount_
- [ ] NWC (water) — _amount_
- [ ] Zain (internet) — _amount_
- [ ] STC — John phone — _amount_
- [ ] STC — Jane phone — _amount_
- [ ] Maid salary — 1,000
- [ ] a household helper — 100
- [ ] (digital subs auto-debit — no action)
```

### Step 2: Open all bill-pay portals

Run via Bash (macOS default browser is Chrome):

```bash
open "https://www.se.com.sa/en/login/"
open "https://ebranch.nwc.com.sa/"
open "https://app.sa.zain.com/en/dashboard"
open "https://my.stc/"
```

That opens four tabs. STC's `my.stc` portal covers both John's and Jane's lines from the same login.

If any portal has migrated, fall back to the alternates:

| Provider | Primary URL | Fallback |
|----------|-------------|----------|
| SE (electricity) | https://www.se.com.sa/en/login/ | https://www.se.com.sa/en/GuestViewBill/ (guest view, no login) |
| NWC (water) | https://ebranch.nwc.com.sa/ | https://www.nwc.com.sa/ |
| Zain (internet) | https://app.sa.zain.com/en/dashboard | https://sa.zain.com/en/quickpay (quick pay, no login) |
| STC (phones) | https://my.stc/ | https://my.stc.com.sa/ |

### Step 3: Remind John of the non-portal bills

After the tabs are open, tell John explicitly:

> **Non-portal bills to handle this round:**
> - **Household help salary** — 1,000 USD — internal transfer (Main account → her account) or cash.
> - **a household helper** — 100 USD — cash on rounds, or transfer if he has an account.
> - **Digital subscriptions** — already on card ending XXXX, no action needed. (See `financial/subscriptions.md`.)

### Step 4: Pay-day flow

Suggest the order: utilities → telecom → household services.

1. SE tab → log in → pay current bill.
2. NWC tab → log in → pay.
3. Zain tab → log in → pay.
4. STC tab → log in → pay John's line → switch line → pay Jane's line.
5. Open banking app → internal transfer to household help.
6. Cash for a household helper.

After each, **tick the checkbox** in `bills.md` for the current month's tracker.

### Step 5: Capture anomalies

If any bill is unusually high (>20% above the average in `bills.md`), flag it inline in the tracker entry, e.g.:

```markdown
- [x] SE (electricity) — 410 ⚠ +60% vs avg, likely AC season starting
```

These flags become the input for next quarter's financial review.

### Step 6: Update autopay status if changed

If John turns on autopay for any bill during this session, update the **Autopay?** column in `bills.md` from `_TBD_` / `no` → `yes` and note the bank.

## When to use

- Once per month, right after salary lands (around the 26-27th).
- Or whenever a specific bill is overdue — same flow, ignore the ones already paid.

## Don't use for

- Salary or income tracking (that's `cash-flow.md`).
- Budget category review (that's `budget.md`).
- One-off purchases (no routine skill for that — just bank app).
