# Semantic Memory

A vector store (ChromaDB) that lets the assistant recall past context by meaning, not just
by filename. **It starts empty** and is built from your own usage — nothing is pre-seeded.

## Layout

- `pending/` — a queue of facts waiting to be embedded into the index. Session processing
  drops JSON here; the embed step consumes it.
- `scripts/` — the helper scripts that build and query the index (`py-chroma.sh` and friends).
- `chromadb/` — the actual vector database. **Not included and gitignored** — it's a large
  binary that is *derived* from `pending/` + your source memory, so it's rebuilt rather than
  shipped or synced.

## Initializing it

You don't have to do anything up front — the index builds itself as you use the system and
run `/process-sessions`. The first run creates `chromadb/` locally.

If you want to (re)build from scratch, run the embed step in `scripts/` (the SessionStart
hook and `/process-sessions` call it for you). Because the index is derived, deleting
`chromadb/` is safe — it regenerates from `pending/` and your memory.

## Why it's gitignored

The embeddings index was historically the single biggest source of git bloat (it's
re-snapshotted whole on every change). The information lives in your source memory; this is
just a fast lookup layer. Keep it out of git and let each machine rebuild it.
