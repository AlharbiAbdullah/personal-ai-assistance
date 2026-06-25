# 17 — Config and Security

> Last updated: 2026-06-14.

`~/.claude/settings.json` — the harness contract (a symlink into the repo). Plus `.pai-protected.json` and `security-patterns.yaml` — the security posture. Plus the single-coordinator sync model (`SYNC-ARCHITECTURE.md`) that keeps the Linux and Mac copies in step. CLAUDE.md files remain the live source of truth; this chapter is a snapshot.

## The settings symlink (critical structural fact)

`~/.claude/settings.json` is **a symlink** into the vault repo:

```
~/.claude/settings.json -> ~/helm/03-rai/config/settings.json
```

So the live Claude Code config is version-controlled inside the vault. **Always edit via the helm path** (`~/helm/03-rai/config/settings.json`), never the `~/.claude` path. This matches the documented `~/.claude/CLAUDE.md -> ~/helm/03-rai/CLAUDE.md` and `~/.claude/hooks -> ~/helm/03-rai/hooks` symlinks.

A common mistake the old manual made was to call `03-rai/config/settings.json` a "mirror or staging" copy of `~/.claude/settings.json`. It is not a mirror — it **is** the file. The `~/.claude` path is the symlink; the repo path is the real, git-tracked target.

Note that **`03-rai/settings.json` does NOT exist** (only `03-rai/config/settings.json`). Several lib helpers — notably `lib/paths.get_settings_path()` — still point at the non-existent `03-rai/settings.json`. That stale path is the cause of the frozen `counts` block (see below).

## Configuration sources

| File | Purpose |
|------|---------|
| `~/helm/03-rai/config/settings.json` | Claude Code harness config (THE live file, symlink target): permissions, hooks wiring, statusline, plugins, effort level, notifications, MCP, autoMode |
| `~/.claude/settings.local.json` | Machine-local permission allowlist. A REAL file, NOT symlinked, NOT in the repo. ~190 allow entries. Intentionally excluded from sync |
| `~/helm/03-rai/.pai-protected.json` | Secret/PII/AI-attribution regex patterns for pre-commit blocking |
| `~/helm/03-rai/identity/security-patterns.yaml` | Security validator runtime patterns: blocked/confirm/alert bash, path access rules |

Plus the rest of `03-rai/config/`:

| File | Size | Purpose |
|------|------|---------|
| `03-rai/config/mcp.json` | 123 B | MCP server registry. Single entry: `context7` → `npx -y @upstash/context7-mcp@latest` |
| `03-rai/config/.skill-lock.json` | 461 B | Lockfile for externally-installed skills (version 3) |
| `03-rai/config/statusline.sh` | 4.1 KB | Legacy Omarchy-adaptive powerline statusline. **No longer wired** — settings.json now invokes the `claude-hud` plugin. Kept as fallback/reference |

---

## settings.json — the harness contract

This is the single most important config file. It tells Claude Code:

- What environment variables to set.
- Which tools to allow without prompting.
- Which hooks to fire on which events.
- What the statusline command is.
- Which plugins are enabled.
- The default effort level.
- Notification routing.
- MCP servers and auto-mode approvals.

### Top-level structure

```json
{
  "env": {},
  "permissions": {...},
  "hooks": {...},
  "statusLine": {...},
  "enabledPlugins": {...},
  "extraKnownMarketplaces": {...},
  "effortLevel": "xhigh",
  "theme": "dark-ansi",
  "agentPushNotifEnabled": true,
  "skipWorkflowUsageWarning": true,
  "skipAutoPermissionPrompt": true,
  "autoMode": {...},
  "notifications": {...},
  "mcpServers": {},
  "counts": {...}
}
```

### env — now empty

```json
"env": {}
```

The `env` block is **empty**. As of commit `abc1234` (2026-06-09, "make hooks, config, and news collectors cross-platform"), `PAI_DIR` was **removed** from `env`. The reason: the vault now syncs Mac↔Linux via git, and a hardcoded machine-specific home path (`~/helm/03-rai`) broke config on whichever machine was not the last to write it.

Hooks now **self-resolve** the Rai brain directory:
- `lib/paths.py::get_pai_dir()` = `os.environ["PAI_DIR"]` if set, else `Path.home() / "helm" / "03-rai"`.
- `security-validator.py` independently: `PAI_DIR = Path(os.environ.get("PAI_DIR") or Path.home()/"helm"/"03-rai")`.
- `protected_scan.py::_patterns_path()` walks `$PAI_DIR/.pai-protected.json` → ancestor dirs → `~/helm/03-rai/.pai-protected.json`.
- Every hook command + statusLine uses `$HOME/helm/03-rai/...` (the shell expands `$HOME`) rather than a hardcoded absolute path.

### permissions

The allow-list. Each entry is either a tool name or a tool with a glob pattern. `permissions.allow` holds ~69 global entries:

```json
"permissions": {
  "allow": [
    "Read", "Write", "Edit", "Glob", "Grep",
    "WebFetch", "WebSearch",
    "Bash(git *)",
    "Bash(uv *)", "Bash(uv run python *)", "Bash(uv run pytest *)",
    "Bash(python *)", "Bash(python3 *)", "Bash(pytest *)",
    "Bash(ruff *)", "Bash(mypy *)",
    "Bash(docker *)", "Bash(docker-compose *)",
    "Bash(pip *)", "Bash(npm *)", "Bash(node *)", "Bash(npx *)",
    "Bash(ls *)", "Bash(cat *)", "Bash(head *)", "Bash(tail *)",
    "Bash(mkdir *)", "Bash(rm *)", "Bash(cp *)", "Bash(mv *)",
    "Bash(touch *)", "Bash(chmod *)", "Bash(which *)", "Bash(pwd)",
    "Bash(env *)", "Bash(export *)", "Bash(echo *)",
    "Bash(curl *)", "Bash(wget *)", "Bash(gh *)",
    "Bash(dagster *)", "Bash(dbt *)", "Bash(psql *)", "Bash(duckdb *)",
    "Bash(source *)", "Bash(. *)", "Bash(sleep *)",
    "Bash(ssh -i ~/.ssh/spot-bot *)",
    "mcp__claude-in-chrome__tabs_context_mcp",
    "mcp__claude-in-chrome__tabs_create_mcp",
    "mcp__claude-in-chrome__navigate",
    ...
  ],
  "defaultMode": "auto"
}
```

Highlights:
- Core tools: `Read`, `Write`, `Edit`, `Glob`, `Grep`, `WebFetch`, `WebSearch`.
- Broad Bash wildcard families covering git, the Python/uv/ruff/mypy toolchain, Docker, package managers, common shell builtins, and data tools (`dagster`, `dbt`, `psql`, `duckdb`).
- One narrow SSH allow: `Bash(ssh -i ~/.ssh/spot-bot *)` — the investment paper-bot probe (read-only).
- 18 `mcp__claude-in-chrome__*` tools (tabs, navigate, page reads, javascript_tool, computer, find, form_input, gif_creator, console/network reads, resize, shortcuts, switch_browser, upload_image, update_plan).

`defaultMode: "auto"` means Claude Code automatically allows tools matching the allow-list without prompting. Combined with `skipAutoPermissionPrompt: true`, this gives Rai broad operational freedom inside the allow-list.

### hooks

The event → command mapping. See [./09-hooks-reference.md](./09-hooks-reference.md) for the full wiring. Quick recap (all commands now use `$HOME/helm/03-rai/...`):

```json
"hooks": {
  "SessionStart":      [{...}, {...}],          // session-start.py (via py-chroma.sh) + check-version.py
  "UserPromptSubmit":  [{...}, ...],            // 4 hooks
  "PreToolUse":        [{matcher, hook}, ...],  // 7 matched entries
  "PostToolUse":       [{matcher, hook}, ...],  // 3 matched entries
  "Stop":              [{...}],                  // stop-orchestrator.py
  "SessionEnd":        [{...}, ...]              // 7 hooks
}
```

There are **19 distinct hook Python scripts** in `03-rai/hooks/`, all 19 wired, across **24 total wired invocations** (SessionStart 2, UserPromptSubmit 4, PreToolUse 7, PostToolUse 3, Stop 1, SessionEnd 7). `security-validator.py` is reused across 4 PreToolUse matchers (Bash, Edit, Write, Read). Two PostToolUse entries call map-updater shell scripts, not Python hooks.

### statusLine

```json
"statusLine": {
  "type": "command",
  "command": "bash -c 'plugin_dir=$(ls -d \"${CLAUDE_CONFIG_DIR:-$HOME/.claude}\"/plugins/cache/claude-hud/claude-hud/*/ 2>/dev/null | ...); exec \"node\" \"${plugin_dir}dist/index.js\"'"
}
```

The statusline is driven by the `claude-hud` plugin (Node-based). The command resolves the newest claude-hud plugin build under `~/.claude/plugins/cache/claude-hud/claude-hud/*/` and execs it via **dynamically-resolved `node`** (`command -v node`, or newest `~/.nvm/.../bin/node`). The dynamic node resolution replaced a hardcoded nvm path on 2026-06-09 as part of the cross-platform fix. The old `03-rai/config/statusline.sh` shell script is no longer wired.

### enabledPlugins / extraKnownMarketplaces

```json
"enabledPlugins": {
  "frontend-design@claude-plugins-official": true,
  "claude-hud@claude-hud": true
},
"extraKnownMarketplaces": {
  "claude-hud": { ... "jarrodwatts/claude-hud" }
}
```

Plugins extend Claude Code with marketplace-installed packages. Currently active:
- `frontend-design` — design system + component generator (claude-plugins-official marketplace).
- `claude-hud` — heads-up display for the statusline (claude-hud marketplace, github `jarrodwatts/claude-hud`).

### effortLevel

```json
"effortLevel": "xhigh"
```

The default effort level for all sessions. `xhigh` means Rai operates at high reasoning intensity. The value churned during this window — `xhigh` → `high` (`abc1234`), with brief dips to `medium` and back — and a model pin (`claude-fable-5[1m]`, commit `abc1234`) was added then dropped (`abc1234`). The **on-disk value at HEAD is `xhigh`**, and there is **no model pin**. Quote `xhigh` as canonical.

### theme

```json
"theme": "dark-ansi"
```

Added 2026-06-14 (commit `abc1234`). A warm muted terminal theme consistent with John's palette preference.

### autoMode

```json
"autoMode": {
  "allow": ["$defaults", "<approval string>"]
}
```

Added 2026-06-14 (commit `abc1234`). The approval string authorizes **read-only** SSH to the investment paper-trading bot at `root@203.0.113.10` via `~/.ssh/spot-bot`, used only by the `/investment` status/ops sub-skills: `docker inspect`, loopback `curl` to freqUI at `127.0.0.1:8080`, and `cat` of `/opt/paper-portfolio/portfolio_state.json`. It is explicitly a dry-run/paper bot probe — never trades, restarts, or edits config.

### notifications

Notification backends and routing:

```json
"notifications": {
  "ntfy": { "enabled": false, "server": "https://ntfy.sh", "topic": "" },
  "discord": { "enabled": false, "webhook_url": "" },
  "twilio": { "enabled": false, "account_sid": "...", ... },
  "routing": {
    "task_complete": ["ntfy"],
    "long_task": ["ntfy"],
    "background_agent": ["ntfy"],
    "error": ["ntfy", "discord"],
    "security": ["ntfy", "discord"]
  }
}
```

All transports are **disabled** (no external pings fire). The routing map is aspirational — it declares what would happen if a transport were enabled. `agentPushNotifEnabled: true` (commit `abc1234`) is a separate harness-level push toggle for agent completion; the in-vault `notifications` transports above are independent and remain off.

### mcpServers

```json
"mcpServers": {}
```

Empty in `settings.json`. The real MCP config lives in `03-rai/config/mcp.json`, which registers exactly **one** server: `context7`. Other MCP tools (`claude-in-chrome`, the Canva/Figma/Gmail/Calendar/Drive family) are provided by Claude Code's connected-apps system, not this file.

### counts (STALE — known bug)

```json
"counts": {
  "skills": 66,
  "hooks": 22,
  "ratings": 4,
  "work": 27,
  "learnings": 16,
  "updatedAt": "2026-04-18T06:54:29.030013+00:00"
}
```

**These numbers are FROZEN and stale.** `update-counts.py` (SessionEnd) writes the recomputed counts to `lib/paths.get_settings_path()`, which returns the **non-existent** `03-rai/settings.json` (the real file is `03-rai/config/settings.json`). The write silently no-ops, so the `counts` block has not refreshed since 2026-04-18. **Do not quote these as current.** The real figures today: 35 top-level skill entries (31 routers + 4 leaves) and 19 wired hook scripts. The HUD plugin reads this block for the statusline, so the displayed count is also stale.

### skipAutoPermissionPrompt / skipWorkflowUsageWarning

```json
"skipAutoPermissionPrompt": true,
"skipWorkflowUsageWarning": true
```

`skipAutoPermissionPrompt: true` (combined with `defaultMode: "auto"`) means the harness does not prompt for tools matching the allow-list — Rai operates without prompting friction inside the allow-list. `skipWorkflowUsageWarning: true` suppresses the workflow usage warning. Both were enabled in commit `abc1234`.

---

## settings.local.json — machine-local, not in repo

`~/.claude/settings.local.json` is a **real file (~13 KB), NOT a symlink, NOT in the git repo**. Its single `permissions.allow` key holds **~190 entries** — an accreted per-machine allowlist. On the Mac this includes:

- Power-user commands: `aerospace *`, `borders ...`, `skhd ...`, `yabai *`, `defaults read/write/find *`, `osascript *`, `brew *`, `tmux *`, PlistBuddy hotkey reads, theme scripts, `displayplacer`, `system_profiler`, `btop`/`fastfetch`.
- Project-specific entries (GeoContext/Helios `PYTHONPATH` dagster/psql commands, a multi-line PLAN02SOURCES commit allow).
- Read scopes: `Read(/~/**)`, `Read(//tmp/**)`, `Read(//usr/local/var/homebrew/**)`.
- Skill allows: `Skill(hammer)`, `Skill(claude-hud:configure)`.

**This file is the per-machine surface and is intentionally excluded from sync** — its Mac-specific commands would break the Linux box (and vice versa). It needs separate backup; it is not in the helm git repo.

---

## .pai-protected.json — secret/PII scanner ruleset

**Path:** `~/helm/03-rai/.pai-protected.json`
**Size:** ~14 KB. **Version:** `rai-1.0` (based on PAI v4.0.3 + custom Rai/local additions).
**Read by:** `03-rai/hooks/lib/protected_scan.py`, which is invoked by `security-validator.py` when a Bash command is a `git commit`.

### What it does

Defines regex patterns that, if matched in a staged file's content being committed, block the commit. This is the pre-commit secret/PII/AI-attribution gate.

### Categories (15, from the file)

| Category | Severity | What it catches |
|----------|----------|-----------------|
| `api_keys` | medium | sk-ant, sk-, OpenAI/Anthropic/Perplexity/ElevenLabs/Google keys, AWS AKIA/ASIA, Stripe sk_live/pk_live, Twilio AC/SK, SendGrid, DataDog, NewRelic, Sentry, Telegram, Supabase, DO `dop_v1_`, npm, pypi, GitLab `glpat-`/`glsa_`, Tavily `tvly-`, JWT `eyJ...` |
| `github_tokens` | medium | `ghp_/gho_/ghu_/ghs_/ghr_`, `github_pat_...`, `GITHUB_TOKEN=` |
| `slack_tokens` | medium | `xoxb-/xoxp-/xoxa-/xoxr-` |
| `webhooks` | medium | Discord, Slack, Zapier, IFTTT webhook URLs |
| `database_credentials` | medium | mongodb/postgres/mysql/redis URIs with creds; `DATABASE_URL/REDIS_URL/MONGO_URI` with `user:pass@` |
| `private_keys` | medium | RSA/OPENSSH/PGP/EC/DSA/ENCRYPTED `BEGIN ... PRIVATE KEY` |
| `pii_financial` | medium | SSN, EIN, credit-card (Visa/Amex), routing/account numbers |
| `personal_emails` | medium | `john.doe@example.com` (+ variants) |
| `private_paths` | medium | `~/` (except `helm/`), `~/`, `~/.claude/` paths |
| `internal_infrastructure` | medium | Private IP ranges (10./172.16-31./192.168.) guarded to exclude version-string false positives; `.internal./.local./.corp./.private.` |
| `credentials_inline` | medium | `password=`/`secret=`/`API_KEY=`/`SECRET_KEY=` key-value shapes (require `=`/`:` so prose doesn't match), `Bearer ...`, `Authorization: Bearer` |
| `cloudflare` | medium | CF API token/key/zone/account IDs |
| `locale_identity` | medium | Family names gated by context, US-format phone and SSN patterns, the owner's city/state |
| `ai_attribution` | **high**, `scope: git_only` | `Co-Authored-By: Claude`, `<noreply@anthropic.com>`, "Generated with Claude Code", "🤖 Generated", "powered by Claude" |
| `misc_sensitive` | medium | `id_rsa/id_ed25519/id_ecdsa` (not `.pub`), `.pem/.key/.p12/.pfx`, `service_account*.json` |

The `api_keys` row is the cascade head — a long alternation of provider key shapes.

### Exceptions

- **`exception_contexts.allowed_prefixes`** (~44) — phrases that, on the same line as a match, suppress it: `# Example:`, `placeholder`, `YOUR_`, `EXAMPLE`, `<your-`, `pattern:`, `regex:`, `localhost:`, `127.0.0.1`, `192.168.x.x`, `10.x.x.x`, `secret detection`, `scan for`, etc.
- **`exception_files`** (~140 entries) — whole files/globs exempt from scanning: the scanner files themselves (`.pai-protected.json`, `security-validator.py`, `protected_scan.py`, `security-patterns.example.yaml`), all of `08-bawaba/**`, `13-archive/news/**`, news `.runs/`/scheduled logs, all memory subtrees (`ai-calls`, `learning/system/integrity`, `relationship`, `security`, `work`, `state/*`), `semantic-memory/chromadb/**` + `pending/**`, `13-archive/historical-sessions/**`, `06-learning/**`, `02-ana/identity/**` + `02-ana/financial/**`, and the large Helios project subtree.

### When the patterns fire

- **Pre-commit only (enforced)** — when a Bash command matches `\bgit\s+commit\b`, the validator calls `scan_staged_git_files()` over `git diff --cached --name-only --diff-filter=AM`. Any hit → block the commit (exit 2) with a summary of the first 5 offending files + categories, pointing the user at `python3 -m hooks.lib.protected_scan --staged`. **Fail-open**: if the scanner itself errors, it is logged as an alert and the commit proceeds.
- The scanner CLI is also runnable manually: `python3 -m hooks.lib.protected_scan <file>` or `--staged` (exit 1 on any match).

### Adjusting patterns

If a legitimate value is being false-flagged (e.g., a placeholder in documentation), the right fixes, in order of preference:
1. Add the file/glob to `exception_files` (if the whole file is safe — this is how Helios backend, news runs, and financial docs are handled).
2. Prefix the literal in docs with an allowed-prefix sentinel (e.g., `# Example: sk-ant-...`).
3. Tighten the pattern. Recent tightenings: `credentials_inline` now requires key-value shape (`abc1234`); `internal_infrastructure` now excludes version-string IPs (`abc1234`); DigitalOcean tokens for news were whitelisted (`abc1234`).

**Never widen `.pai-protected.json` allows just to push a commit.** When the scanner blocks a file, skip it and warn — never `--no-verify`.

---

## security-patterns.yaml — bash and path rules

**Path:** `~/helm/03-rai/identity/security-patterns.yaml`
**Version:** `1.0`, last_updated `2026-02-17`, philosophy `safe_functional` ("Meaningful protection without friction").
**Read by:** `03-rai/hooks/security-validator.py`.
**NOT auto-loaded** into session context (it is a non-`.md` file in `identity/`).

### Structure

```yaml
philosophy: safe_functional

bash:
  blocked:        # 10 patterns
    - "rm -rf /"
    - "rm -rf ~"
    - "sudo rm -rf /"
    - "sudo rm -rf ~"
    - "diskutil eraseDisk"
    - "diskutil zeroDisk"
    - "dd if=/dev/zero"
    - "mkfs"
    - "gh repo delete"
    - "gh repo edit --visibility public"

  confirm:        # 8 patterns
    - "git push --force"
    - "git push -f"
    - "git reset --hard"
    - "DROP DATABASE"
    - "DROP TABLE"
    - "TRUNCATE"
    - "terraform destroy"
    - "docker system prune"

  alert:          # 2 patterns (log but allow)
    - "curl.*\\|.*sh"
    - "curl.*\\|.*bash"

paths:
  zeroAccess:     # 6 globs
    - "~/.ssh/id_*"
    - "~/.ssh/*.pem"
    - "~/.aws/credentials"
    - "~/.gnupg/private*"
    - "**/credentials.json"
    - "**/service-account*.json"

  readOnly:       # 1
    - "/etc/**"

  confirmWrite:   # 3
    - "**/.env"
    - "**/.env.*"
    - "~/.ssh/*"

  noDelete:       # 3
    - ".git/**"
    - "LICENSE*"
    - "README.md"

projects: {}
```

### Behaviors

| Decision | What happens | Mechanism |
|----------|--------------|-----------|
| **blocked** | Tool call refused (exit 2, stderr `{"error":"BLOCKED: ..."}`) | substring match |
| **confirm** | Tool call paused; user must confirm | regex match (substring fallback) → `{"decision":"ask",...}` |
| **alert** | Tool call proceeds, warning logged | regex match → `log_event("alert",...)`, returns allow |
| **allowed** (default) | Tool call proceeds without note | — |

### Path access

| Class | Behavior |
|-------|----------|
| `zeroAccess` | Block ALL operations (any tool) → exit 2 |
| `readOnly` | Block Write/Edit → exit 2 (reads allowed) |
| `confirmWrite` | Confirm before Write/Edit |
| `noDelete` | Declared, but NOT enforceable from Write/Edit — only blocks Bash `rm` (per code comment) |

The validator resolves `~` and `.resolve()`s the path, then `fnmatch`es against each glob.

### Pattern-loading cascade

`security-validator.py` loads its patterns in a cascade:
1. `03-rai/identity/security-patterns.yaml` (user file — loaded first).
2. `03-rai/security-patterns.example.yaml` (the broader fallback template, if the user file is missing).
3. A hardcoded minimal dict in code (if PyYAML is unavailable).

The **example file is a superset**: its `blocked` adds `diskutil partitionDisk` / `apfs deleteContainer` / `apfs eraseVolume`; its `confirm` adds AWS destructive verbs (`s3 rm --recursive`, `ec2 terminate`, `rds delete`), `gcloud.*delete`, `terraform apply.*-auto-approve`, `pulumi destroy`, `docker volume rm`, `kubectl delete namespace`, `DELETE FROM.*WHERE`; its `alert` adds the `wget` variants. The user file is the slimmer, in-effect ruleset.

---

## security-validator.py — the runtime guard

**Path:** `~/helm/03-rai/hooks/security-validator.py` (~13 KB, last touched 2026-06-09).
**Wired on:** Bash, Edit, Write, Read (PreToolUse — 4 matchers).

This is the runtime layer. While `.pai-protected.json` is a pre-commit scanner, `security-validator.py` blocks destructive commands and protected-path access **as you go**.

Behavior model:
- **5-second SIGALRM watchdog** (exits 0 on timeout).
- **Fails OPEN** on any error (bad stdin, missing PyYAML, etc.) — security must never deadlock the agent. This is a deliberate design choice: a broken validator allows rather than blocks.
- Self-times via `lib/hook_timer`. It is by far the most-invoked hook (~1498 calls in a recent window) at avg 2.6 ms — cheap enough to run on every Bash/Edit/Write/Read.
- Logs every event → `03-rai/memory/security/YYYY/MM/security-YYYYMMDD.jsonl` (one JSON line: timestamp, event, tool, detail[:500], blocked). Logging failures are swallowed.

The pre-commit secret scan (`scan_staged_git_files()` against `.pai-protected.json`) is embedded inside this validator — it only runs when the Bash command matches `\bgit\s+commit\b`.

Since 2026-04-22 the validator changed only for cross-platform path resolution (the `~/helm/03-rai` fallback). Its block/confirm/alert/scan logic is otherwise stable.

---

## .skill-lock.json — externally-installed skills

**Path:** `~/helm/03-rai/config/.skill-lock.json` (461 B, version 3).

This is a **lockfile for externally-installed skills** (skills pulled from GitHub repos), not a per-session concurrency lock. It records one locked skill: `beautiful-mermaid` from `intellectronica/agent-skills` (GitHub), installed 2026-01-31.

```json
{
  "version": 3,
  "skills": {
    "beautiful-mermaid": {
      "source": "intellectronica/agent-skills",
      "installed": "2026-01-31T..."
    }
  }
}
```

To inspect or reset:

```bash
cat ~/helm/03-rai/config/.skill-lock.json | jq
```

---

## mcp.json — MCP servers

**Path:** `~/helm/03-rai/config/mcp.json` (123 B).

Registers exactly **one** MCP server:

```json
{
  "mcpServers": {
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp@latest"]
    }
  }
}
```

`context7` provides current library/framework documentation. The other MCP tools available in sessions (`claude-in-chrome`, the Canva/Figma/Excalidraw/Gmail/Google Calendar/Google Drive family) are provided by Claude Code's connected-apps system, not this file. Skills and agents call any of them via `mcp__server__tool` syntax.

---

## statusline.sh — legacy, unwired

**Path:** `~/helm/03-rai/config/statusline.sh` (4.1 KB).

A legacy Omarchy-adaptive powerline shell script (reads `~/.config/omarchy/current/theme/colors.toml`). It is **no longer wired** — `settings.json`'s `statusLine` now invokes the `claude-hud` plugin instead (see the statusLine section above). The script is kept in the repo as a fallback/reference. The live statusline is configured via `/claude-hud:setup` and `/claude-hud:configure`.

---

## Sync and scheduled maintenance — single-coordinator model

The vault lives on two machines and stays in step via a **single-coordinator** model adopted 2026-06-13. The authoritative doc is `~/helm/03-rai/SYNC-ARCHITECTURE.md`. This replaced an older two-writer GitHub-hub design (Mac and Linux both pushed to origin on a 30-minute offset) that fought a constant rebase war over the binary ChromaDB store.

### Topology

```
   GitHub origin  (off-site backup; ONLY Linux writes it)
        ^
        | push/pull
        |
   Linux "pc"  (coordinator + sole origin writer + sole ChromaDB writer)
   100.64.0.2  user: john   always-on desktop
        |
        |  keyless Tailscale SSH (both directions)
        v
   Mac "my-macbook"  (passive source + replica; NO scheduler; never touches GitHub)
   100.64.0.3  user: johndoe
```

| Role | Machine |
|------|---------|
| Sole coordinator + only machine that pushes `origin` (GitHub) | Linux `pc` (100.64.0.2, user `john`) |
| Sole ChromaDB writer | Linux `pc` |
| Passive source + replica; runs no scheduler; never touches GitHub | Mac (100.64.0.3, user `johndoe`) |

Two keyless Tailscale SSH channels:

| Direction | Command | `~/.ssh/config` Host |
|-----------|---------|----------------------|
| Linux → Mac | `ssh mac` | `mac` → `johndoe@my-macbook` |
| Mac → Linux | `ssh linux` | `linux` → `john@100.64.0.2` (must be the Linux local user, or `failed to look up local user`) |

Git remotes: Linux `git remote mac` → `mac:helm`; Mac `git remote linux` → `linux:helm`.

### Coordinator pipeline — run-maintenance-ubuntu.sh

**Path:** `~/helm/03-rai/skills/rai/scheduled/run-maintenance-ubuntu.sh` (16 KB).
**Schedule:** systemd user timer `rai-maintenance.timer` at **04:00 / 10:00 / 16:00 / 22:00** — on Linux only.
**Logs + lock:** `~/.local/state/rai-maintenance/` — OUTSIDE the repo, so a run never commits or rebases its own log. (No `.timer`/`.service` unit is checked into the repo — only this runner script.)

```
0. origin pull   : git fetch origin main  +  git merge --ff-only FETCH_HEAD
1. capture_mac   : ssh mac mac-sync.sh commit -> fetch mac -> merge -X ours mac/main
                   (Mac asleep -> log + skip)
2. merge-collisions (claude -p, 15m cap): fold backed-up collider files back in
3. process-sessions (claude -p, 30m cap): drain BOTH queues into ChromaDB (Linux = sole writer)
4. git-commit + push (claude -p, 30m cap): group churn, push to origin (the ONLY GitHub push)
5. refresh_mac   : ssh mac mac-sync.sh refresh -> propagate Linux origin SHA to Mac
```

Step 0 changed on 2026-06-14 (commit `abc1234`): the pull went from `pull --rebase --autostash origin main` to `fetch` + `merge --ff-only FETCH_HEAD`. The rebase form was the chronic jam — it replayed unpushed `wip(mac)` churn onto origin and choked on "Cannot merge binary files" in ChromaDB, stranding a half-rebase (detached HEAD + UU conflicts) that poisoned every following run. `ff-only` is a steady-state no-op and fails cleanly on the diverged-origin anomaly.

Step 1 merges Mac churn with `-X ours` so **Linux always wins conflicts** (keeping its authoritative ChromaDB); append-only `.jsonl` logs union both sides via `.gitattributes`.

Env toggles: `SYNC_ONLY=1` → steps 0/1/5 only (git plumbing, no `claude`); `NO_LOCK=1` → skip the overlap lock.

Self-healing machinery carried over from the two-writer era: an atomic `mkdir` overlap lock (stale-clears after 60 min); a **news-run guard** (skips if `claude --chrome` is live — the same box runs the news digest); `self_heal_git_state` (aborts a dead rebase/merge/cherry-pick, backs up + restores conflicted paths); `resolve_untracked_collisions`; `heal_autostash_conflicts` (3-pass, disk side wins); `drop_stale_autostashes` (>1 h). Durable collision backups land in `~/.local/state/helm-pull-collisions/`.

### Mac side — mac-sync.sh

**Path:** `~/helm/03-rai/skills/rai/scheduled/mac-sync.sh` (5.8 KB).
Driven by Linux over SSH; the Mac runs no scheduler of its own. Two subcommands:

- **`commit`** — clear half-merge state, `git add -A`, then **unstage `03-rai/semantic-memory/chromadb` (`git reset -- chromadb`)** so the Mac's read-induced ChromaDB byte-drift is never committed, then `git commit -m "wip(mac): churn snapshot <ts>"` (no push, no network). Gives Linux something to fetch.
- **`refresh`** — clear half-merge state, **discard read-induced ChromaDB drift (`git checkout -- chromadb`)**, then `git pull --rebase --autostash linux main` (pulls the **`linux`** remote over Tailscale SSH, **NOT GitHub** — the Mac's GitHub creds are in the macOS Keychain, unreachable from a non-interactive SSH session). Effectively always a fast-forward under the single-writer model; on autostash conflict the live disk copy wins.

### Why ChromaDB is Linux-only

`03-rai/semantic-memory/chromadb/` is a binary store (`chroma.sqlite3` + `*.bin`). Git cannot merge it. **Linux is its sole writer.** The Mac only reads it for recall — but *opening* the store mutates the binaries, and those read-induced byte changes must never sync back. So `mac-sync.sh` unstages chromadb on `commit` and discards it on `refresh`, and the coordinator merges Mac churn with `-X ours`. This is the heart of the 2026-06-14 jam fix.

### Mac-side maintenance — retired 2026-06-13

The Mac's own scheduled-maintenance machinery was **fully retired** (commits `abc1234`, `abc1234`). Gone:
- launchd `com.john.rai-maintenance` (the 23:00 backstop).
- `sleepwatcher` daemon + the heavy in-repo `run-maintenance.sh` Mac runner (`git rm`'d — the caffeinate/DarkWake drift-guard saga ended).
- `pmset repeat wakepoweron` (must be cancelled manually with `sudo pmset repeat cancel`).

One nuance to flag: a lightweight `~/.wakeup` pull-only wake refresh on the Mac was *restored* 2026-06-14 (per the maintenance-schedule memory note), but `SYNC-ARCHITECTURE.md` and `mac-sync.sh` — the in-repo source of truth at HEAD — describe the Mac as scheduler-less. Treat the in-repo docs as canonical and the `~/.wakeup` refresh as a pull-only convenience layered on top.

### Sync failure modes

| Failure | Behavior |
|---------|----------|
| Mac asleep/unreachable | capture + refresh skip; everything else runs; Mac syncs the next run it is awake for. No failed-run noise |
| Merge/autostash conflict | heal resolves keep-disk; divergent colliders backed up durably to `~/.local/state/helm-pull-collisions/`, folded by step 2 |
| Two consecutive hard failures | `notify-send` critical + abort before committing a conflicted tree |
| Linux down | no GitHub pushes until back; the Mac+Linux pair still holds latest state on disk |

---

## Gitignore policy — nothing informational is gitignored

As of commit `abc1234` ("brain-repo policy"), the vault **deliberately does NOT use `.gitignore` to hide secrets or information**. Protection is by *mechanism* (the secret scanner blocks commits), not by *ignore*. The only things ignored are real secrets (`twscrape.db`, `.env`) and machine droppings (`__pycache__/`, `*.pyc`, `.DS_Store`). The memory note restates this: "information is NEVER ignored — fix sync via mechanism, not ignores."

The single `.gitattributes` rule is a **merge strategy, not an ignore**:

```
03-rai/memory/**/*.jsonl merge=union
```

Append-only logs union both sides on merge, so sync never drops entries (added `abc1234`, re-touched `abc1234`).

---

## How to change config safely

| Change | Where | After change |
|--------|-------|--------------|
| Add a new tool to allow-list | `03-rai/config/settings.json` `permissions.allow` | Restart session |
| Add a machine-local allow | `~/.claude/settings.local.json` `permissions.allow` | Restart session (NOT synced) |
| Add a new hook | `03-rai/config/settings.json` `hooks.{event}` | Restart session |
| Disable a hook | Remove from `hooks.{event}` | Restart session |
| Change effort level | `03-rai/config/settings.json` `effortLevel` | Restart session (or `/effort` for one-off) |
| Change theme | `03-rai/config/settings.json` `theme` | Restart session |
| Update notification routing | `03-rai/config/settings.json` `notifications.routing` | Takes effect next event (transports must be enabled) |
| Whitelist a file from the secret scanner | `03-rai/.pai-protected.json` `exception_files` | Takes effect on next commit |
| Add a blocked bash pattern | `03-rai/identity/security-patterns.yaml` | Takes effect on next tool call |
| Add a zero-access path | `03-rai/identity/security-patterns.yaml` | Takes effect on next tool call |
| Change the MCP server | `03-rai/config/mcp.json` | Restart session |
| Adjust statusline display | `/claude-hud:configure` | Takes effect immediately |
| Change sync cadence | systemd `rai-maintenance.timer` (Linux, not in repo) | `systemctl --user daemon-reload` on Linux |

The `update-config` skill (Claude Code built-in) is designed for harness config edits — use it for `settings.json` changes. **Never edit `.pai-protected.json` to widen allows just to push a commit** (auto-mode denies it anyway); when the scanner blocks a file, skip and warn, never `--no-verify`.

---

## Security posture summary

The brain has three security layers, plus the sync model that keeps secrets from leaving the local pair:

1. **Permission allow-list** (`settings.json` + `settings.local.json` permissions) — what tools can be called at all.
2. **Runtime bash + path rules** (`security-patterns.yaml` via `security-validator.py`) — what bash commands and path accesses are allowed / confirmed / blocked, evaluated on every Bash/Edit/Write/Read.
3. **Pre-commit secret scan** (`.pai-protected.json` via `protected_scan.py`, embedded in `security-validator.py`) — what content cannot be committed (secrets, PII, AI-attribution).

Every tool call goes through layer 1. Bash, Read, Write, Edit go through layer 2. Only `git commit` triggers layer 3. A tool call survives all applicable layers → executes; fails any layer → blocked or requires confirmation.

The validator **fails open** — a broken security hook allows rather than blocks. The sync model adds a fourth practical guard: only Linux writes to GitHub, and the secret scanner runs on Linux's commit step, so secrets never reach the off-site backup.

## Failure modes

| Failure | Symptom | Fix |
|---------|---------|-----|
| Tool blocked by allow-list | Permission prompt on every call | Add the pattern to `permissions.allow` (machine-local → `settings.local.json`) |
| Bash command blocked | "BLOCKED: matches blocked pattern" | Either don't run it, or update `security-patterns.yaml` if a false-positive |
| Commit blocked by secret scan | "BLOCKED" with offending file list | Whitelist the file in `exception_files`, or rephrase the placeholder; never `--no-verify` |
| Counts in statusline stale | HUD shows skills:66, hooks:22 | Known bug: `update-counts.py` writes to non-existent `03-rai/settings.json`. Real counts: 35 skills, 19 hooks |
| Statusline not rendering | No HUD info | Check claude-hud plugin install; reconfigure with `/claude-hud:setup` |
| Sync jammed (detached HEAD / binary conflict) | Maintenance run aborts; ChromaDB conflict | Step 0 is now `merge --ff-only` (fixed `abc1234`); check `~/.local/state/rai-maintenance/` log |
| Mac shows "ahead of origin" | bogus git status on Mac | `refresh_mac` propagates Linux's origin SHA; rerun a maintenance cycle |
| Hook timeout | Session start slow | Check `lib/hook_timer` log (`hook-perf.jsonl`); profile the hook |

Full troubleshooting in [./20-troubleshooting.md](./20-troubleshooting.md).

## Backup and restore

Critical config files to back up:

- `~/.claude/settings.local.json` — machine-local, NOT in git. Needs separate backup per machine.
- `03-rai/config/settings.json` — in git (helm repo).
- `03-rai/.pai-protected.json` — in git.
- `03-rai/identity/security-patterns.yaml` — in git.
- `03-rai/config/mcp.json` — in git.
- `03-rai/SYNC-ARCHITECTURE.md` and `03-rai/skills/rai/scheduled/{run-maintenance-ubuntu,mac-sync}.sh` — in git.

Everything except `settings.local.json` lives in `~/helm/03-rai/`, in git, and is replicated to both machines by the sync model (and pushed off-site to GitHub by the Linux coordinator). The `settings.local.json` machine-local allowlist is the one file that needs separate, per-machine backup.

To restore: copy the backup into place (via the helm path for repo files). Restart Claude Code. Test.
