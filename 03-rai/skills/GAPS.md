# Skills GAPS

Open inbox of things not yet done. This file gets drained as items ship
and augmented when new gaps surface.

---

## Resolved in 2026-04-22 Big Reorg

Most of what was in this file shipped:

### Missing skills — DONE
- Business specializations: prds, proposals, presentations, pricing ✓
- Research specializations: competitor, literature, market, academic ✓
- Coding standards: typescript, go, rust ✓ (python already existed)
- Infrastructure: kubernetes, ci-cd, monitoring ✓
- Testing: pragmatic, load-test, code-review, verify-completion, dependency-audit, tech-debt-map ✓

### Missing within existing skills — DONE
- `sanity` Tier F5 + F6 (template integrity, hooks failure-log) ✓
- `sanity` full end-to-end extension: E5, F7, F8, Tier I (algorithm + agents), Tier J (skills deep + hook firing + lib imports), Tier K (work state + counts + protection + MCP) ✓
- `content-analysis/fabric` find-pattern workflow ✓
- `investigation` combo sub-skill (person + infra sequencing) ✓
- `think` mode-chaining + when-not-to-use ✓
- `media/remotion` external services — NOT DONE (still deferred; below)
- `testing/e2e` external-service mocking ✓
- `testing/api-test` + `e2e` load testing — DONE via `/testing/load-test` ✓
- `data-architect` streaming — DONE via new `/data/streaming` ✓
- `docker` multi-arch + secrets ✓
- `solution-architect` microservices, event-driven, saga, compliance ✓

### New tooling — DONE
- `skill-validator.py` — inlined into `rai/sanity` Tier J1-J3 (walks all `skills/*/SKILL.md` + sub-skills, validates frontmatter + name/folder match + collisions + MANIFEST drift). Kept inline rather than extracting to a script — matches the existing self-contained pattern of sanity tiers ✓
- `.pai-protected.json` stale exception entry — verified by `rai/sanity` Tier K3, which loads every pattern, compiles them, and runs positive/negative smoke tests ✓

### Deletions — DONE
- `aphorisms` merged into `life/quote` + deleted ✓
- `rai-upgrade` moved to `/rai/upgrade` with 90-day tombstone (reconsider 2026-07-22)

---

## Still deferred (next deep-work block)

### Big content rewrites
- **`recall/history`** (592 lines): compress ~70% repeated py-chroma.sh templates into 1–2 parameterized templates.
- **`news-digest`** (681 lines): resolve v3 vs v4.3 version drift; factor ~150 lines of CSS-inject + scroll + extract repeated across X/Substack/Medium into one reusable template.

### New tooling
- **AI sub-skills — defer until proven by use**: `eval-harness`, `prompt-patterns`. Add to `/ai/` only after manual use demonstrates the need.

### Cross-cutting polish
- **Algorithm spec drift — PRD.md vs META.yaml**: the Algorithm `latest` spec references `memory/work/{slug}/PRD.md` but current hooks write `META.yaml`. Sanity K1 checks reality (META.yaml) and I2 surfaces doc drift. Separate session to align spec + hooks.
- **Security authorization format**: standardize the authorization block across `security/prompt-injection`, `security/web-assessment`, and `investigation/*`. Pick one canonical phrasing ("written approval via email/ticket stating target + scope + explicit go-ahead") and propagate.
- **`media/remotion`** external-service integration: rendering with audio, TTS, stock footage libraries. Not in scope today.

---

## Future additions (not scheduled)

### Language additions
- **`coding-standards/swift`** — add when Swift becomes a recurring language (iOS, macOS native)

### New potential routers
- **`/linux/`** — Linux/Omarchy-specific tooling. Add when John commits to Omarchy as daily driver.
- **`/observability/` or split from devops** — if monitoring + logging + tracing grow beyond 3 sub-skills.

### Enhancement ideas
- Router SKILL.md for business, research, data: expand routing tables as new sub-skills land.
- `investigation/combo` workflow sub-skill: create after 3+ invocations if value is clear.
- Weekly cross-session synthesis skill: `/recall/synthesize` (bridge unnamed patterns across notes + sessions). Promote from planned to real when needed.

---

## Tombstones (delete if not invoked)

| Skill | Deadline | Decision |
|---|---|---|
| `rai/upgrade` | 2026-07-22 | Delete if not invoked in 90 days |
| `/ai/` (both sub-skills) | 2026-06-22 | Review usage; delete if no uses; do NOT add more sub-skills without 3 manual uses each |

---

## How this file works

- Items here are not yet scoped or scheduled
- Promote with `/rai/create-skill` when ready to build
- Resolved items move to "Resolved" section above, then eventually archived out of this file
- New gaps found during deep-work passes get appended here
