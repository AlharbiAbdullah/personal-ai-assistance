# Project Workflow

**Triggered by:** "new project" / "build {idea} from scratch" / "start the {idea} project"
**Cadence:** Per project
**Done when:** shipped, retrospective written in `completed/{name}/`, active folder removed, inventory + index refreshed.

Full lifecycle from first spark to shipped product.

```
Idea → Kitchen → Architecture → Init → Build (phases) → Ship → Retro
```

---

## Steps

### Phase 1: Crystallize the Idea

- [ ] Capture the spark in `09-ideas/` as a [[Seed]] (`/ideas → start-seed`)
- [ ] Iterate with LLMs — clarify the problem, not the solution
- [ ] Move to [[Plant]] then [[Tree]] — research, scope, plan (`/ideas → promote`)
- [ ] Graduate — idea spawns a project (`/ideas → graduate` → `kitchen/{name}/`)

> **Decision Point**: Is this worth building?
> - Yes → continue to Phase 2
> - Not yet → leave as Tree, revisit next weekly review
> - No → leave the idea at its stage. Ideas never die (`09-ideas/CLAUDE.md`); lineage carries forward.

---

### Phase 2: Kitchen (Planning)

- [ ] Follow [[03-kitchen]] workflow
- [ ] Write PRD (problem, scope, success metrics)
- [ ] Write SPEC (architecture, components, data models, tech stack)
- [ ] Iterate until zero open questions
- [ ] Exit kitchen with clear PRD + SPEC

---

### Phase 3: Architecture Review

- [ ] Run `/architecture → solution-architect` against the SPEC
- [ ] Run `/architecture → data-architect` if a data layer is involved
- [ ] Validate separation of concerns in the proposed structure
- [ ] Confirm tech stack choices

> **Decision Point**: Architecture feedback
> - Clean → continue
> - Issues found → revise SPEC, re-review

---

### Phase 4: Project Setup

- [ ] Create code directory: `~/projects/[project-name]/` (outside helm)
- [ ] Move planning docs from `kitchen/[project-name]/` into the code repo
- [ ] Run `/project-init` — generates skeleton, CLAUDE.md, hooks, skills
- [ ] Create `05-projects/active/[project-name]/` for ongoing non-code work (minimal — no Brief or Kanban; those patterns are retired)
- [ ] Add the project to the `05-projects/projects-moc.md` inventory
- [ ] Initial commit in the code repo: `/git → commit`

---

### Phase 5: Build in Phases

Each phase is a logical chunk. Each task within a phase follows [[02-task]].

- [ ] Break project into 3-7 phases (from SPEC)
- [ ] For each phase:
  - [ ] Create git worktree: `git worktree add ../[project]-[phase] -b feature/[phase]`
  - [ ] Complete tasks using [[02-task]] workflow
  - [ ] Merge phase branch to main
  - [ ] Log progress in `05-projects/active/[project-name]/`
- [ ] Run `/testing → e2e` after each phase merges

> **Decision Point**: Scope creep detected?
> - Capture new requirements as ideas in `09-ideas/`
> - Do NOT fold them into the current build unless critical

---

### Phase 6: Ship

- [ ] Follow [[06-shipping]] workflow
- [ ] Pre-ship checklist (tests, review, README, version)
- [ ] Deploy + post-deploy verification

---

### Phase 7: Retrospective

- [ ] Write `05-projects/completed/[project-name]/retrospective.md` (move diagrams alongside)
- [ ] Update `05-projects/projects-moc.md` — mark the project done
- [ ] Remove the `active/[project-name]/` folder
- [ ] Run `/map-updater` if the project produced reusable vault knowledge
- [ ] Commit the code repo with `/git → commit`. Vault edits stay **local** for the Linux coordinator (single-writer — `03-rai/SYNC-ARCHITECTURE.md`).

---

## Connections

- Kitchen details: [[03-kitchen]]
- Task-level work: [[02-task]]
- Shipping: [[06-shipping]]
- Project lifecycle: `05-projects/CLAUDE.md`
- Idea pipeline: `/ideas` skill group
