---
name: compare
description: >
  Compare two-or-more options (tools, libraries, architectures, approaches) head-to-head as a
  single self-contained animated HTML file — side-by-side hand-drawn diagrams, a scored trade-off
  matrix, and a clear recommendation. Light/dark toggle. Invoked via /visual router. Use when
  John says "visual compare X vs Y" or is weighing options and wants them laid out visually.
---

# /visual · compare

Lay N options side by side so the choice is obvious — in a **single self-contained HTML file**.
Where `explain`'s A/B toggle compares two states of *one* thing, `compare` is built for a
**decision**: each option gets its own diagram, the criteria become a scored matrix, and the
artifact ends on a recommendation with its reasoning.

## How John uses it
1. He's weighing options — tools, libraries, architectures, vendors, approaches.
2. He says **"visual compare X vs Y"** (or "lay these out").
3. You build the HTML: each option diagrammed, scored against shared criteria, with a clear pick.
4. He scans the matrix, flips light/dark, drills into any option.

## Build it (from `references/engine.html` — see the router's Engine API)
1. **Get the facts straight first.** Each option's real shape, trade-offs, and constraints —
   no strawman of the one you're not picking. A dishonest comparison is worse than none.
2. **Clone the engine**, set `<body data-nav="tabs" data-skill="compare">`. Tabs let the reader
   jump straight to the option (or the matrix) they care about.
3. **Fill the sections** (rename/drop to fit):
   - **The decision** — what's being chosen and the criteria that matter (weighted if relevant).
   - **Option A / Option B / …** — one tab each: a `graph()` of that option + its 1-line essence.
     Use the **A/B toggle** or **semantic zoom** to drill into an option's internals.
   - **Scorecard** — a styled table: criteria × options, each cell scored; use `.diff-add` /
     `.diff-rem` glyphs and color (never color alone) so wins/losses read at a glance. Animate
     the totals with the **count-up** metric.
   - **The pick** — the recommendation, *why*, and the conditions under which you'd choose differently.
4. **Signature feel — the side-by-side.** The payoff is seeing the options' diagrams in the same
   visual language; keep them structurally parallel so differences pop. Optional: a single A/B
   toggle that swaps the two architectures in place to highlight what actually changes.

## When NOT to use
- One option clearly dominates — just say so. A comparison would be theater.
- Explaining how one existing thing works → use `explain`. Planning to build one → use `plan`.
