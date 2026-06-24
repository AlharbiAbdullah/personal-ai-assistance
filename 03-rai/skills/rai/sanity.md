---
name: sanity
description: End-to-end healthcheck for the brain. Verifies data safety, environment, ChromaDB, pipeline, configuration, vault + identity, memory index, hygiene, algorithm + agents, skills deep-structure + hook firing, work state + protection. A PASS certifies the entire Rai system works as intended, not just that files exist. Use when the user says "/sanity", "check the brain", "run a healthcheck", or suspects something is broken.
allowed-tools: Bash, Read, Glob, Grep, Edit, Write
---

# /sanity - Brain End-to-End Healthcheck

Verify every important touchpoint of the brain system in one pass. Report a pass/fail table with evidence. Surface regressions fast.

## Philosophy

The brain is the user's most important folder. It cannot be silently lost, corrupted, or stop learning. This skill enforces that by tiered checks.

| Tier | Name | What breaks if it fails |
|------|------|-------------------------|
| A | Data safety | A laptop crash wipes work that was never pushed |
| B | Environment | Python/chromadb can't be reached at all |
| C | ChromaDB integrity | Memory stops being written or read |
| D | Pipeline health | Capture or processing pipeline has stalled |
| E | Configuration | Invalid JSON, missing hooks, broken symlinks |
| F | Vault + identity | Folders, templates, or identity files gone |
| G | Memory index | The `MEMORY.md` auto-memory system is wrong |
| H | Hygiene | Orphaned or duplicated trees masking real state |
| I | Algorithm + agents | Reasoning spine missing; agents unlistable |
| J | Skills deep + hook behavior | Skill routing breaks; hooks silently stop firing |
| K | Work state + protection | META/counts drift; secret scanner or MCP broken |

## Arguments

| Argument | Description |
|----------|-------------|
| (none) | Full healthcheck (~70s) |
| `--quick` | Skip slow checks: C4 (write round-trip), C5 (semantic query), E4 (symlink tree scan), J4 (hook firing recency), K1 (META.yaml walk). Target: under 30s. |
| `--fix` | Surface fixes but do not apply them |
| `--baseline` | Update `.sanity-baseline.json` with current counts as the new baseline |

## Portability

All paths use `$HOME`. The skill works on macOS and Linux without edits (`$HOME` resolves to the correct user home on each platform). The `py-chroma.sh` wrapper handles the chromadb environment on both.

## Instructions

Run each check as an independent bash block. Collect results into a final table. **Never fail silently** — if a check raises, report it in the table as FAIL with the error as evidence.

Always capture evidence (counts, paths, timestamps). A PASS without evidence is not acceptable.

---

## TIER A — Data Safety

### Check A1: Git backup status

```bash
cd "$HOME/helm" || exit 1
uncommitted=$(git status --porcelain | wc -l | tr -d ' ')
unpushed=$(git log --oneline @{u}..HEAD 2>/dev/null | wc -l | tr -d ' ')
last_commit_epoch=$(git log -1 --format=%ct 2>/dev/null || echo 0)
now=$(date +%s)
days_since=$(( (now - last_commit_epoch) / 86400 ))
remote_ok=$(git ls-remote --exit-code origin HEAD >/dev/null 2>&1 && echo "yes" || echo "no")
echo "uncommitted: $uncommitted"
echo "unpushed: $unpushed"
echo "days_since_commit: $days_since"
echo "remote_reachable: $remote_ok"
```

- PASS: `unpushed == 0`, `days_since_commit < 7`, `remote_reachable == yes`.
- WARN: `uncommitted > 50` (stale work), `unpushed > 0` (commits only on this machine), `days_since_commit >= 7`.
- FAIL: `remote_reachable == no` (no backup target).

### Check A2: File baselines (drift detection)

```bash
BASE="$HOME/helm/03-rai/.sanity-baseline.json"
md_count=$(find "$HOME/helm" -type f -name "*.md" ! -path "*/.git/*" ! -path "*/node_modules/*" 2>/dev/null | wc -l | tr -d ' ')
pending_count=$(find "$HOME/helm/03-rai/semantic-memory/pending" -type f -name "*.json" 2>/dev/null | wc -l | tr -d ' ')
chroma_bytes=$(du -sk "$HOME/helm/03-rai/semantic-memory/chromadb" 2>/dev/null | awk '{print $1*1024}')
echo "md_count: $md_count"
echo "pending_count: $pending_count"
echo "chromadb_bytes: $chroma_bytes"
if [ -f "$BASE" ]; then
  python3 -c "
import json, os
base = json.load(open(os.path.expanduser('$BASE')))
now = {'md_count': $md_count, 'chromadb_bytes': $chroma_bytes}
for k, v in now.items():
    old = base.get(k, 0)
    if old == 0:
        continue
    delta_pct = (v - old) / old * 100
    flag = 'DROP' if delta_pct < -5 else ('OK' if delta_pct >= 0 else 'minor')
    print(f'  {k}: {old} -> {v} ({delta_pct:+.1f}%) [{flag}]')
"
else
  echo "  no baseline yet. Run /sanity --baseline to create."
fi
```

- PASS: no metric dropped by more than 5% since last baseline.
- WARN: any metric dropped 5-20% (possible accidental deletion).
- FAIL: any metric dropped more than 20% (major data loss signal).
- With `--baseline`, write the current values to `.sanity-baseline.json` instead of comparing.

---

## TIER B — Environment

### Check B1: Python + chromadb environment

```bash
"$HOME/helm/03-rai/semantic-memory/scripts/py-chroma.sh" -c "
import chromadb
print('chromadb', chromadb.__version__)
" 2>&1 | tail -3
```

- PASS: prints `chromadb <version>`.
- FAIL: ModuleNotFoundError, wrapper missing, or non-zero exit.

### Check B2: py-chroma.sh wrapper executable

```bash
[ -x "$HOME/helm/03-rai/semantic-memory/scripts/py-chroma.sh" ] && echo "wrapper: executable" || echo "wrapper: NOT executable"
```

- PASS: `executable`. FAIL: not executable (fix: `chmod +x`).

---

## TIER C — ChromaDB Integrity

### Check C1: Expected collections present

```bash
"$HOME/helm/03-rai/semantic-memory/scripts/py-chroma.sh" -c "
import chromadb
from pathlib import Path
c = chromadb.PersistentClient(path=str(Path.home() / 'helm/03-rai/semantic-memory/chromadb'))
names = sorted(x.name for x in c.list_collections())
expected = {'memories'}
missing = expected - set(names)
print('collections:', names)
print('missing:', sorted(missing) if missing else 'none')
" 2>&1 | tail -5
```

- PASS: `memories` collection present (only one we keep post-Phase-0 cleanup).
- FAIL: any expected collection missing.

### Check C2: ChromaDB populated and date range fresh

```bash
"$HOME/helm/03-rai/semantic-memory/scripts/py-chroma.sh" -c "
import chromadb
from pathlib import Path
client = chromadb.PersistentClient(path=str(Path.home() / 'helm/03-rai/semantic-memory/chromadb'))
col = client.get_collection('memories')
result = col.get(include=['metadatas'])
dates = sorted(set(m.get('date','') for m in result['metadatas']))
print('total:', col.count())
print('range:', dates[0] if dates else '?', '->', dates[-1] if dates else '?')
print('unique_dates:', len(dates))
" 2>&1 | tail -5
```

- PASS: count > 0, most recent date within the last 7 days.
- WARN: most recent date 7-14 days old.
- FAIL: empty, or most recent date > 14 days old.

### Check C3: Monthly coverage

```bash
"$HOME/helm/03-rai/semantic-memory/scripts/py-chroma.sh" -c "
import chromadb
from collections import Counter
from pathlib import Path
client = chromadb.PersistentClient(path=str(Path.home() / 'helm/03-rai/semantic-memory/chromadb'))
col = client.get_collection('memories')
result = col.get(include=['metadatas'])
by_month = Counter(m.get('date','')[:7] for m in result['metadatas'])
for ym in sorted(by_month):
    print(f'  {ym}: {by_month[ym]}')
" 2>&1 | tail -20
```

- PASS: each recent month has >= 5 entries.
- WARN: any month with < 5 entries (confirm with user if vacation).

### Check C4: ChromaDB write → read → delete round trip

Skip when `--quick` is passed.

```bash
"$HOME/helm/03-rai/semantic-memory/scripts/py-chroma.sh" -c "
import chromadb, uuid
from pathlib import Path
client = chromadb.PersistentClient(path=str(Path.home() / 'helm/03-rai/semantic-memory/chromadb'))
col = client.get_collection('memories')
probe_id = f'sanity-probe-{uuid.uuid4()}'
try:
    col.add(ids=[probe_id], documents=['sanity check probe'], metadatas=[{'date': '1970-01-01', 'type': 'probe'}])
    got = col.get(ids=[probe_id])
    assert got['ids'] == [probe_id], 'probe missing after write'
    col.delete(ids=[probe_id])
    gone = col.get(ids=[probe_id])
    assert gone['ids'] == [], 'probe not deleted'
    print('round_trip: OK')
except Exception as e:
    print(f'round_trip: FAIL - {e}')
" 2>&1 | tail -3
```

- PASS: prints `round_trip: OK`.
- FAIL: any exception. Storage is broken — do not run `/process-sessions` until fixed.

### Check C5: history-recall semantic query

Skip when `--quick` is passed.

```bash
"$HOME/helm/03-rai/semantic-memory/scripts/py-chroma.sh" -c "
import chromadb
from pathlib import Path
client = chromadb.PersistentClient(path=str(Path.home() / 'helm/03-rai/semantic-memory/chromadb'))
col = client.get_collection('memories')
r = col.query(query_texts=['brain vault sessions'], n_results=3, include=['metadatas','distances'])
for i, meta in enumerate(r['metadatas'][0]):
    sim = 1 - r['distances'][0][i]
    print(f\"  {meta.get('date','?')} | {meta.get('type','?')} | sim={sim:.2f}\")
" 2>&1 | tail -5
```

- PASS: 3 results, top similarity > 0.3.
- WARN: 3 results but top similarity < 0.3 (embedding model may have changed).
- FAIL: error or empty.

### Check C6: ChromaDB folder writable

```bash
chroma_dir="$HOME/helm/03-rai/semantic-memory/chromadb"
if [ -w "$chroma_dir" ] && [ -x "$chroma_dir" ]; then
  echo "chroma_perms: OK ($(ls -ld "$chroma_dir" | awk '{print $1, $3, $4}'))"
else
  echo "chroma_perms: FAIL — folder not writable by current user"
  ls -ld "$chroma_dir"
fi
```

- PASS: prints `chroma_perms: OK ...`.
- FAIL: folder is read-only or wrong owner. `/process-sessions` will silently lose writes until fixed.

---

## TIER D — Pipeline Health

### Check D1: Pending queue depth

```bash
pending=$(find "$HOME/helm/03-rai/semantic-memory/pending" -type f -name "*.json" 2>/dev/null | wc -l | tr -d ' ')
summaries=$(find "$HOME/helm/03-rai/semantic-memory/pending-summaries" -type f -name "*.json" 2>/dev/null | wc -l | tr -d ' ')
echo "pending: $pending"
echo "pending-summaries: $summaries"
```

- PASS: `pending < 10`, `summaries == 0`.
- WARN: `pending >= 10` (run `/process-sessions`).
- FAIL: `summaries > 0` (storage step stalled between summarization and ChromaDB insert).

### Check D1b: store_to_chromadb.py exists and is executable

```bash
script="$HOME/helm/03-rai/hooks/scripts/store_to_chromadb.py"
if [ -f "$script" ] && [ -r "$script" ]; then
  echo "store_to_chromadb: OK"
else
  echo "store_to_chromadb: FAIL — script missing or unreadable at $script"
fi
```

- PASS: prints `store_to_chromadb: OK`. `/process-sessions` can drain the pending queue.
- FAIL: script missing. The pending queue will accumulate until restored.

### Check D2: Session capture is live

```bash
# BSD stat (mac) and GNU stat (linux) differ. Use python for portable mtime.
python3 - <<'PY'
import os, time
from pathlib import Path
pend = Path.home() / 'helm/03-rai/semantic-memory/pending'
files = sorted(pend.glob('*.json'), key=lambda p: p.stat().st_mtime, reverse=True)
if not files:
    print('no pending sessions')
else:
    newest = files[0]
    age_h = (time.time() - newest.stat().st_mtime) / 3600
    print(f'newest: {newest.name}')
    print(f'age_hours: {age_h:.1f}')
PY
```

- PASS: at least one pending file written in the last 48h.
- WARN: newest is 48-168h old (did you use a laptop this week?).
- FAIL: > 168h or no pending files at all (SessionEnd hook is not firing).

### Check D3: STATE + RELATIONSHIP writes fresh

```bash
python3 - <<'PY'
import time
from pathlib import Path
home = Path.home()
for label, glob in [
    ('STATE', home / 'helm/03-rai/memory/state/tab-titles'),
    ('RELATIONSHIP', home / 'helm/03-rai/memory/relationship'),
]:
    if not glob.exists():
        print(f'{label}: MISSING folder')
        continue
    pattern = '*.json' if label == 'STATE' else '*/*.md'
    files = list(glob.glob(pattern))
    if not files:
        print(f'{label}: no files')
        continue
    newest = max(files, key=lambda p: p.stat().st_mtime)
    age_h = (time.time() - newest.stat().st_mtime) / 3600
    print(f'{label}: newest={newest.name}, age_hours={age_h:.1f}')
PY
```

- PASS: most recent write within 48h for both.
- FAIL: stale > 7 days (hooks `relationship-memory.py` or `save-memory.py` are broken).

### Check D4: SessionStart hook output

```bash
"$HOME/helm/03-rai/semantic-memory/scripts/py-chroma.sh" \
  "$HOME/helm/03-rai/hooks/session-start.py" 2>&1 | tail -30
```

- PASS: output includes `## Who`, `## Mission`, and `## Recent Memory` sections.
- FAIL: blank output, timeout, or any section missing.

---

## TIER E — Configuration Integrity

### Check E1: JSON configs are valid

```bash
python3 - <<'PY'
import json, sys
from pathlib import Path
home = Path.home()
targets = [
    home / '.claude/settings.json',
    home / '.claude/mcp.json',
    home / 'helm/03-rai/config/settings.json',
    home / 'helm/03-rai/config/mcp.json',
]
fail = 0
for p in targets:
    if not p.exists():
        print(f'  MISSING: {p}')
        fail += 1
        continue
    try:
        json.loads(p.read_text())
        print(f'  OK: {p.name} ({p.parent.name})')
    except Exception as e:
        print(f'  INVALID JSON: {p} — {e}')
        fail += 1
print(f'invalid_or_missing: {fail}')
PY
```

- PASS: all 0 failures (each file exists and parses).
- FAIL: any invalid or missing.

### Check E2: Hooks registered + scripts exist + executable

```bash
python3 - <<'PY'
import json, os
from pathlib import Path
home = Path.home()
cfg = json.loads((home / '.claude/settings.json').read_text())
total = missing = not_exec = 0
problems = []
for event, groups in cfg.get('hooks', {}).items():
    for g in groups:
        for h in g.get('hooks', []):
            total += 1
            cmd = h.get('command','')
            # first absolute path token is the script
            for tok in cmd.split():
                if tok.startswith('/') and tok.endswith(('.py', '.sh')):
                    p = Path(tok)
                    if not p.exists():
                        missing += 1
                        problems.append(('missing', event, tok))
                    elif not os.access(p, os.X_OK) and tok.endswith('.sh'):
                        not_exec += 1
                        problems.append(('not_exec', event, tok))
                    break
print(f'hooks_total: {total}')
print(f'hooks_missing: {missing}')
print(f'hooks_not_executable: {not_exec}')
for p in problems[:5]:
    print(' ', p)
PY
```

- PASS: `hooks_missing == 0` and `hooks_not_executable == 0`.
- FAIL: any script missing or `.sh` not executable.

### Check E3: `.claude/` symlinks resolve

```bash
python3 - <<'PY'
from pathlib import Path
home = Path.home()
expected = [
    ('agents', home / 'helm/03-rai/agents'),
    ('hooks', home / 'helm/03-rai/hooks'),
    ('memory', home / 'helm/03-rai/memory'),
    ('skills', home / 'helm/03-rai/skills'),
    ('CLAUDE.md', home / 'helm/03-rai/CLAUDE.md'),
    ('mcp.json', home / 'helm/03-rai/config/mcp.json'),
    ('settings.json', home / 'helm/03-rai/config/settings.json'),
    ('statusline.sh', home / 'helm/03-rai/config/statusline.sh'),
]
broken = wrong_target = not_a_link = 0
for name, want in expected:
    link = home / '.claude' / name
    if not link.is_symlink():
        if link.exists():
            print(f'  WARN: {name} is not a symlink (real file/dir exists)')
            not_a_link += 1
        else:
            print(f'  MISSING: {name}')
            broken += 1
        continue
    target = link.resolve()
    if not target.exists():
        print(f'  BROKEN: {name} -> {link.readlink()}')
        broken += 1
    elif target != want.resolve():
        print(f'  WRONG TARGET: {name} -> {target} (expected {want})')
        wrong_target += 1
    else:
        pass
print(f'broken: {broken}, wrong_target: {wrong_target}, not_a_link: {not_a_link}')
PY
```

- PASS: broken == 0, wrong_target == 0, not_a_link == 0.
- FAIL: any broken, wrong target, or replaced-by-real-file (source of truth compromised).

### Check E4: No broken symlinks in helm tree

Skip when `--quick` is passed.

```bash
# find dangling symlinks anywhere under helm/ (excludes .git and chromadb internals)
broken=$(find "$HOME/helm" \
  -path "*/.git" -prune -o \
  -path "*/chromadb" -prune -o \
  -path "*/node_modules" -prune -o \
  -type l ! -exec test -e {} \; -print 2>/dev/null)
if [ -z "$broken" ]; then
    echo "broken_symlinks: 0"
else
    echo "broken_symlinks: $(echo "$broken" | wc -l | tr -d ' ')"
    echo "$broken" | head -10
fi
```

- PASS: 0 broken symlinks.
- WARN: 1-3 (usually cross-machine paths; decide to remove).
- FAIL: > 3 (widespread corruption).

---

## TIER F — Vault Structure

### Check F1: Top-level folders exist

```bash
python3 - <<'PY'
from pathlib import Path
home = Path.home()
expected = ['00-landing', '01-inbox', '02-ana', '03-rai', '04-work',
            '05-projects', '06-learning', '07-reading', '08-bawaba', '09-ideas',
            '10-knowledge', '11-workflows', '12-system', '13-archive']
missing = [d for d in expected if not (home / 'helm' / d).is_dir()]
print(f'folders_expected: {len(expected)}')
print(f'folders_missing: {len(missing)}')
for d in missing:
    print(f'  MISSING: {d}')
PY
```

- PASS: all 14 folders present.
- FAIL: any missing.

### Check F2: Key templates present

```bash
python3 - <<'PY'
from pathlib import Path
home = Path.home()
templates_dir = home / 'helm/12-system/templates'
required = ['Capture.md', 'Plant.md', 'Insight Note.md', 'Learning.md', 'MOC.md']
if not templates_dir.is_dir():
    print('templates_dir: MISSING')
else:
    missing = [t for t in required if not (templates_dir / t).exists()]
    print(f'templates_required: {len(required)}')
    print(f'templates_missing: {len(missing)}')
    for t in missing:
        print(f'  MISSING: {t}')
PY
```

- PASS: all required templates present.
- WARN: 1-2 missing. FAIL: > 2 missing.

### Check F3: Key root files present

```bash
python3 - <<'PY'
from pathlib import Path
home = Path.home()
vault = home / 'helm'
required = ['CLAUDE.md']
index_path = vault / '.helm-index' / 'helm-index.md'
missing = [f for f in required if not (vault / f).exists()]
index_found = index_path.exists()
print(f'root_missing: {missing if missing else "none"}')
print(f'helm_index: {"found" if index_found else "MISSING"}')
PY
```

- PASS: `CLAUDE.md` and `.helm-index/helm-index.md` present.
- FAIL: any missing.

### Check F4: Skills reachable

```bash
total=$(ls "$HOME/.claude/skills/" 2>/dev/null | wc -l | tr -d ' ')
critical=0
[ -f "$HOME/.claude/skills/rai/sanity.md" ] && critical=$((critical+1))
[ -f "$HOME/.claude/skills/rai/process-sessions.md" ] && critical=$((critical+1))
[ -f "$HOME/.claude/skills/recall/history.md" ] && critical=$((critical+1))
echo "global_skills: $total"
echo "critical_skills: $critical/3"
```

- PASS: `critical_skills: 3/3`.
- FAIL: any critical skill missing.

### Check F5: Template integrity

Every template in `12-system/templates/` must start with `---` frontmatter.

```bash
bad=0
for t in ~/helm/12-system/templates/*.md; do
    first=$(head -1 "$t" 2>/dev/null)
    if [ "$first" != "---" ]; then
        echo "BAD: $t (first line: $first)"
        bad=$((bad+1))
    fi
done
total=$(ls ~/helm/12-system/templates/*.md 2>/dev/null | wc -l | tr -d ' ')
echo "templates: $total total, $bad with missing frontmatter"
```

- PASS: every template starts with `---`.
- FAIL: any template missing frontmatter.

### Check F6: Hook failure logs

Any recent stderr from hook scripts indicates a silent failure in the
brain's event loop.

```bash
log_dir=~/helm/03-rai/memory/learning/system
if [ -f "$log_dir/hook-perf.jsonl" ]; then
    recent_errors=$(tail -200 "$log_dir/hook-perf.jsonl" 2>/dev/null | grep -c '"status":"error"' || echo 0)
    echo "recent_hook_errors: $recent_errors"
    if [ "$recent_errors" -gt 0 ]; then
        echo "sample errors:"
        tail -200 "$log_dir/hook-perf.jsonl" | grep '"status":"error"' | tail -3
    fi
else
    echo "hook-perf.jsonl not found — hook logging may not be enabled"
fi
```

- PASS: `recent_hook_errors: 0`.
- WARN: 1–5 errors in the last 200 events.
- FAIL: 5+ errors, or the log file is missing when it should exist.

### Check F7: Identity files present and readable

Every `*.md` in `03-rai/identity/` and `02-ana/identity/` is auto-loaded
at SessionStart. Non-`.md` files (e.g. `security-patterns.yaml`) are
intentionally ignored by the loader. Sanity verifies the `.md` files
actually exist and are non-empty.

```bash
python3 - <<'PY'
from pathlib import Path
home = Path.home()
problems = []
for label, d in [('rai', home / 'helm/03-rai/identity'),
                 ('ana', home / 'helm/02-ana/identity')]:
    if not d.is_dir():
        problems.append(f'{label}: MISSING folder'); continue
    md_files = sorted(d.glob('*.md'))
    unreadable = [p.name for p in md_files if not p.is_file() or p.stat().st_size == 0]
    print(f'{label}: {len(md_files)} .md files')
    for name in unreadable:
        problems.append(f'{label}/{name}: unreadable or empty')
    non_md = [p.name for p in d.iterdir() if p.is_file() and p.suffix != '.md']
    if non_md:
        print(f'  (non-auto-loaded: {non_md})')
print(f'problems: {len(problems)}')
for p in problems:
    print(f'  {p}')
PY
```

- PASS: all `.md` files readable and non-empty.
- WARN: Rai identity < 4 `.md` files (core config: dai-identity, ai-steering-rules, response-format, coding-format) or John identity < 3 `.md` files.
- FAIL: any `.md` file unreadable or empty.

### Check F8: Identity cache coherence

`session-start.py` caches identity in `memory/state/identity-cache.json`
keyed by newest mtime across all identity files. If the cache's recorded
mtime doesn't match the actual newest mtime, SessionStart will reload
(self-healing), but a persistent drift signals a writer problem.

```bash
python3 - <<'PY'
import json
from pathlib import Path
home = Path.home()
cache = home / 'helm/03-rai/memory/state/identity-cache.json'
if not cache.exists():
    print('cache: MISSING (first-run state — OK)')
    raise SystemExit
try:
    data = json.loads(cache.read_text())
except Exception as e:
    print(f'cache: FAIL — unparseable ({e})'); raise SystemExit
recorded = data.get('max_mtime', 0)
files = []
for d in [home / 'helm/03-rai/identity', home / 'helm/02-ana/identity']:
    if d.is_dir():
        files.extend(p for p in d.glob('*.md') if p.is_file())
actual = max((p.stat().st_mtime for p in files), default=0)
drift_s = abs(actual - recorded)
listed = set(data.get('files', []))
actual_names = {str(p) for p in files}
missing = actual_names - listed
print(f'cache_mtime: recorded={recorded:.0f}, actual={actual:.0f}, drift={drift_s:.1f}s')
print(f'cache_files: {len(listed)}, actual: {len(actual_names)}')
if missing:
    print(f'  not in cache: {sorted(missing)[:3]}')
PY
```

- PASS: `drift_s <= 1`, cache `files:` matches filesystem.
- WARN: drift 1-60s (pending SessionStart refresh — self-healing).
- FAIL: drift > 60s persistent, or cache unparseable.

---

## TIER G — Memory Index

### Check G1: MEMORY.md integrity

```bash
python3 - <<'PY'
import re
from pathlib import Path
home = Path.home()
mem_dir = home / '.claude/projects/-Users-johndoe/memory'
index = mem_dir / 'MEMORY.md'
if not index.exists():
    # Fallback for Linux path
    for alt in home.glob('.claude/projects/*/memory/MEMORY.md'):
        index = alt
        mem_dir = alt.parent
        break
if not index.exists():
    print('MEMORY.md: MISSING')
else:
    lines = index.read_text().splitlines()
    print(f'lines: {len(lines)} (limit: 200)')
    refs = re.findall(r'\[[^\]]+\]\(([^)]+\.md)\)', index.read_text())
    missing = [r for r in refs if not (mem_dir / r).exists()]
    print(f'references: {len(refs)}')
    print(f'missing_refs: {len(missing)}')
    for m in missing[:5]:
        print(f'  MISSING: {m}')
PY
```

- PASS: `lines <= 200`, `missing_refs == 0`.
- WARN: `lines > 150` (approaching truncation limit).
- FAIL: MEMORY.md missing, or > 200 lines, or any referenced file missing.

---

## TIER H — Hygiene

### Check H1: Orphans and duplicates

```bash
# Real dir check that ignores symlinks
for p in "$HOME/helm/03-rai/archive" "$HOME/.claude/hooks"; do
    if [ -d "$p" ] && [ ! -L "$p" ]; then
        echo "ORPHAN: $p is a real directory (should not exist)"
    else
        echo "  clean: $p"
    fi
done
# Known underscore alias should not exist
[ -e "$HOME/helm/05_agent_brain" ] && echo "ORPHAN: 05_agent_brain alias exists" || echo "  clean: 05_agent_brain alias"
# Historical sessions count
count=$(ls "$HOME/helm/13-archive/historical-sessions/" 2>/dev/null | wc -l | tr -d ' ')
echo "  historical-sessions: $count"
```

- PASS: no orphan directories, no alias files.
- FAIL: any real directory where a symlink is expected (indicates broken setup, source of truth compromised).

---

## TIER I — Algorithm + Agents

The brain's reasoning spine. If the Algorithm spec is missing or
phase-tracking has stopped firing, every structured task is flying blind.
Agents need a valid MANIFEST or `Task(subagent_type: ...)` fails.

### Check I1: Algorithm `latest` pointer + spec file exists

`algorithm/latest` is either a symlink to the active version file OR a
plain text file containing the version filename (e.g. `v3.7.0.md`).
Both patterns are valid — resolve to the underlying spec file either way.

```bash
python3 - <<'PY'
from pathlib import Path
algo = Path.home() / 'helm/03-rai/algorithm'
latest = algo / 'latest'
if not latest.exists():
    print('algorithm: FAIL — latest missing'); raise SystemExit
if latest.is_symlink():
    spec = latest.resolve()
    via = 'symlink'
else:
    name = latest.read_text().strip()
    spec = algo / name
    via = f'pointer-file->{name}'
if not spec.exists():
    print(f'algorithm: FAIL — latest points to {spec.name} but file missing'); raise SystemExit
size = spec.stat().st_size
if size == 0:
    print(f'algorithm: FAIL — {spec.name} is empty'); raise SystemExit
print(f'algorithm: OK -> {spec.name} ({size} bytes, via {via})')
PY
```

- PASS: spec resolves (via symlink OR pointer file), non-empty.
- FAIL: missing, dangling, or 0 bytes.

### Check I2: Algorithm phase definitions + effort tiers present

Verify the spec actually contains the contract documented in `CLAUDE.md`:
7 phases and 5 effort tiers. Drift here means docs claim one thing and
spec says another — surface the divergence.

```bash
python3 - <<'PY'
from pathlib import Path
algo = Path.home() / 'helm/03-rai/algorithm'
latest = algo / 'latest'
if not latest.exists():
    print('spec: FAIL — latest missing'); raise SystemExit
spec = latest.resolve() if latest.is_symlink() else algo / latest.read_text().strip()
if not spec.exists():
    print(f'spec: FAIL — {spec.name} missing'); raise SystemExit
text = spec.read_text()
phases = ['OBSERVE', 'THINK', 'PLAN', 'BUILD', 'EXECUTE', 'VERIFY', 'LEARN']
tiers = ['Standard', 'Extended', 'Advanced', 'Deep', 'Comprehensive']
missing_phases = [p for p in phases if p not in text]
missing_tiers = [t for t in tiers if t not in text]
print(f'phases: {len(phases)-len(missing_phases)}/{len(phases)}')
print(f'tiers:  {len(tiers)-len(missing_tiers)}/{len(tiers)}')
if missing_phases: print(f'  missing phases: {missing_phases}')
if missing_tiers:  print(f'  missing tiers:  {missing_tiers}')
PY
```

- PASS: 7/7 phases and 5/5 tiers.
- WARN: 1-2 items missing (spec drift; review against `CLAUDE.md`).
- FAIL: 3+ items missing (spec corrupted or wrong version).

### Check I3: Algorithm state freshness

`algorithm-scan.py` writes a per-session state file at SessionEnd. If
nothing has been written recently, either no structured tasks have run
(ok) or the hook has stopped firing (not ok).

```bash
python3 - <<'PY'
import time
from pathlib import Path
d = Path.home() / 'helm/03-rai/memory/state/algorithms'
if not d.is_dir():
    print('algorithm_state: FAIL — folder missing'); raise SystemExit
files = list(d.glob('*.json'))
if not files:
    print('algorithm_state: WARN — no state files yet (new system or no structured tasks)')
    raise SystemExit
newest = max(files, key=lambda p: p.stat().st_mtime)
age_d = (time.time() - newest.stat().st_mtime) / 86400
print(f'algorithm_state: {len(files)} files, newest {newest.name}, age {age_d:.1f}d')
PY
```

- PASS: files exist, newest < 7 days old.
- WARN: 7-30d old (low structured-task usage, OR `algorithm-scan.py` has regressed).
- FAIL: > 30d old, or folder missing.

### Check I4: Agents frontmatter + MANIFEST sync

```bash
python3 - <<'PY'
import re
from pathlib import Path
d = Path.home() / 'helm/03-rai/agents'
files = sorted(p.stem for p in d.glob('*.md') if p.name != 'MANIFEST.md')
problems = []
for stem in files:
    body = (d / f'{stem}.md').read_text(encoding='utf-8', errors='replace')
    if not body.startswith('---'):
        problems.append(f'{stem}: no frontmatter'); continue
    m = re.search(r'^name:\s*([\w-]+)', body, re.M)
    if not m:
        problems.append(f'{stem}: no name field')
    elif m.group(1) != stem:
        problems.append(f'{stem}: name={m.group(1)} mismatches filename')
manifest = (d / 'MANIFEST.md')
if not manifest.exists():
    problems.append('MANIFEST.md missing')
    listed = set()
else:
    m_text = manifest.read_text()
    listed = set(re.findall(r'^\|\s*`([a-z][a-z0-9-]+)`\s*\|', m_text, re.M))
unlisted = sorted(f for f in files if f not in listed)
print(f'agents: {len(files)} files, {len(listed)} in MANIFEST table')
print(f'frontmatter_problems: {len(problems)}')
for p in problems[:5]:
    print(f'  {p}')
if unlisted:
    print(f'  not in manifest: {unlisted}')
PY
```

- PASS: 0 frontmatter problems, 0 unlisted agents.
- FAIL: any frontmatter error, or 1+ agent missing from MANIFEST (invocation will fail for unlisted agents).

---

## TIER J — Skills Deep + Hook Behavior

Existing tier F4 counts critical skills. This tier verifies *structure*:
every SKILL.md has valid frontmatter with `name:` matching its folder,
every sub-skill's `name:` matches its filename stem, and no router
contains a sub-skill with the same name as the router.

### Check J1-J3: Skills deep-structure walk

Single inline skill-validator. Walks `skills/*/SKILL.md` and
`skills/*/*.md`. Routers MUST have valid frontmatter and a `name:` field
matching the folder — harness discovery depends on it. Sub-skills are
lighter: a `---` block is encouraged but optional (routers read them
by filename). When a sub-skill *does* have frontmatter, its `name:`
must match the filename stem.

```bash
python3 - <<'PY'
import re
from pathlib import Path
root = Path.home() / 'helm/03-rai/skills'
EXCLUDE_SUB = {'SKILL.md', 'MANIFEST.md', 'GAPS.md', 'README.md'}
router_problems, sub_problems, sub_no_frontmatter, collisions = [], [], [], []
def parse_name(path):
    text = path.read_text(encoding='utf-8', errors='replace')
    if not text.startswith('---'):
        return None, 'no frontmatter'
    m = re.search(r'^name:\s*([\w:-]+)', text, re.M)
    if not m:
        return None, 'no name field'
    return m.group(1), None
router_dirs = sorted(d for d in root.iterdir() if d.is_dir())
router_names = set()
for rd in router_dirs:
    skill_md = rd / 'SKILL.md'
    if not skill_md.exists():
        router_problems.append(f'{rd.name}/: no SKILL.md'); continue
    name, err = parse_name(skill_md)
    if err:
        router_problems.append(f'{rd.name}/SKILL.md: {err}'); continue
    if name != rd.name:
        router_problems.append(f'{rd.name}/SKILL.md: name={name} mismatches folder')
    router_names.add(rd.name)
    for sub in rd.glob('*.md'):
        if sub.name in EXCLUDE_SUB:
            continue
        sub_name, err = parse_name(sub)
        if err == 'no frontmatter':
            sub_no_frontmatter.append(f'{rd.name}/{sub.name}')
            continue
        if err:
            sub_problems.append(f'{rd.name}/{sub.name}: {err}'); continue
        if sub_name != sub.stem:
            sub_problems.append(f'{rd.name}/{sub.name}: name={sub_name} mismatches stem')
        if sub_name == rd.name:
            collisions.append(f'{rd.name}/{sub.name}: shares router name')
manifest = root / 'MANIFEST.md'
unlisted = []
if manifest.exists():
    m_text = manifest.read_text()
    listed = set(re.findall(r'^\|\s*[A-Z]\s*\|\s*\*\*([a-z][a-z0-9-]+)\*\*', m_text, re.M))
    unlisted = sorted(r for r in router_names if r not in listed)
print(f'routers: {len(router_names)}, router_problems: {len(router_problems)}')
print(f'sub_skills_with_frontmatter_errors: {len(sub_problems)}')
print(f'sub_skills_without_frontmatter: {len(sub_no_frontmatter)} (advisory)')
print(f'collisions: {len(collisions)}')
print(f'manifest_drift: {len(unlisted)}')
for p in router_problems[:3]: print(f'  router: {p}')
for p in sub_problems[:3]: print(f'  sub: {p}')
for c in collisions[:3]: print(f'  collision: {c}')
if unlisted: print(f'  drift: {unlisted[:5]}')
PY
```

- PASS: 0 router_problems, 0 sub_problems, 0 collisions, manifest_drift ≤ 1.
- WARN: 20+ sub-skills without frontmatter (encourage adding), OR manifest_drift 2-3.
- FAIL: any router_problem, any sub_problem (name mismatch on frontmatter-having sub-skill), any collision, OR manifest_drift > 3.

### Check J4: Hooks firing recency

Every registered hook in `~/.claude/settings.json` should appear at least
once in `hook-perf.jsonl` within a rolling window. A hook that has stopped
firing is a silent regression: the harness no longer invokes it, or
`hook_timer` is crashing before it logs.

Skip when `--quick` is passed.

```bash
python3 - <<'PY'
import datetime, json, time
from collections import deque
from pathlib import Path
home = Path.home()
settings = home / '.claude/settings.json'
registered = set()
try:
    cfg = json.loads(settings.read_text())
    for _event, groups in cfg.get('hooks', {}).items():
        for g in groups:
            for h in g.get('hooks', []):
                for tok in h.get('command', '').split():
                    if tok.endswith('.py') and '/hooks/' in tok:
                        registered.add(Path(tok).stem); break
except Exception as e:
    print(f'settings_parse: FAIL — {e}'); raise SystemExit
log = home / 'helm/03-rai/memory/learning/system/hook-perf.jsonl'
seen_7d, seen_14d = set(), set()
if log.exists():
    cut7 = time.time() - 7 * 86400
    cut14 = time.time() - 14 * 86400
    with log.open() as f:
        for line in deque(f, maxlen=5000):
            try:
                e = json.loads(line)
                ts = e.get('ts', '')
                dt = datetime.datetime.fromisoformat(ts.replace('Z', '+00:00'))
                epoch = dt.timestamp()
                name = e.get('hook', '')
                if epoch > cut14:
                    seen_14d.add(name)
                if epoch > cut7:
                    seen_7d.add(name)
            except Exception:
                continue
silent_7d  = sorted(registered - seen_7d)
silent_14d = sorted(registered - seen_14d)
print(f'registered: {len(registered)}, firing_7d: {len(seen_7d)}, firing_14d: {len(seen_14d)}')
if silent_7d:  print(f'  silent_7d:  {silent_7d}')
if silent_14d: print(f'  silent_14d: {silent_14d}')
PY
```

- PASS: every registered hook seen within last 7 days.
- WARN: 1-2 hooks silent 7-14d (low-frequency hooks like `work-completion-learning`).
- FAIL: 1+ hook silent > 14d, OR 3+ hooks silent 7-14d.

### Check J5: `hooks/lib/*.py` importable

If any `lib/` module has an import error, every hook that imports it
cascade-fails silently. Catch this early.

```bash
python3 - <<'PY'
import sys
from pathlib import Path
hooks_dir = Path.home() / 'helm/03-rai/hooks'
sys.path.insert(0, str(hooks_dir))
lib_dir = hooks_dir / 'lib'
mods = sorted(p.stem for p in lib_dir.glob('*.py') if p.name != '__init__.py')
errors = []
for m in mods:
    try:
        __import__(f'lib.{m}')
    except Exception as e:
        errors.append(f'lib.{m}: {type(e).__name__}: {e}')
print(f'lib_modules: {len(mods)}, import_errors: {len(errors)}')
for e in errors:
    print(f'  {e}')
PY
```

- PASS: 0 import errors.
- FAIL: any ImportError, SyntaxError, or circular import.

---

## TIER K — Work State + Protection

Validates live work-tracking artifacts (PRD/META), settings.json counts
coherence against filesystem truth, secret-protection patterns, hook
context-mapping, and external config (MCP, statusline). These are
DEGRADED-tier — failures don't corrupt data but mean specific features
(hook routing, secret scanning, HUD) stop working correctly.

### Check K1: META.yaml present and parseable in every work dir

The Algorithm spec references PRD.md but current work dirs use
`META.yaml`. Sanity checks what's actually on disk. Regex-based parser
avoids `yaml` stdlib dependency.

Skip when `--quick` is passed (walks all ~80 work dirs).

```bash
python3 - <<'PY'
import re
from pathlib import Path
work = Path.home() / 'helm/03-rai/memory/work'
if not work.is_dir():
    print('work: FAIL — folder missing'); raise SystemExit
dirs = sorted(d for d in work.iterdir() if d.is_dir())
bad = []
for d in dirs:
    meta = d / 'META.yaml'
    if not meta.exists():
        bad.append(f'{d.name}: no META.yaml'); continue
    text = meta.read_text(encoding='utf-8', errors='replace')
    if not re.search(r'^\s*status\s*:', text, re.M):
        bad.append(f'{d.name}: no status field')
print(f'work_dirs: {len(dirs)}, malformed: {len(bad)}')
for b in bad[:5]:
    print(f'  {b}')
PY
```

- PASS: 0 malformed.
- WARN: 1-3 malformed (recently-started work, not yet populated).
- FAIL: 4+ malformed (work tracking broken or `auto-work-creation.py` regressed).

### Check K2: Counts coherence vs filesystem

Semantics match `hooks/update-counts.py` exactly: skills = dirs at
`skills/*/` with `SKILL.md`; hooks = `*.py` at depth 1 in `hooks/`;
work = dirs in `memory/work/`; learnings = all `*.json` under
`memory/learning/`; ratings = lines in `ratings.jsonl`.

```bash
python3 - <<'PY'
import json, os
from pathlib import Path
home = Path.home()
rai = home / 'helm/03-rai'
def count_skills():
    d = rai / 'skills'
    return sum(1 for p in d.iterdir() if p.is_dir() and (p / 'SKILL.md').exists()) if d.is_dir() else 0
def count_hooks():
    d = rai / 'hooks'
    return len(list(d.glob('*.py'))) if d.is_dir() else 0
def count_ratings():
    r = rai / 'memory/learning/signals/ratings.jsonl'
    return sum(1 for _ in r.open()) if r.exists() else 0
def count_work():
    d = rai / 'memory/work'
    return sum(1 for p in d.iterdir() if p.is_dir()) if d.is_dir() else 0
def count_learnings():
    d = rai / 'memory/learning'
    if not d.is_dir(): return 0
    n = 0
    for _, _, files in os.walk(d):
        n += sum(1 for f in files if f.endswith('.json'))
    return n
actual = {'skills': count_skills(), 'hooks': count_hooks(), 'ratings': count_ratings(),
          'work': count_work(), 'learnings': count_learnings()}
settings = rai / 'config/settings.json'
stored = {}
if settings.exists():
    try:
        stored = (json.loads(settings.read_text()).get('counts') or {})
    except Exception as e:
        print(f'settings_parse: FAIL — {e}'); raise SystemExit
max_drift = 0.0
for k, v in actual.items():
    old = stored.get(k, 0)
    if old == 0 and v == 0:
        flag = 'OK'; drift = 0
    elif old == 0:
        flag = 'NEW'; drift = 100
    else:
        drift = (v - old) / old * 100
        flag = 'OK' if abs(drift) <= 10 else ('DRIFT' if abs(drift) <= 30 else 'STALE')
    max_drift = max(max_drift, abs(drift))
    print(f'  {k}: stored={old}, actual={v} ({drift:+.0f}%) [{flag}]')
print(f'max_drift: {max_drift:.0f}%')
PY
```

- PASS: max_drift ≤ 10%.
- WARN: max_drift 10-30% (SessionEnd hasn't fired since recent additions; self-healing).
- FAIL: max_drift > 30% (`update-counts.py` broken or semantics diverged).

### Check K3: `.pai-protected.json` valid + regex compile + smoke test

Loads every regex pattern; confirms they compile; runs positive and
negative smoke tests to prove the scanner actually catches what it
should and doesn't false-positive on innocuous text.

```bash
python3 - <<'PY'
import json, re
from pathlib import Path
pai = Path.home() / 'helm/03-rai/.pai-protected.json'
if not pai.exists():
    print('pai: FAIL — .pai-protected.json missing'); raise SystemExit
try:
    data = json.loads(pai.read_text())
except Exception as e:
    print(f'pai: FAIL — invalid JSON: {e}'); raise SystemExit
pattern_list = []
def walk(obj):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in ('patterns', 'regex') and isinstance(v, list):
                pattern_list.extend(x for x in v if isinstance(x, str))
            else:
                walk(v)
    elif isinstance(obj, list):
        for x in obj: walk(x)
walk(data)
compile_errors = 0
for pat in pattern_list:
    try:
        re.compile(pat)
    except re.error as e:
        compile_errors += 1
        print(f'  bad regex: {pat[:40]!r} — {e}')
print(f'patterns: {len(pattern_list)}, compile_errors: {compile_errors}')
positive = 'ghp_' + 'a' * 36
negative = 'hello world, nothing to see'
hits_pos = sum(1 for p in pattern_list if re.search(p, positive))
hits_neg = sum(1 for p in pattern_list if re.search(p, negative))
print(f'smoke: positive_hits={hits_pos} (>=1 expected), negative_hits={hits_neg} (0 expected)')
PY
```

- PASS: 0 compile errors, positive_hits ≥ 1, negative_hits == 0.
- FAIL: invalid JSON, any compile error, positive_hits == 0, OR negative_hits > 0.

### Check K4: `context_mapping.json` valid + paths exist

```bash
python3 - <<'PY'
import json
from pathlib import Path
cm = Path.home() / 'helm/03-rai/hooks/context_mapping.json'
if not cm.exists():
    print('context_mapping: FAIL — missing'); raise SystemExit
try:
    data = json.loads(cm.read_text())
except Exception as e:
    print(f'context_mapping: FAIL — invalid JSON: {e}'); raise SystemExit
paths = []
if isinstance(data, dict):
    for k in data:
        if isinstance(k, str) and ('/' in k or k.startswith('~')):
            paths.append(k)
stale = []
for p in paths:
    if '*' in p or '?' in p:  # glob patterns are templates, not literal paths
        continue
    expanded = Path(p.replace('~', str(Path.home())))
    if not expanded.exists():
        stale.append(p)
print(f'mapped_paths: {len(paths)}, stale: {len(stale)}')
for s in stale[:5]:
    print(f'  stale: {s}')
PY
```

- PASS: 0 stale paths.
- WARN: 1-2 stale (renamed folder; update mapping).
- FAIL: invalid JSON or 3+ stale paths.

### Check K5: MCP + statusline integrity

```bash
python3 - <<'PY'
import json, os
from pathlib import Path
home = Path.home()
ok = True
for p in [home / '.claude/mcp.json', home / 'helm/03-rai/config/mcp.json']:
    if not p.exists():
        print(f'  {p.name} ({p.parent.name}): MISSING'); ok = False; continue
    try:
        doc = json.loads(p.read_text())
        servers = (doc.get('mcpServers') or {})
        print(f'  {p.name} ({p.parent.name}): OK, {len(servers)} server(s)')
    except Exception as e:
        print(f'  {p.name} ({p.parent.name}): INVALID — {e}'); ok = False
statusline = home / 'helm/03-rai/config/statusline.sh'
if not statusline.exists():
    print('  statusline.sh: MISSING'); ok = False
elif not os.access(statusline, os.X_OK):
    print('  statusline.sh: NOT executable'); ok = False
else:
    print('  statusline.sh: executable')
print(f'k5: {"OK" if ok else "FAIL"}')
PY
```

- PASS: both mcp.json files valid, statusline.sh executable.
- FAIL: any JSON parse error, missing file, or non-executable statusline.

---

## Report Format

After running all checks, print one consolidated table. Group by tier so the user can see which layer is healthy.

```
# Brain Sanity Check — YYYY-MM-DD HH:MM

## Tier A: Data Safety
| # | Component | Status | Evidence |
|---|-----------|--------|----------|
| A1 | Git backup | PASS | uncommitted=5, unpushed=0, last=1d ago, remote=yes |
| A2 | File baselines | PASS | md=1247 (+0.3%), chromadb=42MB (+1.1%) |

## Tier B: Environment
| # | Component | Status | Evidence |
|---|-----------|--------|----------|
| B1 | Python + chromadb | PASS | chromadb 1.5.8 |
| B2 | py-chroma.sh | PASS | executable |

## Tier C: ChromaDB Integrity
| # | Component | Status | Evidence |
|---|-----------|--------|----------|
| C1 | Collections | PASS | memories |
| C2 | Populated | PASS | 380 entries, 2026-01-22 → 2026-04-16 |
| C3 | Monthly coverage | WARN | 2026-03: 15 entries |
| C4 | Write round-trip | PASS | OK |
| C5 | Semantic query | PASS | 3 results, top sim 0.61 |

## Tier D: Pipeline Health
| # | Component | Status | Evidence |
|---|-----------|--------|----------|
| D1 | Pending queue | WARN | pending=8, summaries=0 |
| D2 | Capture live | PASS | newest 2h ago |
| D3 | STATE/RELATIONSHIP | PASS | STATE 1h, RELATIONSHIP 3h |
| D4 | SessionStart hook | PASS | Who/Mission/Recent Memory present |

## Tier E: Configuration Integrity
| # | Component | Status | Evidence |
|---|-----------|--------|----------|
| E1 | JSON configs valid | PASS | 4/4 parse |
| E2 | Hooks registered | PASS | 24/24 scripts resolved, all executable |
| E3 | .claude/ symlinks | PASS | 9/9 resolve to helm |
| E4 | No broken symlinks | PASS | 0 dangling |

## Tier F: Vault + Identity
| # | Component | Status | Evidence |
|---|-----------|--------|----------|
| F1 | Top-level folders | PASS | 14/14 |
| F2 | Templates | PASS | 5/5 required |
| F3 | Root files | PASS | CLAUDE.md + .helm-index/helm-index.md |
| F4 | Skills reachable | PASS | 67 global, 3/3 critical |
| F5 | Template integrity | PASS | all have frontmatter |
| F6 | Hook failure logs | PASS | 0 recent errors |
| F7 | Identity files | PASS | rai=4 ana=12 |
| F8 | Identity cache | PASS | mtime drift 0.3s |

## Tier G: Memory Index
| # | Component | Status | Evidence |
|---|-----------|--------|----------|
| G1 | MEMORY.md | PASS | 16 lines, 3 refs, all exist |

## Tier H: Hygiene
| # | Component | Status | Evidence |
|---|-----------|--------|----------|
| H1 | Orphans + duplicates | PASS | no orphans, no alias |

## Tier I: Algorithm + Agents
| # | Component | Status | Evidence |
|---|-----------|--------|----------|
| I1 | Algorithm symlink | PASS | -> v3.7.0.md (26012 bytes) |
| I2 | Phases + tiers | PASS | 7/7 phases, 5/5 tiers |
| I3 | Algorithm state | PASS | 8 files, newest 0.1d |
| I4 | Agents + MANIFEST | PASS | 10 files, 0 problems |

## Tier J: Skills Deep + Hook Behavior
| # | Component | Status | Evidence |
|---|-----------|--------|----------|
| J1-J3 | Skills structure | PASS | 22 routers, 0 problems, 0 collisions |
| J4 | Hooks firing | PASS | 19/19 firing in 7d |
| J5 | lib/ importable | PASS | 18 modules, 0 errors |

## Tier K: Work State + Protection
| # | Component | Status | Evidence |
|---|-----------|--------|----------|
| K1 | META.yaml parseable | PASS | 84 dirs, 0 malformed |
| K2 | Counts coherence | PASS | max_drift 3% |
| K3 | Protected patterns | PASS | 47 patterns compile, smoke OK |
| K4 | Context mapping | PASS | 0 stale paths |
| K5 | MCP + statusline | PASS | 2 configs, executable |

## Summary
- PASS: 33  WARN: 2  FAIL: 0
- Overall: HEALTHY
```

## Verdict Rules

- **HEALTHY** (green): All PASS, optional WARN ≤ 2.
- **DEGRADED** (yellow): Any FAIL in E/F/G/H, J1-J3, or K; or 3+ WARN anywhere.
- **BROKEN** (red): Any FAIL in A, B, C, D, I, J4, or J5. Stop and address before doing other work on the brain. These are load-bearing — data safety, runtime, storage, pipeline, algorithm spine, hook firing, lib imports.

## Fix Suggestions

For each FAIL, print a one-line fix hint:

| Failure | Fix |
|---------|-----|
| Git unpushed > 0 for days | `cd ~/helm && git push`. The laptop is the only copy until then. |
| Git remote unreachable | Check network. Verify `git remote -v` points at reachable GitHub repo. |
| File baseline: large drop | Investigate `git status` and recent trash activity before running `--baseline` to reset. |
| chromadb import error | Warm the uv cache, then verify `py-chroma.sh` exists and is executable. |
| Collection missing | Check `scripts/store_to_chromadb.py` for hardcoded collection names. Recreate carefully. |
| ChromaDB empty or stale | Run `/process-sessions` to drain any backlog. |
| Round-trip FAIL | DB is read-only or corrupted. Do not run `/process-sessions`. Inspect file permissions and disk space. |
| pending >= 10 | Run `/process-sessions` manually. |
| pending-summaries > 0 | Pipeline stalled between summarization and storage. Check `scripts/store_to_chromadb.py` args. |
| SessionStart hook blank | Check `PAI_DIR` env var and `identity/` files. |
| STATE/RELATIONSHIP stale | Check `relationship-memory.py` and `save-memory.py` SessionEnd hooks. |
| JSON config invalid | Restore from `git diff` / git history. Never hand-edit without backup. |
| Hooks script missing | Edit the Rai `settings.json` (source of truth), not the `.claude/` symlink. |
| .claude/ symlink broken | `ln -sfn ~/helm/03-rai/<target> ~/.claude/<name>`. |
| Broken symlinks in tree | Delete each dangling link. Common causes: cross-machine paths, renamed targets. |
| Top-level folder missing | Restore from git. These folders are structural. |
| Template missing | Restore from git or `12-system/templates/`. |
| MEMORY.md > 200 lines | Anything past line 200 is silently truncated by the auto-memory loader. Refactor now. |
| Orphan directory | A symlink was overwritten by a real directory. Move aside, re-create the symlink. |
| Identity file unreadable | Restore from git: `cd ~/helm && git checkout 03-rai/identity/ 02-ana/identity/`. |
| Identity cache drift | Normal after editing identity; next SessionStart heals. If persistent, check `session-start.py`. |
| Algorithm symlink broken | `cd ~/helm/03-rai/algorithm && ln -sfn v3.X.Y.md latest`. |
| Algorithm phases/tiers missing | Spec drift from `CLAUDE.md`. Restore from git or update one to match the other. |
| Algorithm state stale >30d | `algorithm-scan.py` SessionEnd hook has regressed. Check hook-errors.jsonl for it. |
| Agent frontmatter error | Each `agents/*.md` must have `---`+ `name: <stem>`. Restore or fix by hand. |
| Agent missing from MANIFEST | Edit `agents/MANIFEST.md` to list the file, or remove the file if unintended. |
| Skill frontmatter error | Each `SKILL.md` needs `name:` matching folder; each sub-skill needs `name:` matching stem. |
| Router/sub-skill collision | A sub-skill shares its router's name (e.g. `research/research.md`). Rename one. |
| Manifest drift >3 | `skills/MANIFEST.md` is out of sync. Update it or move the folder. |
| Hook silent >14d | Hook has stopped firing. Check `~/.claude/settings.json` matchers and hook-errors.jsonl. |
| `hooks/lib` ImportError | A lib module has a syntax error or broken import. Run `python3 -c "import lib.<name>"` to isolate. |
| META.yaml malformed | Restore or recreate. `auto-work-creation.py` writes these — check for hook regressions. |
| Counts drift >30% | `update-counts.py` SessionEnd hook has stopped firing or changed semantics. |
| Protected patterns broken | Restore `.pai-protected.json` from git. Run K3 smoke test to verify. |
| context_mapping.json stale | Folder was renamed; update the mapping or remove obsolete keys. |
| mcp.json invalid | Restore from git. Harness will drop MCP connections until fixed. |
| statusline.sh not executable | `chmod +x ~/helm/03-rai/config/statusline.sh`. |

## Notes

- Do NOT auto-fix anything (except when `--baseline` is passed, which only writes `.sanity-baseline.json`).
- The `py-chroma.sh` wrapper is required because the system python on some machines has no chromadb module. Do not call `python3` directly for chromadb operations.
- Vacation gaps in month coverage are expected and should WARN not FAIL.
- Tier A (Data safety) is the most important. A brain that is entirely readable but never backed up is one disk failure away from gone.
- The `--baseline` flag is the only case where this skill writes to the brain. All other checks are read-only.
