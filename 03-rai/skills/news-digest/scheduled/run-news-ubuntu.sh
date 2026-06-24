#!/bin/bash
# news scheduled runner (UBUNTU) — HEADLESS: drives the news-digest skill via
# `claude -p --chrome` (no terminal mux, no WezTerm). Runs on the 24/7 Ubuntu box.
#
# Usage:  run-news-ubuntu.sh [daily|weekly]
# Env:    RECOVERY=1         skip the git pull + run ONE attempt with the
#                            budget-protecting retry prompt (no auto-retry)
#         WATCHDOG_SEC=N     hard cap per digest attempt (default 7200 = 120 min)
#         RETRY_DELAY_SEC=N  wait before the automatic retry (default 600 = 10 min)
#         NO_RETRY=1         disable the automatic retry
#
# Why headless `-p` (2026-06-09): the old path spawned an INTERACTIVE
# `claude --chrome` session in a WezTerm pane. That hit a one-time "Bypass
# Permissions mode → Yes, I accept" prompt that BLOCKS an unattended session
# forever (unsuppressable in interactive, not persisted) — THAT is what hung the
# 03:00 runs for the full 120-min watchdog. `claude -p --chrome` shows no such
# prompt, loads skills fine (the Skill tool works in -p), drives the local Chrome,
# and runs to completion (verified: 773 items, all sources, post-filled). So the
# whole WezTerm layer is gone (John moved to Ghostty anyway). Completion =
# the `-p` process exiting; `timeout` is the watchdog. No PTY, no pane, no socket.
#
# Auto-retry (2026-06-10): a run can be killed mid-flight by a per-request API
# Usage Policy block (Fable 5 cyber-classifier false positive on security-news
# content — see logs/2026-06-10-daily.log, req_011CbtdKnb3971pqXadnh8mz). The
# block is probabilistic per request, so one delayed retry usually passes. On a
# failed attempt 1 the runner waits RETRY_DELAY_SEC and re-runs ONCE with a
# budget-protecting prompt that reuses same-day .runs/ dumps instead of
# re-collecting — critically X, whose account-level read budget does NOT reset
# within the day (re-scraping after the 03:24 kill is what capped X at 264/2000
# on 2026-06-10). recovery-prompt.txt is RETIRED: it was the one-off X-scroller
# diagnostic prompt and that collection bug is fixed; RECOVERY=1 now uses the
# same built-in retry prompt.
#
# Browser: drives the LOCAL Chrome (isLocal:true), which must be logged into X for
# X coverage. A fast headless preflight ensures a local browser is paired before
# the run (restarting Chrome only if it is not already paired). NOTE: while the Mac
# is signed into the same Claude account it also appears as a remote (isLocal:false)
# browser; the prompt selects the local one, but pinning is best-effort.
# Scheduled by systemd user timers news-daily.timer (03:00) and news-weekly.timer
# (Sat 07:00); graphical env comes from the systemd user environment (Hyprland).

set -uo pipefail
export PATH="$HOME/.local/bin:/usr/bin:/bin:$PATH"

MODE="${1:-daily}"
CLAUDE="$HOME/.local/bin/claude"
HELM="$HOME/helm"
SCHED="$HELM/03-rai/skills/news-digest/scheduled"
CHROME_DIR="$HOME/.config/google-chrome"
CHROME_LOG="/tmp/chrome-news-$MODE.log"
WATCHDOG_SEC="${WATCHDOG_SEC:-7200}"
RETRY_DELAY_SEC="${RETRY_DELAY_SEC:-600}"
RUNS_DIR="$HELM/03-rai/skills/news-digest/.runs/$(date +%Y-%m-%d)"
LOGDIR="$HOME/.local/state/news-digest/logs"   # OUT of the repo — no per-run log-commit churn
mkdir -p "$LOGDIR"
LOG="$LOGDIR/$(date +%Y-%m-%d)-$MODE.log"
exec >>"$LOG" 2>&1

echo "════════ $(date '+%F %T') START mode=$MODE (headless -p) ════════"

# 1. Sync with whatever the Mac pushed (cross-machine protocol; --autostash
#    because the tree is essentially always dirty between runs).
#    --autostash covers dirty TRACKED files only — an incoming commit carrying
#    a path that exists locally as UNTRACKED still aborts the pull (how the
#    2026-06-06 pulls failed): identical → drop local; divergent → move aside.
COLLISION_BACKUP="$HOME/.local/state/helm-pull-collisions/$(date +%Y%m%d-%H%M%S)"
resolve_untracked_collisions() {
  git -C "$HELM" fetch origin main || return 1
  local p
  while IFS= read -r p; do
    [ -e "$HELM/$p" ] || continue
    git -C "$HELM" ls-files --error-unmatch "$p" >/dev/null 2>&1 && continue
    if git -C "$HELM" show "origin/main:$p" 2>/dev/null | cmp -s - "$HELM/$p"; then
      rm -f "$HELM/$p"; echo "collision (identical): dropped local untracked $p"
    else
      mkdir -p "$COLLISION_BACKUP/$(dirname "$p")"
      mv "$HELM/$p" "$COLLISION_BACKUP/$p"
      echo "COLLISION (divergent): moved local untracked $p -> $COLLISION_BACKUP/$p"
    fi
  done < <(git -C "$HELM" diff --name-only HEAD origin/main)
}
if [ "${RECOVERY:-0}" = "1" ]; then
  echo "RECOVERY MODE: skipping git pull to preserve locally-seeded dedup priors."
else
  resolve_untracked_collisions || echo "WARN: fetch failed — attempting pull anyway."
  git -C "$HELM" pull --rebase --autostash origin main || echo "WARN: pull failed — continuing with local state."
fi

# 2. Chrome lifecycle (daily/recovery only — weekly mines archived dumps + reads
#    dailies and enriches via WebSearch/WebFetch; it never needs a browser).
ensure_native_host_wrapper() {    # repair the version-pinned native-host wrapper if a CLI upgrade dangled it
  local wrapper="$HOME/.claude/chrome/chrome-native-host"
  [ -f "$wrapper" ] || { echo "WARN: native-host wrapper missing at $wrapper — run 'claude --chrome' once interactively to (re)install it."; return; }
  local pinned; pinned="$(grep -oE '/[^"]*/versions/[0-9.]+' "$wrapper" | head -1)"
  if [ -n "$pinned" ] && [ ! -x "$pinned" ]; then
    local live; live="$(readlink -f "$CLAUDE")"
    printf '#!/bin/sh\nexec "%s" --chrome-native-host\n' "$live" >"$wrapper"; chmod +x "$wrapper"
    echo "native-host: repaired stale wrapper -> $live"
  fi
}

launch_chrome() {                 # launch the local Default Chrome, anti-throttle flags, detached
  export DISPLAY="${DISPLAY:-:0}" WAYLAND_DISPLAY="${WAYLAND_DISPLAY:-wayland-1}" XDG_RUNTIME_DIR="${XDG_RUNTIME_DIR:-/run/user/$(id -u)}"
  setsid google-chrome \
    --disable-renderer-backgrounding --disable-backgrounding-occluded-windows \
    --disable-background-timer-throttling --disable-features=CalculateNativeWinOcclusion \
    </dev/null >"$CHROME_LOG" 2>&1 &
}

restart_chrome() {                # only when unpaired: kill the local Chrome + relaunch fresh so it loads the native host
  pkill -u "$USER" -TERM -x chrome 2>/dev/null || true
  local _i; for _i in $(seq 1 20); do pgrep -u "$USER" -x chrome >/dev/null || break; sleep 0.5; done
  pgrep -u "$USER" -x chrome | xargs -r kill -KILL 2>/dev/null || true
  rm -f "$CHROME_DIR/SingletonLock" "$CHROME_DIR/SingletonSocket" "$CHROME_DIR/SingletonCookie"
  launch_chrome; sleep 6
}

preflight_local_paired() {        # rc 0 = a LOCAL (isLocal:true) browser is paired; ~20-30s headless probe
  local out rc; out="$(mktemp /tmp/news-preflight.XXXXXX.txt)"
  printf '%s' 'Call the tool mcp__claude-in-chrome__list_connected_browsers exactly once with no arguments, then output its raw JSON result verbatim and nothing else. Do not call any other tool, do not navigate, do not open tabs.' \
    | timeout 120 "$CLAUDE" -p --chrome --output-format text \
        --allowedTools "mcp__claude-in-chrome__list_connected_browsers" \
        --dangerously-skip-permissions >"$out" 2>/dev/null
  grep -q '"isLocal"[[:space:]]*:[[:space:]]*true' "$out"
  rc=$?; rm -f "$out"; return $rc
}

ensure_paired() {                 # rc 0 = local browser paired (restarts Chrome up to twice); reused before the retry attempt
  ensure_native_host_wrapper
  pgrep -x chrome >/dev/null 2>&1 || { echo "Chrome not running — launching the local Default profile."; launch_chrome; sleep 6; }
  local attempt
  for attempt in 1 2 3; do
    echo "Preflight: local-browser pairing check attempt $attempt ..."
    if preflight_local_paired; then echo "Preflight: a LOCAL browser is paired and drivable."; return 0; fi
    echo "Preflight attempt $attempt: no local browser paired (likely Chrome predates the native host)."
    [ "$attempt" -lt 3 ] && { echo "Restarting the local Chrome fresh so it loads the host and pairs ..."; restart_chrome; }
  done
  return 1
}

if [ "$MODE" != "weekly" ]; then
  if ! ensure_paired; then
    echo "PREFLIGHT FAILED: no local browser paired after 2 restarts — ABORTING in minutes (not hanging)."
    notify-send -a news-digest -u critical "News digest ($MODE) ABORTED" "No local Chrome paired — see $LOG" 2>/dev/null || true
    printf 'preflight pairing failure %s mode=%s\n' "$(date '+%F %T')" "$MODE" >>"$LOGDIR/preflight-failures.log"
    exit 1
  fi
fi

# 3. Mode-specific prompt + expected output file + failure markers.
#    HEADLESS_NOTE (2026-06-12): both attempts that morning died because the agent
#    ended its turn to "wait" for a background X collector — under `claude -p`,
#    ending the turn EXITS the process (and systemd then kills the whole cgroup,
#    including "detached" collectors). The collector had hit its 2,003-tweet
#    target 12s before the run died. This clause is the fix; keep it in every
#    prompt this script sends.
HEADLESS_NOTE="HEADLESS -p MODE (critical): this session runs under claude -p — the process TERMINATES the instant you end your turn, and background-task completion will NOT re-invoke you; any background processes you spawned are killed with the session. NEVER end your turn to wait for a background collector, monitor, timer, or notification. If you start a long-running background process, poll it from the FOREGROUND (a blocking Bash loop: sleep 30-60s, check its status file, repeat) until it completes, then continue in the same turn. Ending your turn before the digest file is written and verified = failed run."
FAIL_ROOT="$HELM/08-bawaba/.news-failed-$(date +%Y-%m-%d).md"
FAIL_DAILY="$HELM/08-bawaba/daily/.news-failed-$(date +%Y-%m-%d).md"
if [ "$MODE" = "weekly" ]; then
  PROMPT="Use the Skill tool to load the skill named news-digest, then run it in WEEKLY mode — the Bawaba Weekly MAGAZINE (SKILL.md section 'Weekly Magazine'), topical departments in magazine prose, NOT a news recap. Pipeline: (1) run python3 ~/helm/03-rai/skills/news-digest/weekly_mine.py and confirm its console summary reports >0 week-unique records; (2) read the five department briefs + coverage.md it writes under .runs/weekly-<week>/, plus this week's daily digests from BOTH ~/helm/08-bawaba/daily/ AND ~/helm/13-archive/news/daily/ (prefer the daily/ copy when a date exists in both; skip missing days silently); (3) pick subjects per department — one Cover Story, the Model State inventory, ONE Lesson concept with real teaching depth, Workshop tools, 3-5 Reading Shelf long-reads — and pull full text from ~/helm/13-archive/news/dumps/<day>/ whenever a candidate needs depth; (4) enrich the Cover Story, The Lesson, and Model State subjects with WebSearch/WebFetch ONLY, max ~10 fetches — NEVER open a browser, never scrape sources; (5) write the issue (Editor's Letter, Cover Story, Model State, The Lesson, The Workshop, Reading Shelf, Closing — Wisdom, coverage footer; ~8,000-10,000 words) to ~/helm/08-bawaba/weekly/ named for the ISO week; (6) move any PRIOR week's file from 08-bawaba/weekly/ to 13-archive/news/weekly/ (move, never delete), then grep the new issue for CLAUDE_FILL and for instruction comments and confirm zero. Run fully autonomously; ask nothing. $HEADLESS_NOTE"
  OUT="$HELM/08-bawaba/weekly/$(date +%G)-W$(date +%V).md"
else
  PROMPT="Use the Skill tool to load the skill named news-digest, then run it to generate today's full DAILY digest. Run fully autonomously; ask nothing. $HEADLESS_NOTE SCHEDULED MODE: apply the scheduled-mode deadline contract in SKILL.md (config.yaml scheduled_mode) — collection must end by start+85min, never start a cooldown/retry that crosses that line, and ship the digest with explicitly-noted partial coverage rather than nothing. X COLLECTION (PRIMARY — do this FIRST, it is the dealbreaker source): X is gathered in THREE gentle passes per night to beat X's per-session timeline throttle — the 21:00 and 00:00 passes already ran (news-x-collect.timer) and ACCUMULATED into .runs/$(date +%Y-%m-%d)/x_foryou.json + x_following.json (merge-write, deduped by tweet id, tweets tagged source_tier). Do the FINAL pass now as a BLOCKING FOREGROUND call (NOT the Chrome MCP). Run: export PATH=\"\$HOME/.local/bin:\$PATH\"; uv run ~/helm/03-rai/skills/news-digest/_collect_x_headless.py --date $(date +%Y-%m-%d) --target 700 --following-target 50 --phase both — and WAIT for it to finish; it merge-appends this pass into the same pool. @johndoe is X Premium (~10k/day read cap), but each pass is intentionally gentle (~400-700 tweets) and the THREE passes accumulate — judge success on the MERGED pool, not this single pass: read the length of x_foryou.json / x_following.json after it finishes; success = >=700 For You + >=110 Following cumulative. A quick plateau on this final pass is EXPECTED when the pool is already full — do NOT grind reloads. If it exits 3 or writes .runs/<date>/x_LOGIN_FAILED.json the X login is dead — write a one-line marker to BOTH \$FAIL_ROOT AND \$FAIL_DAILY and ship a partial (a partial-noted digest beats none under scheduled mode). Do NOT use the slow MCP scroll ladder unless the headless chrome itself refuses to launch. BROWSER (Substack + Medium ONLY): for just those two sources, call list_connected_browsers and select_browser with the deviceId whose isLocal is true; do not call AskUserQuestion or wait on a picker. If no local browser connects within ~2 minutes, mark Substack+Medium partial and CONTINUE — do NOT abort the run, because X (the dealbreaker) already came from the headless collector and curl sources still run. Collect all sources (Hacker News, Reddit, GitHub Trending via curl; Substack, Medium via MCP; X via the headless collector) and save the digest to ~/helm/08-bawaba/daily/$(date +%Y-%m-%d).md. POST-FILL: you are not finished until every <CLAUDE_FILL_*> placeholder is replaced with real prose, every raw scaffolding line (those beginning with <!-- raw:) is stripped, AND every <!-- CLAUDE INSTRUCTIONS --> block is deleted (News Wire trim instructions, Gems hook rubric, Hot Topics); the News Wire instruction block requires you to DELETE non-tech candidate bullets before writing briefs. Before finishing, run grep -c on the output file for CLAUDE_FILL, for the raw scaffolding marker, and for the literal text <!-- CLAUDE, and confirm all three are 0. A digest shipped with placeholders or instruction blocks is a failed run."
  OUT="$HELM/08-bawaba/daily/$(date +%Y-%m-%d).md"
fi

# Budget-protecting retry prompt: reuse same-day .runs/ dumps instead of
# re-collecting. X is the hard constraint — its account-level read budget does
# not reset within the day, so a retry that re-scrapes X burns coverage for the
# NEXT attempt too. Prepended to the standard prompt; the override wording wins
# over the collection instructions inside it.
build_retry_prompt() {            # $1 = failure reason for attempt 1
  if [ "$MODE" = "weekly" ]; then
    printf '%s' "RETRY RUN — attempt 2 of today's weekly magazine: attempt 1 failed ($1). Mining the dumps and reading briefs/dailies is cheap and safe to redo, so regenerate the issue in full (weekly_mine.py is idempotent; the web-fetch cap applies fresh). $PROMPT"
  else
    printf '%s' "RETRY RUN — attempt 2 of today's scheduled digest: attempt 1 failed partway ($1). Collection artifacts from attempt 1 likely already exist in $RUNS_DIR/. BUDGET PROTECTION — this OVERRIDES the collection instructions that follow: as your first collection step, list $RUNS_DIR/; for every source whose dump file already exists there and is non-trivial, LOAD AND REUSE that dump instead of re-collecting the source — re-scrape only sources with no usable dump. X IS CRITICAL: the X account read budget is account-level and does NOT reset within the same day. If x_foryou.json or x_following.json exists there with more than 50 tweets, you MUST NOT re-scrape that timeline — merge the existing dump(s) and, if under target, note partial X coverage in the run note. Only if an X dump is missing or near-empty may you attempt ONE collection window; if it plateaus at ~10-15 tweets with an endless loading spinner, that is an account-level read rate-limit — do NOT run cooldown retries; record the finding and ship with partial X. A partial digest with an explicit run note beats no digest. Everything below still applies. $PROMPT"
  fi
}

if [ "${RECOVERY:-0}" = "1" ] && [ "$MODE" != "weekly" ]; then
  PROMPT="$(build_retry_prompt "manual recovery run")"
  echo "RECOVERY MODE: using the built-in budget-protecting retry prompt (recovery-prompt.txt is retired)."
fi
echo "Expecting output: $OUT"

# 4. Run the digest HEADLESS (no WezTerm). `timeout` is the watchdog; completion
#    is this process returning. Weekly needs no browser, so it drops --chrome.
run_headless() {                  # $1 = prompt
  if [ "$MODE" = "weekly" ]; then
    printf '%s' "$1" | timeout "$WATCHDOG_SEC" "$CLAUDE" -p --dangerously-skip-permissions --output-format text >>"$LOG" 2>&1
  else
    printf '%s' "$1" | timeout "$WATCHDOG_SEC" "$CLAUDE" -p --chrome --dangerously-skip-permissions --output-format text >>"$LOG" 2>&1
  fi
}

digest_ok() {                     # complete digest on disk: exists, no placeholders/scaffolding/instruction blocks, non-trivial size
  local min_bytes=2000
  [ "$MODE" = "weekly" ] && min_bytes=20000   # a ~60-min magazine issue is never this small
  [ -f "$OUT" ] && ! grep -qE 'CLAUDE_FILL|<!-- raw:|<!-- CLAUDE' "$OUT" 2>/dev/null && [ "$(stat -c%s "$OUT" 2>/dev/null || echo 0)" -gt "$min_bytes" ]
}

failure_reason() {                # best-effort classification of attempt 1 for the retry prompt + notification
  if grep -q 'Usage Policy' "$LOG"; then
    echo "API Usage Policy block — likely a cyber-classifier false positive on security-news content"
  elif [ -f "$OUT" ]; then
    echo "incomplete digest — placeholders left or file too small"
  else
    echo "no digest file produced"
  fi
}

echo "Running headless digest (timeout ${WATCHDOG_SEC}s) ..."
run_headless "$PROMPT" || echo "WARN: headless run exited non-zero (rc $?)."

# 5. Auto-retry ONCE on failure (2026-06-10). Skipped for manual RECOVERY runs
#    (already a retry) and when NO_RETRY=1. Re-checks Chrome pairing first in
#    case Chrome died during attempt 1.
if ! digest_ok && [ "${RECOVERY:-0}" != "1" ] && [ "${NO_RETRY:-0}" != "1" ]; then
  REASON="$(failure_reason)"
  echo "ATTEMPT 1 FAILED: $REASON — auto-retrying once in ${RETRY_DELAY_SEC}s with the budget-protecting retry prompt."
  notify-send -a news-digest "News digest ($MODE) attempt 1 failed" "$REASON — auto-retry in $((RETRY_DELAY_SEC / 60)) min" 2>/dev/null || true
  sleep "$RETRY_DELAY_SEC"
  if [ "$MODE" != "weekly" ] && ! ensure_paired; then
    echo "RETRY ABORTED: no local browser paired before the retry attempt."
    printf 'retry preflight pairing failure %s mode=%s\n' "$(date '+%F %T')" "$MODE" >>"$LOGDIR/preflight-failures.log"
  else
    echo "Running retry attempt (timeout ${WATCHDOG_SEC}s) ..."
    run_headless "$(build_retry_prompt "$REASON")" || echo "WARN: retry exited non-zero (rc $?)."
  fi
fi

# 6. Archive the day's raw dumps regardless of outcome — present_v5.py copies
#    them on success, but a failed run's partial collection is information too
#    (helm = brain: nothing collected is thrown away). Idempotent rsync.
if [ "$MODE" != "weekly" ]; then
  RUNS_TODAY="$HELM/03-rai/skills/news-digest/.runs/$(date +%Y-%m-%d)"
  if [ -d "$RUNS_TODAY" ]; then
    mkdir -p "$HELM/13-archive/news/dumps/$(date +%Y-%m-%d)"
    rsync -a "$RUNS_TODAY/" "$HELM/13-archive/news/dumps/$(date +%Y-%m-%d)/" 2>/dev/null \
      && echo "Dumps archived to 13-archive/news/dumps/$(date +%Y-%m-%d)/"
  fi
fi

# 7. Outcome notification (the local Chrome is left running — never killed here).
#    Exits non-zero on failure so systemd marks the unit failed (visible in
#    list-units / journal, and available to a future OnFailure= hook).
if digest_ok; then
  notify-send -a news-digest "News digest ($MODE) ready" "$(basename "$OUT") — $(stat -c%s "$OUT") bytes" 2>/dev/null || true
  echo "RESULT: success — $OUT"
  RC=0
else
  notify-send -a news-digest -u critical "News digest ($MODE) FAILED" "No complete digest at $(basename "$OUT"). See $LOG" 2>/dev/null || true
  echo "RESULT: FAILURE — no complete digest at $OUT"
  RC=1
fi

echo "════════ $(date '+%F %T') END mode=$MODE ════════"
exit $RC
