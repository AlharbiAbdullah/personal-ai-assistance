---
name: visual-plan
description: >
  USE WHEN John is in plan mode for a new feature or a messy multi-file task
  and says "use visual plan". Builds and live-updates a single self-contained
  HTML file — interactive diagrams, tabbed sections, clickable wireframes,
  togglable UI states — saved in the project's own `visual-plan/` folder. The
  HTML *is* the plan and the approval gate before any code is written. Occasional
  use. Deliberately separate from the Algorithm/PRD flow.
---

# Visual Plan

Plan a feature in a **single self-contained HTML file** you open in a browser —
not chat prose, not Markdown. HTML because it opens the gate: interactive Mermaid
diagrams, tabs, collapsibles, clickable wireframes, **togglable UI states**, even
live prototypes. One double-click to open, zero build step, zero infra.

Adapted from BuilderIO's `visual-plan` — the idea, not their hosted stack.
Reach for it **occasionally**, when a feature is messy enough that a visual,
interactive plan beats prose. It does **not** touch `memory/work/.../PRD.md` or
the Algorithm phases — it is its own thing.

## How John uses it
1. He's building a new feature and switches to **plan mode**.
2. He says **"use visual plan"**.
3. As you both plan, you **create and live-update the HTML file**. The HTML is
   the living plan — every diagram, decision, and open question lands in it.
4. He opens the file in a browser, reviews, comments.
5. **He approves the plan → only then does code begin.**

## Hard rules
1. **It must be beautiful.** This is the bar, not a nice-to-have — refined
   typography, generous spacing, a warm muted-dark canvas (soft foreground, no
   stark white). A plain or boxy plan fails the brief.
2. **Diagrams are Excalidraw-style, never Mermaid.** Hand-drawn look via rough.js
   (Excalidraw's own engine) + the Kalam font, already wired into the template's
   `graph()` helper. Sketchy strokes, warm accent colors, hand-drawn labels.
3. **No source-code edits while the plan is being built or reviewed.** The only
   file you write is the plan HTML under `visual-plan/`. The plan is the approval
   gate; editing source begins only after John approves the direction.

> Note on strict plan mode: Claude Code's strict plan mode blocks *all* file
> writes, including this HTML. To live-update the file as you plan, work in
> normal mode and let this rule be the gate — you touch only `visual-plan/*.html`
> until approval. (If he insists on strict plan mode, the HTML is written at each
> ExitPlanMode checkpoint instead of continuously.)

## Where it lives
A `visual-plan/` folder at the **root of the project**, one HTML file per feature:

```
<project-root>/
└── visual-plan/
    └── <feature-slug>.html
```

Example (the worked sample): `04-work/helios/visual-plan/citations-grounding.html`.
The plan is disposable — delete it once the feature ships (git log is the archive).

## Building the file
1. **Inspect first** — read the real files, schemas, and symbols. Ground every
   diagram and file reference in what actually exists in the project.
2. **Clone the skeleton** — start from `references/template.html` (theme, `graph()`
   rough.js engine, tab + checklist JS already wired). Self-contained: inline CSS,
   rough.js + Kalam via CDN. Keep the warm muted-dark theme.
3. **Fill the sections** (tabs in the template):
   - **Overview** — prose-first outcome (what + why), at-a-glance decisions, build sequence.
   - **Architecture** — hand-drawn `graph()` of components & deps (nodes + edges).
   - **Flow** — hand-drawn `graph()` of the runtime path (numbered steps).
   - **Data** — a hand-drawn rough.js record card, or a styled table.
   - **UI** — clickable wireframe; use HTML state toggles to show design options live (this is *why* HTML).
   - **Decisions** — trade-off cards (note / warning).
   - **Questions** — every open blocker in ONE interactive checklist at the end.
4. **Update live** — re-edit the same file as the plan evolves. Tell him to refresh the browser.

## When NOT to use
- Trivial, single-file, or one-line changes — just do them.
- Work the normal PRD / Algorithm path already covers.

## Rendering notes
Opens in any browser by double-click — no server, no build. rough.js and the
Kalam font load from a CDN, so **diagrams + the hand-drawn font need internet**;
text, layout, wireframes, toggles, and checklist persistence all work offline.
True MDX / a shared component library stays **deferred** — single-file HTML
covers it. (To preview without file:// quirks, `python3 -m http.server` in the
`visual-plan/` folder also works.)
