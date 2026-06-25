---
name: data
description: >
  Explain a dataset, schema, or data model visually as a single self-contained animated HTML file —
  hand-drawn ER/record cards, the medallion/layer flow (e.g. DuckLake bronze→silver→gold),
  relationships, and key field semantics. Light/dark toggle. Invoked via /visual router. Use when
  John says "visual data" / "explain this schema/dataset/pipeline visually".
---

# /visual · data

Make a dataset or data model graspable — in a **single self-contained HTML file**. Hand-drawn
record cards for tables, edges for relationships, and a layered flow for how data moves through
the medallion (bronze → silver → gold) or any pipeline. A focused cousin of `explain`, tuned for
schemas, ER diagrams, and lineage.

## How John uses it
1. He needs to see a dataset's shape — a schema, an ER model, a pipeline's layers, lineage.
2. He says **"visual data"** (or "explain this schema/dataset/pipeline visually").
3. You build the HTML: the tables, their links, the layer flow, the field semantics.
4. He reads the model, follows a column from source to gold, flips light/dark.

## Build it (from `references/engine.html` — see the router's Engine API)
1. **Read the real schema first.** Tables, columns, types, keys, the actual transforms between
   layers. Ground every card and edge — a data diagram that misstates a key is actively harmful.
2. **Clone the engine**, set `<body data-nav="tabs" data-skill="data">`. Tabs = jump to a table
   or a layer; use `scroll` if you're narrating source→gold as one story.
3. **Fill the sections** (rename/drop to fit):
   - **The model** — what this data represents + the one thing to know (grain, key entity).
   - **Tables / entities** — `graph()` nodes as record cards; edges = FK relationships. Turn on
     `legend()` keyed by layer/domain and **focus+context** so a busy ER stays readable.
   - **The flow** — the medallion/pipeline as a **layered build-up** (bronze → silver → gold,
     one tier at a time) or a flow diagram with a `flowDot` tracing one row's journey.
   - **Key fields** — the columns that carry meaning (joins, partitions, the gotcha nullables),
     with **semantic zoom** to expand a table into its columns.
   - **Counts** — row counts / cardinalities with the **count-up** metric for the "real system" feel.
4. **Ground it in the real project where relevant.** Read the actual schema, catalog, and
   storage layer first (e.g. Postgres tables, a warehouse's medallion layers, a Parquet/lake
   catalog) and use the real layer and table names — never invent a structure that isn't there.

## When NOT to use
- A single `CREATE TABLE` or a one-line schema note answers it — just paste/say it.
- Explaining non-data system behavior → use `explain`. Planning a schema change → use `plan`.
