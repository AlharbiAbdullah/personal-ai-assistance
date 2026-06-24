#!/bin/bash
# rai maintenance runner (UBUNTU) — SOLE COORDINATOR + SOLE WRITER since
# 2026-06-13. Full design in 03-rai/SYNC-ARCHITECTURE.md.
#
# The Mac no longer runs any scheduler of its own (its launchd job, sleepwatcher
# and ~/.wakeup were removed). It is a passive source + replica reached over
# Tailscale SSH (`ssh mac`). This box is the ONLY machine that writes origin, so
# the old two-writer rebase war is gone — origin only ever moves when this runs.
#
# Pipeline (headless `claude -p` for the two intelligent steps):
#   0. git pull --rebase origin       defence + transition catch-up; steady-state
#                                      no-op since nobody else pushes origin.
#   1. capture_mac                     ssh mac → snapshot its churn into a commit,
#                                      `git fetch mac main`, merge it in (-X ours).
#                                      Mac asleep/unreachable → log + skip.
#   2. merge-collisions  (claude)      fold any durably-backed-up collider files.
#   3. process-sessions  (claude)      drain BOTH machines' pending queue → ChromaDB
#                                      (this box is the sole ChromaDB writer).
#   4. git-commit + push (claude)      group churn into logical commits → origin.
#   5. refresh_mac                     ssh mac → fast-forward the Mac to origin.
#
# Scheduled by systemd user timer rai-maintenance.timer (04/10/16/22:00). Logs +
# lock live in ~/.local/state/rai-maintenance/ — OUTSIDE the repo, so a run never
# commits or rebases its own log. The Mac is captured opportunistically — whatever
# it has whenever this box reaches it; if it is asleep the run still does the rest.
#
# Env:  NO_LOCK=1    skip the overlap lock (manual debugging)
#       SYNC_ONLY=1  do the git sync only (pull + capture_mac + refresh_mac),
#                    skip the three claude steps — fast plumbing check.

set -uo pipefail
export PATH="$HOME/.local/bin:/usr/local/bin:/usr/bin:/bin:$PATH"

CLAUDE="$HOME/.local/bin/claude"
HELM="$HOME/helm"
SCHED="$HELM/03-rai/skills/rai/scheduled"
STATE="$HOME/.local/state/rai-maintenance"                  # logs + lock OUTSIDE the repo
MAC_REMOTE="mac"                                            # git remote (mac:helm over ssh)
MAC_SSH="ssh -o BatchMode=yes -o ConnectTimeout=15 mac"     # Host mac in ~/.ssh/config
MAC_SYNC='bash ~/helm/03-rai/skills/rai/scheduled/mac-sync.sh'
mkdir -p "$STATE/logs"
LOG="$STATE/logs/$(date +%Y-%m-%d-%H%M)-maintenance.log"
exec >>"$LOG" 2>&1

echo "════════ $(date '+%F %T') START maintenance (ubuntu coordinator) ════════"

# Overlap lock — atomic mkdir; clear stale locks older than 60 min
LOCK="$STATE/.lock"
if [ "${NO_LOCK:-0}" != "1" ]; then
  if [ -d "$LOCK" ]; then
    AGE=$(( $(date +%s) - $(stat -c%Y "$LOCK" 2>/dev/null || echo 0) ))
    if [ "$AGE" -lt 3600 ]; then
      echo "Another run holds the lock (${AGE}s old) — skipping."; exit 0
    fi
    echo "Stale lock (${AGE}s old) — clearing."; rmdir "$LOCK" 2>/dev/null || true
  fi
  mkdir "$LOCK" 2>/dev/null || { echo "Lost lock race — skipping."; exit 0; }
  trap 'rmdir "$LOCK" 2>/dev/null' EXIT
fi

# News-run guard — same box runs the digest; never drain/commit mid-digest
if pgrep -f "claude --chrome" >/dev/null 2>&1; then
  echo "News run in progress (claude --chrome live) — skipping."; exit 0
fi

# ── git self-healing (unattended — every recoverable state recovers HERE) ──────
# Unchanged from the two-writer era except the integration SOURCE: step 1 now
# merges the Mac over SSH instead of both boxes racing origin. The three heal
# layers + durable collision backups are kept verbatim — they still protect the
# origin pull and the Mac merge. Backups go to a DURABLE dir (not /tmp) and are
# folded back by the merge-collisions claude step, then deleted.
COLLISION_ROOT="$HOME/.local/state/helm-pull-collisions"
COLLISION_BACKUP="$COLLISION_ROOT/$(date +%Y%m%d-%H%M%S)"

backup_path() {  # backup_path REPO_RELATIVE_PATH
  mkdir -p "$COLLISION_BACKUP/$(dirname "$1")"
  cp "$HELM/$1" "$COLLISION_BACKUP/$1"
}

self_heal_git_state() {
  if [ -d "$HELM/.git/rebase-merge" ] || [ -d "$HELM/.git/rebase-apply" ]; then
    echo "self-heal: aborting dead rebase"; git -C "$HELM" rebase --abort || true
  fi
  if [ -f "$HELM/.git/MERGE_HEAD" ]; then
    echo "self-heal: aborting dead merge"; git -C "$HELM" merge --abort || true
  fi
  if [ -f "$HELM/.git/CHERRY_PICK_HEAD" ]; then
    echo "self-heal: aborting dead cherry-pick"; git -C "$HELM" cherry-pick --abort || true
  fi
  local p
  while IFS= read -r p; do
    [ -z "$p" ] && continue
    if [ -e "$HELM/$p" ]; then
      backup_path "$p"
      echo "self-heal: backed up conflicted $p -> $COLLISION_BACKUP/$p"
    fi
    git -C "$HELM" restore --staged --worktree --source=HEAD -- "$p" 2>/dev/null \
      || { git -C "$HELM" rm --cached -q -- "$p" 2>/dev/null || true; rm -f "$HELM/$p"; }
  done < <(git -C "$HELM" diff --name-only --diff-filter=U)
}

resolve_untracked_collisions() {  # incoming tracked path exists locally as untracked
  local ref="${1:-origin/main}"
  git -C "$HELM" fetch origin main || return 1
  local p
  while IFS= read -r p; do
    [ -e "$HELM/$p" ] || continue
    git -C "$HELM" ls-files --error-unmatch "$p" >/dev/null 2>&1 && continue   # tracked → autostash handles it
    if git -C "$HELM" show "$ref:$p" 2>/dev/null | cmp -s - "$HELM/$p"; then
      rm -f "$HELM/$p"
      echo "collision (identical): dropped local untracked $p"
    else
      backup_path "$p" && rm -f "$HELM/$p"
      echo "collision (divergent): backed up local untracked $p -> $COLLISION_BACKUP/$p"
    fi
  done < <(git -C "$HELM" diff --name-only HEAD "$ref")
}

heal_autostash_conflicts() {
  local tries=0 p
  while git -C "$HELM" diff --name-only --diff-filter=U | grep -q .; do
    tries=$((tries+1))
    if [ "$tries" -gt 3 ]; then
      echo "ERROR: unmerged paths survived 3 heal passes"; return 1
    fi
    echo "self-heal: conflicted autostash pop — resolving (pass $tries, disk side wins)"
    while IFS= read -r p; do
      [ -z "$p" ] && continue
      git -C "$HELM" checkout --theirs -- "$p" 2>/dev/null || true  # delete/modify: keep disk copy
      git -C "$HELM" add -A -- "$p" 2>/dev/null || true             # index.lock race → next pass
    done < <(git -C "$HELM" diff --name-only --diff-filter=U)
    sleep 2
  done
  if [ "$tries" -gt 0 ] && git -C "$HELM" stash list | head -1 | grep -q ': autostash$'; then
    echo "self-heal: dropping conflicted autostash entry (content resolved into tree)"
    git -C "$HELM" stash drop 'stash@{0}' || true
  fi
  return 0
}

# Linux is the SOLE writer to origin, so origin/main is always an ancestor of
# local main — there is never local work to replay onto it. Use fetch + ff-only,
# not `pull --rebase`. The rebase form was the chronic jam: any run that died
# before its push (step 4) left an unpushed merge; the next run's rebase then
# tried to REPLAY the wip(mac) churn commits onto origin and choked on
# `Cannot merge binary files` in ChromaDB, leaving a half-done rebase that
# poisoned every following run (detached HEAD + UU conflicts). ff-only can never
# do that — it is a no-op in steady state and, on the anomalous diverged-origin
# case, fails cleanly (no half-rebase) and lets the retry/abort path call a human.
do_pull() {
  git -C "$HELM" fetch origin main || return 1
  git -C "$HELM" merge --ff-only FETCH_HEAD
}

# drop_stale_autostashes: an aborted rebase orphans its --autostash entry, which
# then lingers in `git stash list` forever. These are git temp-state, not records
# (their content was already applied to the tree), so drop any `autostash` entry
# older than 1h — a current run's own autostash is younger, so it is never touched.
# NAMED/manual stashes are always kept.
drop_stale_autostashes() {
  local cutoff=$(( $(date +%s) - 3600 )) sel n=0
  for _ in $(seq 1 100); do
    sel=$(git -C "$HELM" stash list --format='%gd %ct %gs' | awk -v c="$cutoff" '$3=="autostash" && $2<c {print $1; exit}')
    [ -z "$sel" ] && break
    git -C "$HELM" stash drop "$sel" >/dev/null 2>&1 && n=$((n+1)) || break
  done
  [ "$n" -gt 0 ] && echo "tidy: dropped $n orphaned autostash entries (named stashes kept)"
}

# ── Mac over Tailscale SSH ─────────────────────────────────────────────────────
# capture_mac: commit the Mac's churn (so there is something to fetch), fetch it,
# merge it into this tree. Returns 1 (and the run continues Mac-less) if the Mac
# is unreachable — a sleeping laptop is captured next run it is awake for.
capture_mac() {
  if ! $MAC_SSH 'true' 2>/dev/null; then
    echo "capture_mac: Mac unreachable (asleep?) — proceeding without its churn this run."
    return 1
  fi
  echo "capture_mac: Mac reachable — snapshotting its churn over SSH"
  $MAC_SSH "$MAC_SYNC commit" 2>&1 || echo "WARN: mac-sync commit returned nonzero"
  if ! git -C "$HELM" fetch "$MAC_REMOTE" main 2>&1; then
    echo "WARN: git fetch $MAC_REMOTE failed — skipping Mac merge this run."; return 1
  fi
  echo "capture_mac: merging $MAC_REMOTE/main (-X ours on conflict; autostash for local churn)"
  # -X ours: on a conflict keep LINUX's side. Critical for the binary ChromaDB —
  # Linux is its sole writer, so the Mac's copy is always stale and must never win.
  # Append-only logs still union via .gitattributes; the autostash pop heals below.
  git -C "$HELM" merge -X ours --autostash --no-edit "$MAC_REMOTE/main" 2>&1 || true
  if ! heal_autostash_conflicts; then
    echo "ERROR: Mac merge left unmerged paths after 3 heal passes."
    notify-send -a rai-maintenance -u critical "Rai maintenance" "Mac merge conflict unresolved — see $LOG" 2>/dev/null || true
    return 1
  fi
  return 0
}

# refresh_mac: fast-forward the Mac to origin AFTER this box has pushed, so the
# Mac picks up the drained ChromaDB + merged memory. Best-effort.
refresh_mac() {
  if ! $MAC_SSH 'true' 2>/dev/null; then
    echo "refresh_mac: Mac unreachable — it self-refreshes on the next run it is awake for."
    return 0
  fi
  echo "refresh_mac: fast-forwarding the Mac to origin/main over SSH"
  local rrc=0
  $MAC_SSH "$MAC_SYNC refresh" 2>&1 || rrc=$?

  # ChromaDB is gitignored since 2026-06-15, so it no longer rides along in git.
  # Linux is its SOLE writer; mirror it to the Mac out-of-band so the Mac's
  # read-replica recall stays current. Safe here: refresh_mac runs after
  # process-sessions (step 3), so Linux's store is quiescent. Best-effort.
  local CDB="03-rai/semantic-memory/chromadb"
  if [ -d "$HELM/$CDB" ]; then
    if rsync -a --delete -e "ssh -o BatchMode=yes -o ConnectTimeout=15" \
         "$HELM/$CDB/" "mac:helm/$CDB/" 2>&1; then
      echo "refresh_mac: ChromaDB mirrored to Mac via rsync"
    else
      echo "refresh_mac: WARN — ChromaDB rsync to Mac failed (Mac keeps prior copy)"
    fi
  fi

  # The Mac can't fetch GitHub (keychain), so its origin/main ref would freeze and
  # `git status` on the Mac would show a bogus, ever-growing "ahead of origin".
  # Propagate THIS box's real origin SHA so the Mac's view of GitHub stays honest.
  local osha; osha=$(git -C "$HELM" rev-parse origin/main 2>/dev/null)
  [ -n "$osha" ] && $MAC_SSH "git -C ~/helm update-ref refs/remotes/origin/main $osha" 2>/dev/null || true

  # VERIFY the refresh actually LANDED — don't trust the exit code alone. The Mac
  # pulls THIS box's main over SSH, so a landed refresh leaves Mac HEAD == this
  # box's HEAD. Comparing against local HEAD (not origin/main) is the right
  # invariant in SYNC_ONLY too, where origin hasn't been pushed yet. A silent miss
  # (the untracked-collision abort, 2026-06-14) left the Mac stale for days while
  # every run logged rc=0; surface it loudly so it can never be invisible again.
  local lhead mhead
  lhead=$(git -C "$HELM" rev-parse HEAD 2>/dev/null)
  mhead=$($MAC_SSH "git -C ~/helm rev-parse HEAD" 2>/dev/null)
  if [ -n "$lhead" ] && [ "$mhead" = "$lhead" ]; then
    echo "refresh_mac: Mac is current @ ${mhead:0:10}"
    return 0
  fi
  echo "refresh_mac: WARN — Mac did NOT reach this box's HEAD (Mac=${mhead:0:10}, linux=${lhead:0:10}, mac-sync rc=$rrc). Mac is STALE; self-heals on wake/next run."
  notify-send -a rai-maintenance -u normal "Rai sync: Mac STALE" "refresh_mac did not land (rc=$rrc) — Mac ${mhead:0:10} != linux ${lhead:0:10} — see $LOG" 2>/dev/null || true
  return 1
}

# Ensure the Mac git remote exists (idempotent; first install or fresh clone).
git -C "$HELM" remote get-url "$MAC_REMOTE" >/dev/null 2>&1 || {
  echo "setup: adding git remote $MAC_REMOTE -> mac:helm"
  git -C "$HELM" remote add "$MAC_REMOTE" mac:helm
}

# ── Step 0 — origin defence/transition pull ────────────────────────────────────
self_heal_git_state
resolve_untracked_collisions || echo "WARN: fetch failed — attempting pull anyway."
if ! do_pull; then
  echo "pull failed — re-running self-heal + collision pass, then one retry."
  self_heal_git_state
  resolve_untracked_collisions || true
  if ! do_pull; then
    echo "ERROR: pull --rebase failed twice — needs a human. Aborting run."
    notify-send -a rai-maintenance -u critical "Rai maintenance FAILED" "pull --rebase failed twice — see $LOG" 2>/dev/null || true
    exit 1
  fi
fi
if ! heal_autostash_conflicts; then
  echo "ERROR: unmerged files remain — refusing to run steps on a conflicted tree."
  notify-send -a rai-maintenance -u critical "Rai maintenance FAILED" "autostash conflicts unresolved — see $LOG" 2>/dev/null || true
  exit 1
fi

drop_stale_autostashes   # tidy orphaned rebase autostashes (git clutter, not records)

# ── Step 1 — capture the Mac's churn over SSH ──────────────────────────────────
capture_mac || true

# SYNC_ONLY — fast plumbing check: refresh the Mac (to current origin) and stop
# before the expensive claude steps. Leaves any merged churn uncommitted for the
# next real run.
if [ "${SYNC_ONLY:-0}" = "1" ]; then
  refresh_mac; RC5=$?
  echo "════════ $(date '+%F %T') END (SYNC_ONLY) rc5=$RC5 ════════"
  exit "$RC5"
fi

# run_step NAME CAP_MINUTES PROMPT [allowedTools...]
run_step() {
  local name="$1" cap_min="$2" prompt="$3"; shift 3
  echo "──── STEP $name start $(date '+%T') (cap ${cap_min}m) ────"
  ( cd "$HELM" && timeout --kill-after=30 "${cap_min}m" "$CLAUDE" -p "$prompt" --allowedTools "$@" )
  local rc=$?
  [ "$rc" -eq 124 ] && echo "STEP $name TIMED OUT after ${cap_min}m."
  echo "──── STEP $name end $(date '+%T') rc=$rc ────"
  return $rc
}

# ── Step 2 — fold collision backups back into the vault ────────────────────────
RC0=0
if [ -n "$(find "$COLLISION_ROOT" -type f 2>/dev/null | head -c1)" ]; then
  P0="Collision backups live under $COLLISION_ROOT/<timestamp>/<repo-relative-path> — files the vault sync set aside instead of clobbering. For each backed-up file: read it and the corresponding live file at ~/helm/<repo-relative-path>. If the backup contains content the live file lacks, merge it in — append-only logs (memory .md / .jsonl) get the union of entries in time order; state/config files keep the more complete or newer version. Strip any git conflict markers (<<<<<<< / ======= / >>>>>>>) — keep both sides' content, never the markers. If the live file already covers the backup, change nothing. Then delete the processed backup file and remove empty directories under $COLLISION_ROOT. Fully unattended — never ask for confirmation."
  run_step "merge-collisions" 15 "$P0" \
    "Read" "Write" "Edit" "Glob" "Grep" \
    "Bash(ls *)" "Bash(find *)" "Bash(diff *)" "Bash(cmp *)" "Bash(rm *)" "Bash(rmdir *)"
  RC0=$?
  [ "$RC0" -ne 0 ] && echo "WARN: merge-collisions rc=$RC0 — backups left in place for next run."
fi

# ── Step 3 — drain pending sessions (this box is the sole ChromaDB writer) ─────
P1="Read ~/helm/03-rai/skills/rai/process-sessions.md and execute it exactly as written, fully unattended — never ask for confirmation. If there are no pending sessions, say so and stop."
run_step "process-sessions" 30 "$P1" \
  "Bash(~/helm/03-rai/semantic-memory/scripts/py-chroma.sh *)" \
  "Bash(python3 *)" "Bash(ls *)" "Bash(mv *)" "Bash(grep *)" "Bash(wc *)" \
  "Read" "Write" "Edit" "Glob" "Grep"
RC1=$?
[ "$RC1" -ne 0 ] && echo "WARN: process-sessions rc=$RC1 — continuing to commit step anyway."

# ── Step 4 — commit + push (sole writer to origin) ─────────────────────────────
P2="Read ~/helm/03-rai/skills/git/commit.md and execute it on ~/helm exactly as written: group the working-tree changes into logical commits, stage files explicitly, commit, then pull --rebase and push to origin. Fully unattended — never ask for confirmation. If the tree is clean but the branch is ahead of origin, still pull --rebase and push. If the tree is clean and nothing is ahead, say so and stop."
run_step "git-commit" 30 "$P2" \
  "Bash(git *)" "Read" "Glob" "Grep"
RC2=$?

# ── Step 5 — fast-forward the Mac to the freshly-pushed origin ─────────────────
refresh_mac; RC5=$?

echo "════════ $(date '+%F %T') END rc0=$RC0 rc1=$RC1 rc2=$RC2 rc5=$RC5 ════════"
[ "$RC5" -ne 0 ] && echo "════════ NOTE: Mac is STALE (refresh_mac rc=$RC5) — see WARN above ════════"
