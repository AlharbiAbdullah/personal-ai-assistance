---
name: trace
description: >
  Walk a bug, incident, or request lifecycle through a system as a single self-contained animated
  HTML file — a packet pulses along the real path to the failure point, a scrubbable timeline of
  what happened when, and a hypothesis tree. Light/dark toggle. Invoked via /visual router. Use
  when John says "visual trace" / "visualize this bug/incident/request".
---

# /visual · trace

Make a bug or an incident *legible* by animating its path through the system — in a **single
self-contained HTML file**. The flow-dot rides the real edges to the **point of failure**, a
scrubbable timeline replays what happened when, and a hypothesis tree shows what was ruled in
and out. A debugging/postmortem companion to the `debugger` agent.

## How John uses it
1. Something broke, or a request's lifecycle is hard to hold in the head.
2. He says **"visual trace"** (or "visualize this bug / incident / request path").
3. You build the HTML: the path, the failure, the timeline, the hypotheses, the fix.
4. He scrubs the timeline, follows the pulse, sees where it went wrong.

## Build it (from `references/engine.html` — see the router's Engine API)
1. **Reconstruct the real path first.** Read the code, the logs, the trace. Every node, edge,
   and timestamp must be real — a trace that invents the path teaches the wrong lesson.
2. **Clone the engine**, set `<body data-nav="scroll" data-skill="trace">`. Scroll suits a
   narrative ("here's what happened, in order"); use `tabs` if it's more of a reference.
3. **Fill the sections** (rename/drop to fit):
   - **What broke** — the symptom in one line + the blast radius.
   - **The path** — a `graph()` of the request/data route; the failure node tinted red.
   - **Timeline** — the **scrubbable ribbon** of events with timestamps; scrubbing updates a caption.
     Animate latency/counts with **count-up** badges.
   - **Hypotheses** — a tree/list of what was suspected, with each ruled in (green) or out (red)
     using `.diff-add` / `.diff-rem` glyphs (not color alone).
   - **Root cause & fix** — the actual cause, the fix, and the guardrail that stops a recurrence.
4. **Signature animation — the pulse to failure.** A `flowDot()` travels the real edges and, on
   reaching the failure node, **flashes red and stops** (use the `red` color, drop the success
   landing). Sync it to the timeline scrub so dragging the playhead moves the pulse — the reader
   watches the request die exactly where it died.

## When NOT to use
- A one-line root cause is enough — just say it.
- Explaining healthy steady-state behavior → use `explain`. Planning a fix's build → use `plan`.
