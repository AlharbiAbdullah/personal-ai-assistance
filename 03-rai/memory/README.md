# Memory

File-based memory for the assistant. **It starts empty** — the directories below fill in
as you use the system. Nothing here is shipped pre-populated; your memory is yours.

| Folder | What accumulates here |
|--------|------------------------|
| `learning/` | Telemetry the hooks emit — counts, timings, signals used to tune behavior over time. |
| `relationship/` | Month-bucketed notes about working with you (preferences, corrections, context). |
| `security/` | A log of anything the security validator flagged or blocked. |
| `state/` | Per-session working state (current work, tab titles, algorithm state). Ephemeral. |
| `work/` | One folder per non-trivial task: its PRD and working notes (see the algorithm). |
| `ai-calls/` | Logs and prompts from external model calls (if you use the `/ask-model` skill). |

## How it fills

- **Hooks** write `learning/`, `security/`, and `state/` automatically as sessions run.
- The **algorithm** creates a `work/{slug}/PRD.md` for non-trivial tasks.
- **Session processing** (`/process-sessions`) distills finished sessions into `relationship/`
  notes and queues facts for the semantic index.

## Privacy

This whole tree is personal and is **gitignored from the public starter kit's history**
by default where it would contain real content (see the root `.gitignore`). If you publish
your own fork, keep your memory out of the public repo unless you mean to share it.
