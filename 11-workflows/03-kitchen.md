# Kitchen Workflow

**Triggered by:** "plan {project}" / "write the PRD/SPEC" / "graduate this idea"
**Cadence:** Per project (planning phase)
**Done when:** PRD + SPEC finalized with zero open questions, code repo created, build handed to [[01-project]] Phase 5.

The gap between "graduated idea" and writing code. Plan thoroughly here so building is fast later.

```
PRD → SPEC → Iterate → Zero open questions → Exit kitchen
```

---

## Steps

### Entry

- [ ] Idea has reached `graduated` status in `09-ideas/`
- [ ] Create folder: `05-projects/kitchen/[project-name]/`
- [ ] Create `README.md` — project overview (who, what, why)

### PRD (What Are We Building?)

- [ ] **Problem statement** — what pain are we solving?
- [ ] **Scope** — what's in, what's explicitly out
- [ ] **Success metrics** — how do we know it worked? (measurable)
- [ ] **User stories** — who uses it, what do they do, what do they get?
- [ ] **Constraints** — time, budget, tech, regulatory

> **Decision Point**: Is the problem worth solving?
> - Yes → continue to SPEC
> - Unclear → go back to Plant stage, research more (`/ideas → promote`)
> - No → stop; capture the learning. The idea stays in `09-ideas/` at its stage (ideas never die).

### SPEC (How Will We Build It?)

- [ ] **Architecture** — high-level system diagram
- [ ] **Components** — what modules/services, their responsibilities
- [ ] **Data models** — entities, relationships, storage
- [ ] **Tech stack** — languages, frameworks, infrastructure (justify choices)
- [ ] **APIs** — interfaces between components
- [ ] **Security** — auth, access control, data protection
- [ ] Run `/architecture → solution-architect` to validate the architecture
- [ ] Run `/architecture → data-architect` if the data layer is significant

### Iterate

- [ ] Read PRD + SPEC back-to-back — do they tell a coherent story?
- [ ] List all open questions
- [ ] Resolve each one (research, prototype, or decision)
- [ ] Update docs after each resolution

> **Decision Point**: Zero open questions?
> - Yes → exit kitchen
> - No → keep iterating

### Exit Kitchen

- [ ] PRD and SPEC are finalized
- [ ] Create code dir: `~/projects/[project-name]/` (outside helm)
- [ ] Move all planning docs from kitchen into the code repo
- [ ] Run `/project-init` to generate the project skeleton
- [ ] Create `05-projects/active/[project-name]/` for ongoing non-code work (minimal — no Brief/Kanban)
- [ ] Delete the kitchen folder
- [ ] Continue with [[01-project]] Phase 5 (Build)

---

## Kitchen Contents

```
kitchen/[project-name]/
├── README.md         ← Project overview
├── PRD.md            ← Product requirements
├── SPEC.md           ← Technical specification
├── ARCHITECTURE.md   ← System design (optional)
└── TASKS.md          ← Initial task breakdown (optional)
```

---

## Connections

- Full project lifecycle: [[01-project]]
- Project folder structure: `05-projects/CLAUDE.md`
- Architecture patterns: `/architecture → patterns`
- Templates: `12-system/templates/PRD.md`
