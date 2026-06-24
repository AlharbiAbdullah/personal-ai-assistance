---
name: spec-driven
description: >
  Spec-Driven Development thinking mode. USE WHEN the user wants to turn a
  vague request into a rigorous spec BEFORE any code is written. Forces
  requirements clarity, constraint surfacing, task decomposition.
---

# Spec-Driven

The discipline of writing a spec before writing code. Forces clarity
upstream so downstream implementation is mechanical.

## When to use

- Feature request is vague and you're about to start coding
- Multi-step task where planning pays back on execution
- AI-assisted implementation — a spec grounds the agent
- Anywhere "we don't know what we're building yet" is a real risk

## When NOT to use

- Trivial changes (1–5 lines, obvious scope)
- Spikes / exploration where discovery is the goal
- Emergency fixes where speed > rigor

## Spec-Driven workflow

### 1. Brainstorm requirements
With the user (or yourself), answer:
- Who is the user? What's their job-to-be-done?
- What's the expected input? Output?
- What MUST work? What SHOULD work? What WON'T this do (non-goals)?
- What's the success criterion — how will we know it's working?

### 2. Surface constraints
- Performance (latency, throughput, memory)
- Compatibility (environments, versions)
- Security + compliance (what's off-limits)
- Operational (deployability, reversibility, observability)
- Team + time (who's building, by when)

### 3. List edge cases explicitly
- Empty input
- Very large input
- Invalid input
- Concurrent access
- Partial failure
- Timeout / retry behavior
- Permission denials

### 4. Decompose into tasks
- Each task < 1 day of work
- Each task has an acceptance criterion
- Tasks are ordered — dependencies explicit
- Each task is independently verifiable

### 5. Write the spec.md
Canonical structure:

```markdown
# Spec: [Feature Name]
Author: [Name] | Date: YYYY-MM-DD | Status: Draft

## 1. Purpose
[One paragraph: what + for whom + why now]

## 2. Requirements
### 2.1 Must
- [Requirement]
### 2.2 Should
- [Requirement]
### 2.3 Won't (this release)
- [Non-goal]

## 3. Acceptance criteria
- Given X, when Y, then Z
- ...

## 4. Constraints
- [Constraint 1]
- ...

## 5. Edge cases
- [Case 1] — expected behavior
- ...

## 6. Task decomposition
1. [Task] — acceptance: [criterion]
2. ...

## 7. Open questions
- [Question] — needed before [phase]

## 8. Risks + mitigations
- [Risk] → [Mitigation]
```

### 6. Review + iterate
- Walk through with someone who'd implement it — do they understand?
- Check: can you derive N different implementations that all satisfy the spec? If only 1, the spec is over-specified.
- Check: could two people read this and build incompatible things? If yes, under-specified.

### 7. Execute against the spec
- Implement in task order
- Each task: code + test + verify against acceptance criterion
- If reality contradicts the spec, update the spec (don't drift silently)

## Why it's different from PRD

- PRD is product-facing, longer, stakeholder-focused → `/business/prds`
- Spec is technical-facing, shorter, implementer-focused → THIS
- A spec can derive from a PRD but is more concrete

## Why it's different from system design

- System design answers "how will we build this at the component level" → `/architecture/system-design`
- Spec answers "what IS the thing we're building"
- You usually do spec → system design → implementation

## Anti-patterns

- Spec becomes a wishlist — prioritize with must/should/won't
- Jumping to solution before requirements settle
- Acceptance criteria that are implementation details ("use Redis cache") vs outcomes ("read latency < 50ms p95")
- Skipping edge cases — they become prod bugs
- One monolithic task — doesn't help decomposition
- Writing the spec then ignoring it during implementation

## Working with AI

Spec-driven is especially powerful with AI coding assistants:
1. You + human collaborate on the spec
2. AI implements task by task against the acceptance criteria
3. AI's work is verifiable (each task has a criterion it must meet)
4. Drift is contained — if AI invents requirements, you catch it by comparing to spec

## Examples

- "Write a spec for the OpenKit compliance scan feature"
- "Turn this vague Helios request into a spec before we code"
- "Spec-driven breakdown for the ChromaDB memory rewrite"
- "Generate acceptance criteria for the Matchbox API v2"
