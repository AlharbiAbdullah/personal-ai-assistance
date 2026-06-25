---
name: teach
description: >
  Teach a concept so John genuinely LEARNS it — not just understands it once. A single
  self-contained animated HTML file that forces prediction, retrieval, and forced build-up,
  with predict-then-reveal diagrams (ghost→solid, wrong guess flashes red). Light/dark
  toggle, Excalidraw-style diagrams. Invoked via /visual router. Use when John says
  "visual teach" / "teach me X visually".
---

# /visual · teach

Teach a concept in a **single self-contained HTML file** so the reader can *do* something
afterward — not just nod along. The difference from `explain`: teach makes the learner
**generate, predict, and retrieve** rather than passively receive. The interaction *is* the
learning; the animation *is* the explanation of a process unfolding.

Built on evidence-based mechanisms — generation effect, prediction-error, retrieval practice,
worked-example→completion fading, desirable difficulty, misconception confrontation.

## How John uses it
1. He wants to actually learn something — a concept, an algorithm, a system's mental model.
2. He says **"visual teach"** (or "teach me X visually").
3. You **create the HTML** that walks him from zero, making him predict and retrieve along the way.
4. He works through it top to bottom (the order is the lesson).

## Build it (from `references/engine.html` — see the router's Engine API)
1. **Get it correct first.** A teaching artifact that teaches a wrong model is worse than none.
   Ground in the real thing; verify the mental model before drawing it.
2. **Clone the engine**, set `<body data-nav="scroll" data-skill="teach">`. **Scroll = forced
   build-up** — no skipping ahead; each section's diagram draws on as it enters view.
3. **Fill the sections** as a ramp (rename/drop to fit):
   - **Hook + misconception** — "You probably think…" then set up to watch it break.
   - **Build-up** — the diagram **assembles one relationship at a time**, each with a one-line caption.
   - **Worked example → completion → solo** — same diagram, decreasing scaffolding.
   - **Retrieval checkpoints** — short questions *between* sections, not piled at the end.
   - **Self-explain prompts** — ask for the reason before revealing the canonical one.
   - **Self-check** — the recap as active recall.
4. **Signature interaction — predict-then-reveal.** Before each key reveal, the learner commits
   a guess via `.chip[data-correct]`; only then does the truth `drawOn`. A wrong guess flashes
   red + shakes, then the correct path draws green — the **prediction-error contrast is the
   teaching moment**. For misconceptions, send a `flowDot` to the WRONG node, flash red, then
   redraw the correct path green.
5. **Pacing & escape hatch.** Keep gating *light* — predict-then-reveal already supplies the
   desirable difficulty; don't blur whole sections shut by default. Offer a "reveal all" so
   re-reads aren't punished. Teach-specific interaction logic lives in the teach HTML, not the
   shared engine, so plan/explain stay lean.

## When NOT to use
- He just needs to *understand* it once, as reference → use `explain`.
- Planning a feature → use `plan`.
- The concept is trivial — prediction/retrieval would be busywork.
