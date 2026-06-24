# 08 — Agents Catalog

The full agent inventory. 12 agents in two tiers: 10 specialists + 2 methodology. All run `model: opus` at `effort: xhigh`.

Every agent lives at `~/helm/03-rai/agents/{name}.md`. Plus the manifest at `~/helm/03-rai/agents/MANIFEST.md`.

## Discovery and invocation

Agents are invoked via the `Task` tool:

```
Task(subagent_type: "engineer", description: "...", prompt: "...")
```

Or via the `/Task` slash command in interactive mode. The `subagent_type` value matches the agent's `name:` frontmatter field (which matches the filename stem).

## Agent vs Skill — when to use which

| | Skill | Agent |
|---|-------|-------|
| Invocation | `Skill("name")` | `Task(subagent_type: "name")` |
| Context | Same conversation | Separate context window |
| Parallelism | Sequential by default | Easy to parallelize |
| Output | Inline | Returned to parent |
| Use case | Capability with named steps | Specialist persona for a focused subtask |
| Lifetime | Single invocation | Single invocation (or background-running) |

Use a skill when the work fits in the current conversation. Use an agent when you want isolation, parallelism, a different model, or a specialist persona.

## Tier 1 — Specialists (10 agents)

Each specialist has a domain. They are the experts you delegate to.

### architect

**Path:** `03-rai/agents/architect.md`
**Model:** opus
**Scope:** Distributed systems, architecture decisions, trade-off analysis, long-term planning. Constraints-first thinking.

**When to invoke:**
- Designing a non-trivial system (microservices, event-driven, data pipelines).
- Comparing architectural approaches with trade-off rigor.
- Writing or reviewing an ADR.
- Planning a migration that needs explicit constraints.

**Example:**
```
Task(subagent_type: "architect",
     description: "Design event flow for orders service",
     prompt: "We need an event-driven order pipeline. Inputs: REST POST /orders. Outputs: 
              order-created, inventory-reserved, payment-initiated events. Backing: Kafka 
              (we already use it). Idempotency required. Design the event schema, the 
              consumer topology, and identify the trade-offs.")
```

### engineer

**Path:** `03-rai/agents/engineer.md`
**Model:** opus
**Scope:** Production-grade implementation. TDD. Tests-first. Type-safe. Strategic planning.

**When to invoke:**
- Implementing a feature with quality bars (production code, not throwaway).
- Refactoring with full test coverage.
- Building something where types matter.
- Strategic planning before a substantial code change.

**Example:**
```
Task(subagent_type: "engineer",
     description: "Implement user-deletion flow with tests",
     prompt: "Add a user-deletion endpoint to the users service. Requirements: 
              soft-delete only, audit log entry, cascade to user's sessions, 
              return 204 on success. Tests required: success path, idempotency, 
              authorization failure, cascade verification.")
```

### designer

**Path:** `03-rai/agents/designer.md`
**Model:** opus
**Scope:** UX/UI design. WCAG 2.1 AA accessibility. Design systems. Visual hierarchy, spacing, color, interactions.

**When to invoke:**
- Reviewing a UI for accessibility, hierarchy, spacing.
- Building a component with explicit interaction states.
- Designing a flow with clear visual structure.
- Accessibility audit.

### pentester

**Path:** `03-rai/agents/pentester.md`
**Model:** opus
**Scope:** Authorized penetration testing, vulnerability assessment, security auditing. Strict authorization requirements.

**When to invoke:**
- Pentest engagement on a system John owns or has explicit authorization for.
- CTF challenges.
- Security research with defined scope.
- Defensive use cases (testing your own code).

**Authorization required.** Will refuse if scope is unclear.

### qa-tester

**Path:** `03-rai/agents/qa-tester.md`
**Model:** opus
**Scope:** Edge case hunting from user perspective (not developer perspective). Evidence-based PASS/FAIL.

**When to invoke:**
- Validating a feature from a user POV.
- Finding edge cases the developer missed.
- Final QA gate before declaring done.
- Producing a PASS/FAIL report with evidence.

**Difference from reviewer:** qa-tester thinks like a user; reviewer thinks like a developer reading code.

### reviewer

**Path:** `03-rai/agents/reviewer.md`
**Model:** opus
**Scope:** Code review, bug catching, security issues, edge cases. Tests must pass before approval.

**When to invoke:**
- Reviewing a PR or local diff.
- Independent second-opinion on code.
- Bug hunt in existing code.
- Pre-merge gate.

### artist

**Path:** `03-rai/agents/artist.md`
**Model:** opus
**Scope:** Image prompt engineering for FLUX, GPT-Image-1. Illustrations, diagrams, visual assets.

**When to invoke:**
- Generating an image with prompt-engineering rigor.
- Illustrating a concept.
- Diagram authoring.
- Visual assets for content.

### writer

**Path:** `03-rai/agents/writer.md`
**Model:** opus
**Scope:** Prose craftsman. John's locked-in voice across Arabic (Lumen north star) and English, enforcing the shared anti-AI voice rules. Prose, not code.

**When to invoke:**
- Drafting Arabic or English prose that must read as human-written.
- Blog essays, proposals, PRDs (writing craft), social-media posts.
- Running the trio-synth workflow for serious Arabic.

**Reads the voice contract first:** `writing/references/voice.md`, `writing/arabic.md`, `writing/references/arabic-dictionary.md`.

### debugger

**Path:** `03-rai/agents/debugger.md`
**Model:** opus
**Scope:** Root-cause specialist. Reproduce, hypothesize, bisect, instrument, prove. Fixes the class of failure, not the symptom.

**When to invoke:**
- A live failure that needs the actual cause found and proven.
- A bug that resists the obvious fix.
- Flaky / intermittent behavior that needs bisecting.

**Difference from siblings:** reviewer reads a diff, qa-tester probes black-box; debugger goes inside a live failure and explains *why*. Honors the Socratic house rule when John debugs his own code — when delegated, it delivers the fix.

### sre

**Path:** `03-rai/agents/sre.md`
**Model:** opus
**Scope:** Site reliability. Keeps running systems up and diagnoses why they fell over — timers, sync, schedulers, deployments.

**When to invoke:**
- A scheduled job / timer silently didn't fire.
- The single-writer vault sync is wedged.
- An unattended pipeline (news-digest, maintenance) stalled.
- Hardening a live deployment against a recurring failure.

**Scope vs `/devops` skill:** `/devops` builds infra (Dockerfile, systemd unit, CI pipeline); `sre` keeps it running and diagnoses failures.

---

## Tier 2 — Methodology (2 agents)

Methodology agents are problem-agnostic — they encode a way of working rather than a domain.

### algorithm

**Path:** `03-rai/agents/algorithm.md`
**Model:** opus
**Scope:** Structured 7-phase problem-solving via Ideal State Criteria (ISC).

A thin identity layer that wraps the Algorithm spec at `03-rai/algorithm/v3.7.0.md` (the `03-rai/algorithm/latest` pointer resolves to `v3.7.0.md`) for explicit invocation. Use when you want to force the Algorithm even if Rai might otherwise treat the task as trivial — or when you want the Algorithm to govern an isolated subtask.

**When to invoke:**
- Forcing structured problem-solving on a task.
- Running the Algorithm in isolation as a subtask within a larger flow.
- Algorithm-driven code review or planning.

### researcher

**Path:** `03-rai/agents/researcher.md`
**Model:** opus
**Scope:** Multi-source research synthesis. Query decomposition, parallel search, citation-backed findings.

Different from `/research` skill — the researcher *agent* runs in its own context window with its own tool budget. Use it when the research is large enough to warrant context isolation.

**When to invoke:**
- Deep research that would bloat the parent context.
- Parallel research across multiple sources.
- Synthesis report needed with citations.
- Comparative analysis (alternatives, options, vendors).

---

## Removed agents (4)

These were defined and then removed when the multi-model parallel-research pattern proved theoretical without proven demand:

- `codex-researcher`
- `gemini-researcher`
- `grok-researcher`
- `perplexity-researcher`

Can be re-added if the pattern emerges as a real need.

## Frontmatter schema

Every agent file has five frontmatter keys: `name`, `description`, `model`, `effort`, and `permissions.allow`. (There is no `tools:` key — the live files use `permissions.allow:`.) All agents pin `model: opus` and `effort: xhigh`.

```yaml
---
name: <kebab-case-name>
description: <one-line scope; used by Claude Code to choose between agents>
model: opus
effort: xhigh
permissions:
  allow:
    - "<tool>"   # per-agent allow-list — varies, see the table below
---
```

The `permissions.allow` array gates what tools the agent can call. **The allow-lists are NOT uniform** — each agent carries its own list, ranging from 5 tools (read-only validators) to the full 9-tool "everything" set. Agents can be locked down (a read-only researcher with no Bash/Write/Edit) or opened up (an architect with everything).

The nine tools that appear across the agents are: `Bash`, `Read(*)`, `Write(*)`, `Edit(*)`, `Grep(*)`, `Glob(*)`, `WebFetch(domain:*)`, `WebSearch`, `mcp__*`.

### Per-agent allow-lists

| Agent | Bash | Read | Write | Edit | Grep | Glob | WebFetch | WebSearch | mcp__* | Count |
|-------|:----:|:----:|:-----:|:----:|:----:|:----:|:--------:|:---------:|:------:|:-----:|
| architect | x | x | x | x | x | x | x | x | x | 9 |
| designer | x | x | x | x | x | x | x | x | x | 9 |
| pentester | x | x | x | x | x | x | x | x | x | 9 |
| writer | x | x | x | x | x | x | x | x | x | 9 |
| debugger | x | x | x | x | x | x | x | x | x | 9 |
| sre | x | x | x | x | x | x | x | x | x | 9 |
| artist | x | x | x | — | x | x | x | x | x | 8 |
| engineer | x | x | x | x | x | x | x | — | x | 8 |
| algorithm | x | x | x | x | x | x | — | — | x | 7 |
| researcher | — | x | — | — | x | x | x | x | x | 6 |
| qa-tester | x | x | — | — | x | x | — | — | x | 5 |
| reviewer | x | x | — | — | x | x | — | — | x | 5 |

The meaningful deviations from the full 9-tool set:

- **architect, designer, pentester, writer, debugger, sre** — the full 9-tool "everything" set.
- **artist** — has Write but **no Edit** (it generates assets, it does not edit code).
- **engineer** — has WebFetch but **no WebSearch**.
- **algorithm** — full local toolset but **no web access** (no WebFetch, no WebSearch).
- **researcher** — read-only research: **no Bash, no Write, no Edit**. It is the only agent without Bash.
- **qa-tester** and **reviewer** — read-only validators: **no Write, no Edit, no web**. Bash/Read/Grep/Glob/mcp only.

## Model and effort

All 12 agents run `model: opus` at `effort: xhigh` — the highest-quality tier, for the strongest reasoning across every role. The `effort` key overrides the session `effortLevel`; pinning it per-agent keeps xhigh in force even if the global default changes.

**No agent uses sonnet or haiku.** (Haiku appears only as a fast-tier pass condition inside the `agent-execution-guard.py` hook, not as any agent's model.)

## Parallelism

Multiple agents can run in parallel by issuing multiple `Task` tool calls in the same message:

```
[Agent call 1: researcher exploring option A]
[Agent call 2: researcher exploring option B]
[Agent call 3: architect designing topology]
```

The harness runs them concurrently. The parent agent receives all results before continuing.

For a substantial number of independent subtasks, consider Agent Teams (`TeamCreate`) — they share a task list and coordinate.

## Background agents

For non-blocking work:

```
Task(subagent_type: "researcher", run_in_background: true, description: "...", prompt: "...")
```

The agent runs without blocking the parent. Parent gets a notification on completion. Useful for long research while continuing other work.

## Worktree isolation

For agents that modify code in parallel:

```
Task(subagent_type: "engineer", isolation: "worktree", ...)
```

Each agent gets its own git worktree. Changes are isolated. Use when multiple agents would otherwise conflict on the same files.

## Voice announcement rule

Only the primary agent (the main session) emits voice curls. Subagents (anything spawned via Task) must NOT emit voice. The Algorithm spec is explicit:

> CRITICAL: Only the primary agent may execute voice curls. Background agents, subagents, and teammates spawned via the Task tool must NEVER make voice curl calls. Voice is exclusively for the main conversation agent. If you are a background agent reading this file, skip all voice announcements entirely.

## Pre-tool guard

Every Task invocation passes through the PreToolUse hook `03-rai/hooks/agent-execution-guard.py`. It is **warn-only — it never blocks.** Its single job is to nudge Task calls toward background execution for parallelism. What it actually does:

- Fires only when `tool_name == "Task"`.
- **Passes silently** when the call already sets `run_in_background: true`, when `model == "haiku"`, when `subagent_type == "Explore"`, or when the prompt contains the literal string `"Timing: FAST"`.
- **Otherwise it warns** — emits `{"decision": "allow", ...}` with a message suggesting `run_in_background: true`. The Task still proceeds.

What it does **NOT** do (despite earlier documentation that claimed otherwise): it does not validate that the named agent exists, does not read the agent's frontmatter, does not enforce the permission allow-list, and does not log the invocation. If you pass a wrong agent name, this guard will not catch it — the harness's own agent lookup is what fails. The hook has a 5-second SIGALRM timeout and is wrapped in `hook_timer` for perf telemetry.

The permission allow-lists in each agent's frontmatter are enforced by the harness itself, not by this hook.

## Adding a new agent

From the system design:

1. **Identify the niche.** What does no existing agent cover? Don't add an agent that overlaps a specialist. If you can't justify a distinct persona or methodology, it's a skill, not an agent.
2. **Model + effort.** All agents run `model: opus` at `effort: xhigh`. Keep it consistent.
3. **Decide on permissions.** Read-only validator (5 tools)? Read-only researcher (6, no Bash)? Full access (9)? Tailor the `permissions.allow:` list — don't paste the everything block by default.
4. **Write the agent file** at `03-rai/agents/{name}.md` with the five-key frontmatter schema above (`name`, `description`, `model`, `effort`, `permissions.allow`).
5. **Update `agents/MANIFEST.md`** with the new entry.
6. **Test invocation** via `Task(subagent_type: "name", ...)`.

A skill (`/rai compose-agents`) exists to help compose new agents.

## Common invocation patterns

### Independent research, parallel

```
[Task: researcher with topic A]
[Task: researcher with topic B]
[Task: researcher with topic C]
```

### Architect → engineer chain

```
[Task: architect] → produces design + tradeoffs
[Task: engineer]  → implements based on the architect's output
```

### Engineer → reviewer chain

```
[Task: engineer]  → writes code
[Task: reviewer]  → reviews independently (different context)
```

### Engineer → qa-tester chain

```
[Task: engineer]  → ships the feature
[Task: qa-tester] → exercises it like a user
```

### Designer + engineer team

```
[Task: designer]  → mocks + interaction states
[Task: engineer]  → implements
```

### Algorithm forcing for a tricky subtask

```
[Task: algorithm] → runs the 7 phases on the subtask in isolation
```

### Background research while continuing

```
[Task: researcher, run_in_background: true]
[continue other work]
[notification: research complete]
[Read the research output]
```

## Agent file structure (beyond frontmatter)

Below the frontmatter, the body is free-form persona and rules. **There is no fixed body template** — the harness only requires the frontmatter, and the agent files do not share a rigid section layout. In practice the bodies converge on a small set of recurring sections, but they vary per agent:

```markdown
# {Agent name}

## Core Identity
[One paragraph: what this agent is and how it thinks]

## Principles
[The non-negotiable rules this agent operates under]

## Process
[Step-by-step approach this agent follows]
```

Beyond those, sections are agent-specific: engineer has `## Development Cycle`, pentester has `## Authorization Requirements`, designer and reviewer carry a `## Review Checklist`, algorithm has `## ISC Format`, and several agents add an `## Output` section. Treat the block above as illustrative, not a contract — no agent file contains a `## Role` or `## When NOT to use` section.
