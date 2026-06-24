# Task Workflow

**Triggered by:** "do this task" / "implement {feature}" / "fix {bug}" — one unit of work
**Cadence:** Per task
**Done when:** behaviour verified, reviewed, merged to main, worktree cleaned.

A single unit of work — feature, fix, or spike — using git worktrees.

```
Worktree → Goal → Done criteria → TDD → Verify → Review → Merge → Clean
```

---

## Steps

### Setup

- [ ] Create worktree: `git worktree add ../[project]-[task] -b feature/[task]`
- [ ] `cd ../[project]-[task]`

### Define

- [ ] **Goal**: One sentence — what am I achieving?
- [ ] **Done**: How will I know it worked? (observable behavior, not "code written")

> **Decision Point**: Is the task clear enough to start?
> - Yes → continue
> - No → break it down further or clarify with stakeholder

### Build (TDD)

- [ ] Write failing test first — `/testing → tdd` (RED)
- [ ] Write minimal code to pass — (GREEN)
- [ ] Refactor — clean up while tests stay green (REFACTOR)
- [ ] Repeat RED-GREEN-REFACTOR for each behavior

> **Decision Point**: Task growing beyond original scope?
> - Capture extras as separate tasks
> - Finish current scope first

### Verify

- [ ] All unit tests pass
- [ ] Run `/testing → e2e` if integration points exist
- [ ] Run `/security → security-review` if auth, input handling, or data access changed

### Review

- [ ] Follow [[05-code-review]] checklist
- [ ] Full diff against main — no surprises
- [ ] `/git → refactor-clean` — remove dead code, unused imports

### Merge

- [ ] `/git → commit` with descriptive message
- [ ] Switch to main: `cd ../[project] && git merge feature/[task]`
- [ ] Verify tests still pass on main
- [ ] Clean worktree: `git worktree remove ../[project]-[task]`
- [ ] Delete branch: `git branch -d feature/[task]`

---

## Connections

- TDD cycle: `/testing → tdd`
- Code review gate: [[05-code-review]]
- Part of a larger project: [[01-project]]
- Debugging if something breaks: [[04-debugging]]
