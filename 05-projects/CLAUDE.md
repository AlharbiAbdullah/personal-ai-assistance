# 05-projects/ — Project Management

Three lifecycle stages:
- `kitchen/`   — project exists ONLY here. PRDs, architecture, design, planning.
                 No code anywhere yet. The meal being prepared.
- `active/`    — project is active. A folder per project holds non-code artifacts
                 (design iterations, decisions, research, meeting notes).
                 Code lives in `~/projects/{project}/` outside helm.
- `completed/` — project done. One folder per project: `retrospective.md` + diagrams/.

See `projects-moc.md` for the current project inventory.

## Project naming
Lowercase with dashes: `my-project-name`. Short, descriptive, no spaces.

## Lifecycle
1. Idea graduates from `09-ideas/` (Tree → Graduated).
2. Create `kitchen/{name}/` and iterate: PRD, architecture, design.
3. When ready: create `~/projects/{name}/` (outside helm), move planning docs with
   the code, create `active/{name}/` for ongoing non-code work.
4. When done: create `completed/{name}/` with retrospective + diagrams. Remove the
   active folder.

## What Claude does
- "graduate X to kitchen" → create `kitchen/{name}/` with initial PRD.
- "start project X in active" → create `active/{name}/` (minimal; no Brief or Kanban).
- "complete project X" → create `completed/{name}/`, write retrospective, move diagrams.
- No auto-generated Brief.md, Kanban.md, or master board. Those patterns are retired.
