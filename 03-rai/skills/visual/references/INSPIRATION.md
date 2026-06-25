# /visual — inspiration & build backlog

Distilled from a 9-lens deep-research sweep (66 patterns) on how people actually build
interactive HTML/visual explainers. Sources mined: Bret Victor (Tangle, "Explorable
Explanations", "Ladder of Abstraction"), Nicky Case (Parable of the Polygons, Going Critical),
Quantum Country / mnemonic medium (Matuschak + Nielsen), The Pudding / NYT scrollytelling,
Scrollama + CSS scroll-driven animations + View Transitions API, RoughNotation, rough.js seeds,
GSAP/Motion-One/WAAPI, CSS `linear()` springs, "You-Draw-It" (NYT), driver.js spotlights,
Claude Artifacts / generative-UI, Awwwards editorial design.

## North star
Explainers should be **interrogable, not just animated** — the reader pokes a parameter and the
hand-drawn diagram answers; the explainer points at what it's narrating; and it reads like a
premium editorial piece on real paper. Passive → manipulable; pretty → guided; static → alive.

## Built (this pass)
1. **Stable rough seeds** — per-id deterministic seed so a diagram can be *redrawn on every tweak
   without "boiling"*. The foundation for all interactivity.
2. **Reactive widgets — `slider()` + `tweak()` + `reactive()`** — drag a slider or a dashed inline
   number → live `recompute()` → the rough scene + bound numbers repaint. (Tangle / Parable of the Polygons.)
3. **Sketch-in annotations — `annotate(scene,node,{type,note})`** — rough circle / underline / box /
   arrow + a Kalam margin note that draws on at its narrative beat. (RoughNotation / annotation-as-narrative.)
4. **Spring easing via CSS `linear()`** — zero-lib spring/overshoot eases applied across transitions; plus a JS spring tween.
5. **Paper-grain texture + fluid editorial type scale (clamp) + reading measure** — ink-on-paper feel, premium reading.
6. **Path-following flow-dot** — the packet rides the *actual* rough stroke via `getPointAtLength()` (curves and all).

## Backlog (high-value, not yet built)
- **Scrollytelling mode (`data-nav="scrolly"`)** — sticky rough stage + scroll steps; `onStepProgress(0..1)`
  interpolates flow-dot / count-up / dim continuously. The single most-cited real-world pattern (Pudding/NYT). **Next.**
- **Seed-reroll "magic move" morph** — upgrade `morphDiff` to a true matched before/after with preserved
  seeds + strokes-in/un-draw + spring (show structural change on-aesthetic).
- **Mnemonic recall cards** — spaced-repetition flip cards after teach sections, expanding-interval due dates in localStorage. (Quantum Country.)
- **You-Draw-It / Place-your-bets (draw gesture)** — reader sketches a predicted curve/path; truth animates on top with a hachure delta band. (NYT.)
- **Embedded tiny simulation — `sim(scene,{tick,draw})`** — live agent glyphs over the static rough structure (emergence/tipping points). (Going Critical.)
- **Copy-as-prompt round-trip + sandbox graduation** — serialize step/slider/prediction state to a paste-ready prompt; end by unlocking free-play. (The 2025-26 artifact move.)
- **SVG cutout spotlight** bound to the Play tour/scroll (hand-drawn driver.js backdrop).
- **View Transitions API** for super-node expand/collapse + layer swaps (native GPU crossfade, graceful no-op).
- **Hachure node fills** (vs solid) with stable seeds; optional subtle **line-boil** on the hot node only (opt-in, reduced-motion off).

## Cut (deliberately not building)
- Always-on ambient "breathing"/line-boil everywhere — decoration, motion-sickness, first thing reduced-motion kills.
- Heavy chart libraries (D3 bundle) — off-aesthetic and overkill; hand-draw the few charts we need.
- Sound / haptics — novelty, not comprehension.
