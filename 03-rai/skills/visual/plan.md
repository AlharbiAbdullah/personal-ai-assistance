---
name: plan
description: >
  Plan a NEW feature or a messy multi-file change as a single self-contained animated
  HTML file — the HTML *is* the plan and the approval gate before any code is written.
  Excalidraw-style diagrams, light/dark toggle, an animated old→new diff. Invoked via
  /visual router. Use when John is in plan mode and says "visual plan".
---

# /visual · plan

Plan a feature in a **single self-contained HTML file**, not chat prose. HTML opens the
gate: interactive diagrams, clickable wireframes, togglable UI states, an **animated diff**
that shows the change as motion. The HTML is the living plan and the approval gate — code
begins only after John approves.

Reach for it **occasionally**, when a feature is messy enough that a visual, interactive
plan beats prose. It does **not** touch `memory/work/.../PRD.md` or the Algorithm phases —
it is its own thing.

## How John uses it
1. He's building a new feature and switches to **plan mode**.
2. He says **"visual plan"**.
3. You **create and live-update the HTML** as you plan — every diagram, decision, and open question lands in it.
4. He opens it in a browser, reviews, comments.
5. **He approves → only then does code begin.**

## Plan-specific rules
- **No source-code edits while the plan is built or reviewed.** The only file you write
  is the plan HTML under `visual/`. The plan is the gate; editing source starts only after approval.
- **Argue a future state.** Plan must *sell* the change — be persuasive and decision-oriented.
  Lead with the outcome (what + why), then the shape, then the open blockers.

> Strict plan mode blocks all file writes, including this HTML. To live-update as you plan,
> work in normal mode and let the no-source-edits rule be the gate. If he insists on strict
> mode, write the HTML at each ExitPlanMode checkpoint instead of continuously.

## Build it (from `references/engine.html` — see the router's Engine API)
1. **Inspect first** — read the real files, schemas, symbols. Ground every box and file reference.
2. **Clone the engine**, set `<body data-nav="tabs" data-skill="plan">`. Tabs keep the plan
   scroll-reviewable and find-on-page-able; the **last tab is the approval gate**.
3. **Fill the sections** (rename/drop to fit):
   - **Overview** — prose-first outcome (what + why), at-a-glance decisions, build sequence.
   - **Architecture** — `graph()` of components & deps.
   - **Flow** — `graph()` of the runtime path (numbered steps).
   - **Data** — a hand-drawn record card or styled table.
   - **UI** — clickable wireframe; use HTML state toggles to show design options live.
   - **Decisions** — trade-off cards (`note` / `warn`).
   - **Questions** — every open blocker in ONE interactive checklist.
   - **Approval** — the final gate tab: "approve to begin build".
4. **Signature animation — the old→new diff.** This is plan's killer move: show the change
   *as motion*. Default to an A/B toggle whose panes tint **`.diff-add` (green +) / `.diff-rem`
   (red −)** — 80% of the legibility at 10% of the risk. For a genuinely structural refactor,
   reach for `morphDiff(scene, toNodes)` so surviving nodes slide, removed fade, added appear.
5. **Update live** — re-edit the same file as the plan evolves; tell him to refresh.

## When NOT to use
- Trivial, single-file, or one-line changes — just do them.
- Work the normal PRD / Algorithm path already covers.
- Explaining something that already exists → use `explain`. Teaching a concept → use `teach`.
