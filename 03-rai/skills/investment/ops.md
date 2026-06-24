---
name: ops
description: Operate the cloud trading bot — status, logs, restart, deploy a strategy/config change, freqUI watch tunnel, and the guarded go-live gate. USE WHEN John wants to inspect, restart, update, or (only with eyes-open confirmation) take the spot-bot live.
allowed-tools: Read, Bash
---

# Bot Ops

Hands-on operation of the cloud trading bot. The bot is **Freqtrade in DRY-RUN** on a DigitalOcean droplet — Docker container `spot-bot` (`restart: unless-stopped`), compose at `/opt/spot-bot/docker-compose.yml`, config at `/opt/spot-bot/user_data/config.json`. The vault's source-of-truth copy lives at `~/helm/02-ana/financial/investment/02-crypto/spot-bot/`.

**Guardrails (never violate):** Sharia-compliant (spot, no leverage/short/riba) · debt-first (the high-interest cards at a high APR beat any trade) · paper-first · cloud-only. **NEVER flip `dry_run` to `false` silently.** Going live requires an explicit eyes-open confirmation AND walking the bot's `GO-LIVE-CHECKLIST.md` — see Step 6. Tokens/keys never enter the vault.

## SSH one-liner (reuse for every remote call)

```bash
SSH="ssh -i ~/.ssh/spot-bot -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@203.0.113.10"
```

## Instructions

### Step 1: Status — is it alive and trading?

```bash
$SSH 'docker ps --filter name=spot-bot --format "{{.Names}}  {{.Status}}  {{.RunningFor}}"'
$SSH 'docker inspect -f "restart={{.HostConfig.RestartPolicy.Name}} health={{.State.Health.Status}} started={{.State.StartedAt}}" spot-bot'
```

Confirm the container is `Up`, `restart=unless-stopped`, and not restart-looping. Then query the freqtrade REST API for the live picture (see Step 4 for the password fetch):

```bash
PW=$($SSH "grep -oE '\"password\"[^,]+' /opt/spot-bot/user_data/config.json | head -1 | sed -E 's/.*: *\"([^\"]+)\".*/\\1/'")
$SSH "curl -s -u freqtrader:'$PW' http://127.0.0.1:8080/api/v1/show_config"   # CONFIRM dry_run:true
$SSH "curl -s -u freqtrader:'$PW' http://127.0.0.1:8080/api/v1/status"        # open trades
$SSH "curl -s -u freqtrader:'$PW' http://127.0.0.1:8080/api/v1/profit"        # PnL summary
```

Report state honestly: dry-run flag, open trades, paper PnL, uptime. If `dry_run` is anything but `true`, surface it loudly — that is a live account.

### Step 2: Logs — what is it doing / why did it break?

```bash
$SSH 'docker logs spot-bot --tail 50'
$SSH 'docker logs spot-bot --tail 200 2>&1 | grep -iE "error|trace|exception|reject|stall"'   # triage
```

Look for unexplained errors, stalls, double-fills, or model dropouts (per the checklist's parity lessons). Boring logs = healthy.

### Step 3: Restart

```bash
$SSH 'cd /opt/spot-bot && docker compose restart'
```

Then re-run Step 1 to confirm it came back `Up` and clean. Use this for config reloads that don't change the image; use Step 5 when you've changed files.

### Step 4: Fetch the freqUI / API password (runtime only — never hardcode)

The basic-auth user is `freqtrader`; the password lives ONLY in the droplet config. Fetch it at runtime, never write it into this skill or the vault:

```bash
$SSH "grep -oE '\"password\"[^,]+' /opt/spot-bot/user_data/config.json | head -1 | sed -E 's/.*: *\"([^\"]+)\".*/\\1/'"
```

### Step 5: Update strategy or config (vault → droplet)

Edit the **vault copy first** (source of truth), then deploy. Never edit on the droplet directly.

```bash
VAULT=~/helm/02-ana/financial/investment/02-crypto/spot-bot

# 1. (You edit the vault file — strategy code or config.json — via Read/Edit.)

# 2. Ship it to the droplet:
scp -i ~/.ssh/spot-bot -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
    "$VAULT/user_data/strategies/"*.py root@203.0.113.10:/opt/spot-bot/user_data/strategies/
scp -i ~/.ssh/spot-bot -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
    "$VAULT/user_data/config.json" root@203.0.113.10:/opt/spot-bot/user_data/config.json

# 3. Recreate the container with the new files:
$SSH 'cd /opt/spot-bot && docker compose up -d --force-recreate'
```

Before shipping `config.json`, re-confirm the compliance gate: `trading_mode:"spot"`, no `leverage` key, `can_short:false`, and **`dry_run:true`** unless Step 6 has been completed. After deploy, run Step 1 + Step 2 to verify. **Never `scp` a file containing keys/secrets into the vault path** — secrets live only in the droplet's gitignored `.env`.

### Step 6: GO-LIVE GATE — paper → real money (do not skip)

This is the **only** path to `dry_run:false`. Default answer is **no.**

1. **Demand explicit, eyes-open confirmation.** John must say, in plain words, that he wants real money in the bot and accepts the loss. Restate the debt math first: the **high-interest cards cost a high APR — a guaranteed return no strategy here beats.** Every dollars in the bot is a dollars not paying that down. Real money is **tuition, not investment**; cap it at the **a small capped learning allocation**, fully losable.
2. **Walk the checklist line by line:** `Read` `~/helm/02-ana/financial/investment/02-crypto/spot-bot/GO-LIVE-CHECKLIST.md` and confirm EVERY box, out loud, with the bot:
   - Compliance gate still true (spot, no leverage, `can_short:false`, no leveraged tokens).
   - **Weeks** of dry-run on live data — not days — with sane, boring logs.
   - Paper ↔ live **parity** proven (one fill per signal, fees modeled, position book reconciles 1:1, realistic slippage).
   - Strategy edge validated (purged walk-forward, holds across ≥3 windows, exits re-tuned 5×→1×).
   - Risk recalibrated to the **real** balance; daily-loss + max-DD kill-switches wired and tested.
   - Per-symbol Binance spot **minimum-notional / lot-size** filters clear at the real balance; whitelist pruned to what can actually fill.
3. **Keys (only after every box passes):** create **spot-only** Binance API keys — *Enable Spot Trading ONLY*, futures/margin/withdrawals OFF — **IP-restricted** to the droplet IP. Supply them **via ENV only** in the droplet's gitignored `.env`, never committed:
   ```bash
   # On the droplet only, in a root-only gitignored .env:
   export FREQTRADE__EXCHANGE__KEY="..."
   export FREQTRADE__EXCHANGE__SECRET="..."
   ```
   `config.json` exchange `key`/`secret` stay `""`. Confirm nothing secret is in git history.
4. **Flip the one change:** `cp config.json config-live.json`, set `dry_run:false` in `config-live.json` only, start with that + the ENV keys at **tiny** size, watch closely, keep `docker compose down` ready as instant rollback.

If any box is unchecked, or confirmation is anything less than explicit, **stop and stay in dry-run.** A blown account researches nothing.

### Step 7: freqUI watch tunnel (hand to John)

Give John this to watch the dashboard locally over an SSH tunnel:

```bash
ssh -i ~/.ssh/spot-bot -N -L 8080:127.0.0.1:8080 root@203.0.113.10
# then open http://127.0.0.1:8080  (login: freqtrader + the password from Step 4)
```

## Rules

- Every remote action goes through the SSH one-liner above. No other access path.
- Fetch the freqUI/API password at runtime (Step 4). Never hardcode or commit it.
- Edit the vault copy first; the droplet is a deploy target, not the source of truth.
- Secrets (keys, tokens, `.env`) NEVER enter the vault or git — droplet-only.
- `dry_run:false` requires Step 6 in full. Never flip it silently or "just to test."
- End any Sharia verdict you give with: "not professional advice — confirm with a qualified advisor."
