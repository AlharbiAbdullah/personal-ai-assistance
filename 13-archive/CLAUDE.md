# 13-archive/ — Session Preservation

## Purpose

This folder preserves session JSONs forever. Other historical artifacts are deleted — git log is the archive.

Session JSONs are cheap to store and the forensic/wisdom-mining value compounds over time. That's why they get the exception.

## What lives here

- `historical-sessions/` — session JSONs from `/process-sessions` drain.
- `learning/` — retired learning topics, moved here whole at John's explicit request (2026-06-10: adapting-pai, claude-code-mastery, omarchy, opencode-cli, personal-ai-infrastructure). Frozen reference, not active curricula.
- `news/` — prior news digests (`daily/`, `weekly/`), moved here automatically by the `/news` skill after each run (exception added 2026-06-10 at John's request), plus `news/dumps/YYYY-MM-DD/` — the FULL raw collection dumps of every news run (all ~2k tweets/posts collected each day, not just the ~100 displayed; exception added 2026-06-13 at John's request). Copied automatically by `present_v5.py` and the scheduled runner. Git-tracked, synced Mac↔Ubuntu, NEVER purged.

Nothing else.

## Rules

- **Archive is sessions-only, plus the `learning/` exception above.** Other content (plans, snapshots, stale docs) gets deleted, not archived. New exceptions require John's explicit request.
- **Read-only by default.** Do not modify archived session JSONs. The whole point is that they're frozen.
- **No new content authored here.** If something needs to be written, it belongs in a live folder (`09-ideas/`, `06-learning/`, `10-knowledge/`, etc.).

## What Claude should do

When asked about a past session, treat historical-sessions/ as the authoritative record for what happened that session.

Never move non-session content into 13-archive. If a user asks to "archive" a note, ask whether they mean delete (default) or keep in live folders with an "archived" status.

Never edit archived session JSONs unless the user explicitly asks.
