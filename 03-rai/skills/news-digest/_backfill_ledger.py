#!/usr/bin/env python3
"""One-off: seed seen_ledger.jsonl from prior digests (v5.4 migration).

Walks every dated daily digest in ~/helm/13-archive/news/daily/ and
~/helm/08-bawaba/daily/, extracts displayed URLs (News Wire + Gems sections,
same parsing as the old cross-day dedup), and writes URL-only ledger records
with the EARLIEST first_seen per URL. Titles/authors are not reliably
parseable from old markdown; URL is the primary dedup key anyway.

Idempotent: rewrites the backfilled records but preserves any records whose
first_seen is newer than every digest date (i.e., live appends).

Usage:
    python3 _backfill_ledger.py            # writes seen_ledger.jsonl
    python3 _backfill_ledger.py --dry-run  # report only
"""
import argparse
import json
import re
from pathlib import Path

SKILL_DIR = Path(__file__).parent
LEDGER_PATH = SKILL_DIR / "seen_ledger.jsonl"
DIGEST_DIRS = [
    Path.home() / "helm/13-archive/news/daily",
    Path.home() / "helm/08-bawaba/daily",
]
DATED_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})\.md$")


def normalize_url(u):
    if not u:
        return ""
    u = u.split("?")[0].split("#")[0].rstrip("/").lower()
    return re.sub(r"^https?://(www\.)?", "", u)


def parse_digest_urls(digest_path):
    urls = set()
    text = digest_path.read_text()
    if text.startswith("---"):
        end = text.find("---", 3)
        if end != -1:
            text = text[end + 3:]
    wisdom_idx = text.find("\n## Wisdom")
    if wisdom_idx != -1:
        text = text[:wisdom_idx]
    for m in re.finditer(r"https?://\S+", text):
        urls.add(normalize_url(m.group(0).rstrip(").,;:>*_`'\"!")))
    return urls


def guess_src(u):
    host = u.split("/")[0]
    if "substack.com" in host or "/p/" in u:
        return "substack"
    if host in ("x.com", "twitter.com"):
        return "x_foryou"
    if "reddit.com" in host:
        return "reddit"
    if host == "news.ycombinator.com":
        return "hn"
    if host == "github.com":
        return "github"
    if "medium.com" in host or "/@" in u:
        return "medium"
    return "web"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    first_seen = {}  # url -> earliest digest date
    files = []
    for d in DIGEST_DIRS:
        if not d.exists():
            continue
        for p in sorted(d.iterdir()):
            m = DATED_RE.match(p.name)
            if m:
                files.append((m.group(1), p))
    files.sort()
    print(f"scanning {len(files)} digests across {len(DIGEST_DIRS)} dirs")

    for date, p in files:
        for u in parse_digest_urls(p):
            if u and (u not in first_seen or date < first_seen[u]):
                first_seen.setdefault(u, date)

    # preserve live records newer than the backfill window
    max_digest_date = files[-1][0] if files else ""
    preserved = []
    if LEDGER_PATH.exists():
        for line in LEDGER_PATH.read_text().splitlines():
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if rec.get("first_seen", "") > max_digest_date and rec.get("u") not in first_seen:
                preserved.append(line)

    print(f"backfill: {len(first_seen)} unique URLs (earliest first_seen kept), "
          f"{len(preserved)} newer live records preserved")
    if args.dry_run:
        for u in list(first_seen)[:10]:
            print(f"  {first_seen[u]}  {u}")
        return

    lines = [
        json.dumps({"u": u, "t": "", "a": "", "src": guess_src(u),
                    "first_seen": d, "published": None}, ensure_ascii=False)
        for u, d in sorted(first_seen.items(), key=lambda kv: (kv[1], kv[0]))
    ] + preserved
    LEDGER_PATH.write_text("\n".join(lines) + "\n")
    print(f"wrote {LEDGER_PATH} ({len(lines)} records)")


if __name__ == "__main__":
    main()
