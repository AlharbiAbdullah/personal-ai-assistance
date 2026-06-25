---
name: explain
description: >
  Explain something that ALREADY exists — a system, codebase, concept, process, or
  decision — as a single self-contained animated HTML file with a light/dark toggle.
  Excalidraw-style diagrams, a flow-dot that traces the real runtime path, focus+context
  on dense diagrams. A communication artifact, NOT a gate. Invoked via /visual router.
  Use when John says "visual explain" / "explain this visually".
---

# /visual · explain

Explain something in a **single self-contained HTML file**, not chat prose. HTML opens the
gate: hand-drawn diagrams, a **packet that traces the real runtime path**, focus+context to
keep complex diagrams readable, and a light/dark toggle.

The point is *understanding*, not approval and not testing. It's a random-access reference
the reader jumps around in — onboarding to a subsystem, unpacking a tricky flow, walking a
decision. No gate; usable anytime, including after code ships.

## How John uses it
1. You're discussing something — a system, a piece of code, a concept, a choice.
2. He says **"visual explain"** (or "explain this visually").
3. You **create the HTML** and live-update it as the explanation sharpens.
4. He opens it in a browser, toggles light/dark, clicks through.

## Build it (from `references/engine.html` — see the router's Engine API)
1. **Understand first** — read the real files/symbols, or pin the concept down precisely.
   You can't draw a clean picture of something you only half-know.
2. **Clone the engine**, set `<body data-nav="tabs" data-skill="explain">`. Tabs = random access.
3. **Fill the sections** (rename/drop to fit):
   - **Big picture** — the essence in one paragraph + the "so what" + an analogy.
   - **How it works** — `graph()` of the runtime path + a clickable stepper.
   - **The parts** — `graph()` of components; turn on `legend()` + focus+context for the dense one.
   - **Zoom in** — an A/B toggle to compare two states / approaches / before-after.
   - **Why it matters** — strength/cost trade-off cards.
   - **Recap** — the whole thing recompressed + an optional check-yourself list.
4. **Signature animation — the guided trace.** A `flowDot()` rides the *actual* edges as the
   stepper advances, lighting each node on arrival, so the reader's eye literally follows data
   through the system. Keep it synced to the stepper (one source of truth = current step). The
   path must mirror the real runtime path — never decorate.
5. **Put all diagrams in `diagrams()`** so the theme toggle redraws them. **Update live** —
   re-edit the same file; tell him to refresh.

## When NOT to use
- A one-sentence answer would do — just say it.
- Planning a feature for approval → use `plan`. Teaching so he can *do* it → use `teach`.
- The thing is genuinely simple — a picture would add ceremony, not clarity.
