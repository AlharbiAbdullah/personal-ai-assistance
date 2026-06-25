---
name: visual
description: >
  Visual explainer router. USE WHEN John wants something rendered as a single
  self-contained, animated, beautiful HTML file he opens in a browser — with a
  light/dark toggle and Excalidraw-style hand-drawn diagrams. Routes between six
  sub-skills: plan (plan a NEW feature; the HTML is the approval gate), explain
  (explain something that ALREADY exists), teach (teach a concept so he LEARNS it),
  compare (weigh options head-to-head), trace (walk a bug/incident/request path),
  data (explain a schema/dataset/pipeline). All share ONE engine (references/engine.html).
  Triggers: "visual plan/explain/teach/compare/trace/data", "explain this visually".
---

# Visual

Turn an idea into a **single self-contained HTML file** — double-click to open, zero
build step, zero server. Animated hand-drawn diagrams, a light/dark toggle, and rich
interaction. Six sub-skills, one shared engine.

## Routing table

| Task | Sub-skill | File to Read |
|------|-----------|--------------|
| Plan a NEW feature / messy multi-file change; the HTML *is* the approval gate before code | plan | `plan.md` |
| Explain something that ALREADY exists (a system, codebase, concept, decision) | explain | `explain.md` |
| Teach a concept so the reader genuinely LEARNS it (predict / retrieve / build-up) | teach | `teach.md` |
| Weigh two-or-more options head-to-head; needs a scored matrix + a pick | compare | `compare.md` |
| Walk a bug / incident / request lifecycle; pulse to the failure point + timeline | trace | `trace.md` |
| Explain a schema / dataset / data model / pipeline (ER, medallion layers, lineage) | data | `data.md` |

## How to use

1. Pick the sub-skill by intent (see the routing table + disambiguation below).
2. `Read` that file in this directory.
3. Build the HTML by cloning `references/engine.html` (see **The engine** below) and following the sub-skill's spec.

## When two could fit
- **plan vs explain:** plan argues a *future* state and gates code (no source edits until approved). explain describes a *present* state — no gate, usable anytime.
- **explain vs teach:** explain makes you *understand* (random-access reference). teach makes you *able to do it* — it forces you to predict and retrieve, in a forced build-up order. If there's a quiz, it's teach.
- **explain vs compare:** explain unpacks *one* thing; compare puts *several* side by side and ends on a recommendation.
- **explain vs trace:** explain shows steady-state behavior; trace follows *one specific* run/bug to where it went wrong (failure node + timeline).
- **explain vs data:** data is explain specialized for schemas/datasets — record cards, FK edges, medallion layers, lineage.

## Hard rules (all sub-skills)
1. **It must be beautiful.** Refined type, generous spacing, calm canvas in *both* themes (gruvbox dark + light). A plain or boxy result fails the brief.
2. **Diagrams are Excalidraw-style, never Mermaid.** Hand-drawn via rough.js + Kalam, through the engine's `graph()`. Sketchy strokes, warm accents, hand-drawn labels.
3. **Animation must aid understanding, not decorate.** Every motion earns its place: it draws the eye to what just appeared, traces a real path, or shows a real change. No ambient "breathing".
4. **Ground it in reality.** Explaining/planning code → read the real files, schemas, symbols first; every box and arrow maps to something real. Teaching a concept → get it correct, no diagrams implying a structure that isn't true.
5. **Light/dark toggle + reduced-motion are non-negotiable** and already wired into the engine — don't break the re-render path or the `prefers-reduced-motion` handling.

## The engine — `references/engine.html`

ONE shared file is the source of truth for all three sub-skills (this is deliberate —
three hand-synced templates would drift). Clone the whole file, then:

- Set `<body data-nav="…" data-skill="…">` — `data-nav` picks the navigation paradigm
  (`tabs` random-access · `scroll` forced linear build-up · `deck` slides), `data-skill`
  is `plan|explain|teach|compare|trace|data` (drives the badge/footer).
- Replace `{TITLE}` / `{SUBJECT}` / `{DATE}`, fill or delete sections, edit `diagrams()`.
- Reach for the signature animation your sub-skill calls for.

**Engine API** (all theme-aware; all honor the global `REDUCED` guard; `build()` cancels
every running animation before redrawing, so the theme toggle never stacks loops):

| Helper | What it does |
|--------|--------------|
| `graph(id, nodes, edges, size)` → scene | Hand-drawn boxes+arrows. Each node/edge is a `<g data-node/ data-edge>` with metadata; returns `{svg, nodes, edges}`. Node `{x,y,w,h,t,s(color),g(group),f(fill)}`; edge `{a,as,b,bs,c}` (sides l/r/t/b). |
| `drawOn(scene)` | Strokes **sketch themselves in** (staggered, ~1.2s cap, click-to-skip). The shared "alive" primitive. Auto-runs on first build + on section entry. |
| `flowDot(scene, fromId, toId, opts)` | A glowing packet **rides a real edge** and lights the target node. `opts:{color,r,dur}`. |
| `focus(scene, id)` / `unfocus(scene)` | **Focus+context dim** (.4 opacity) of everything but a node + its neighbors. Wired to hover/focus automatically. |
| `legend(containerId, groups)` | Color key that doubles as a **per-role filter** (`groups:[{key,label,color}]`, matched to node `g`). |
| `morphDiff(scene, toNodes)` | **plan signature:** animate matched nodes old→new; removed fade, added appear. `toNodes:{id:{x,y}}`. |
| `predictReveal` (markup) | **teach signature:** `.chip[data-correct]` guesses → `.reveal` opens only after a guess; wrong shakes red. |
| `countUp(el)` / `runMetrics(root)` | **Cheap win:** a `.metric[data-count][data-unit]` ticks `0→N` on section entry. Hand-font feel. |
| `timeline(id, steps, onSeek)` | **Cheap win:** a draggable scrubbable ribbon (`steps:[{t,cap}]`); `onSeek(i,step)` to drive a diagram. |
| `setupBuild(svg, ctrls, cap, stages)` | **Complexity:** layered build-up — a 15-node system accrues one tier at a time (`stages:[{t,cap,nodes,edges}]`, cumulative). |
| node `{super:true}` + `#detail-<id>` | **Complexity (semantic zoom):** clicking a super-node reveals its internals panel + focuses it. |
| `minimap(svgId)` | **Complexity:** opt-in corner minimap for a tall/large diagram (call it yourself in `init`). |
| `.selfx` markup + `wireSelfExplain()` | **teach depth:** commit a written reason, *then* reveal the canonical one. |
| `.calib` markup + `wireCalibrated()` | **teach depth:** rate confidence then answer; surfaces "confident-but-wrong". |
| `slider(id, {min,max,value,label,unit,fmt,onInput})` | **EXPLORABLE:** a knob whose `onInput(v)` recomputes + redraws the scene live. (Tangle / Bret Victor.) |
| `tweak(elOrSel, {min,max,value,unit,fmt,onInput})` | **EXPLORABLE:** turn a dashed inline number into a drag-to-change handle feeding `onInput(v)`. |
| `annotate(scene, nodeId, {type,note,color})` | **Annotation-as-narrative:** rough circle/underline/box that *sketches in* + a Kalam margin note, at its beat. `clearAnnotations(scene)` resets. |
| `seedOf(id)` (auto in `graph()`) | Stable per-id rough **seed** so a scene REDRAWS on every tweak **without "boiling"** — the foundation of all interactivity. Node `{hachure:true}` for hachure fill. |

**The explorable pattern** (turn a passive diagram into an interrogable model): keep tunable values in a `STATE` object, write one `render()` that draws the scene from `STATE` (called by `diagrams()` so the theme toggle re-renders it), then wire `slider()`/`tweak()` so `onInput` mutates `STATE` → `render()`. Stable seeds keep it from boiling.

Shared chrome (free, no wiring): sticky **progress rail** (scroll-spy + jump), full
**keyboard** model (`←/→/Space` step · `1-9` jump · `.` play · `S` skip · `T` theme · `?`
cheatsheet), optional **Play** tour, **resume** chip, self-check persistence, and a
no-rough DOM fallback.

## Where outputs live
A `visual/` folder at the **root of the project**, one HTML file per artifact, named
`<slug>.html`. Disposable — regenerate anytime; git log is the archive. For a topic not
tied to a repo, save to `~/helm/00-landing/visual/`.

## Rendering notes
Opens in any browser by double-click. rough.js + Kalam load from a CDN, so diagrams +
the hand-drawn font need internet (text, layout, theme toggle, and interactions work
offline; a no-rough fallback keeps the doc readable). To preview cleanly:
`python3 -m http.server` in the `visual/` folder.

## Cross-references
- Adapted from BuilderIO's `visual-plan` — the idea, not their hosted stack.
