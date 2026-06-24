# Agents Manifest

12 agents. All kebab-case. All run `opus` at `xhigh` effort. Invocation drives from the `name:` field in each `.md` file.

Two tiers: **specialists** (user invokes explicitly to take on a role) and **methodology** (applied to any problem, not domain-bound).

## Specialists (10)

Each has a distinct persona and scope. Invoke with `Task(subagent_type: "name")` or a direct "use the X agent" prompt.

| Agent | Scope |
|-------|-------|
| `architect` | Distributed systems, architecture decisions, trade-off analysis. Thinks in constraints and principles. |
| `engineer` | Production-grade implementation. TDD, types, tests-first. |
| `designer` | UX/UI, WCAG 2.1 AA, visual hierarchy, spacing, interactions. |
| `pentester` | Authorized security testing, vulnerability assessment. Requires explicit authorization. |
| `qa-tester` | Edge case hunting from user perspective. Evidence-based PASS/FAIL. |
| `reviewer` | Code review, bug catching, security issues. Tests must pass before approval. |
| `artist` | Image prompt engineering for FLUX, GPT-Image-1. Illustrations, diagrams, visual assets. |
| `writer` | Prose craftsman. Locked-in voice across Arabic (Lumen north star) + English, anti-AI rules. Prose, not code. |
| `debugger` | Root-cause specialist. Reproduce, hypothesize, bisect, instrument, prove. Fixes the class, not the symptom. |
| `sre` | Site reliability. Keeps running systems up, diagnoses failures (timers, sync, schedulers). `/devops` builds; `sre` keeps alive. |

## Methodology (2)

Persona-neutral. Applied to any problem.

| Agent | Scope |
|-------|-------|
| `algorithm` | Structured 7-phase problem-solving via Ideal State Criteria (ISC). Full spec at `algorithm/latest`. |
| `researcher` | Multi-source research synthesis. Query decomposition, parallel search, citation-backed findings. |

## Removed (4, in commit trimming agents to 10)

`codex-researcher`, `gemini-researcher`, `grok-researcher`, `perplexity-researcher` — the multi-model parallel research pattern was theoretical. If pull emerges, add back or teach the base `researcher` to spawn API variants on demand.

## Adding a new agent

1. Scope: what distinct persona or methodology does this bring that no existing agent covers? If the answer is "none," it's not an agent — it's a skill.
2. File: `agents/<name>.md` with frontmatter `name: <name>`, `description:`, `model: opus`, `effort: xhigh`, `permissions.allow:`.
3. Update this manifest.
4. Invocation: `Task(subagent_type: "<name>")` or `/Task` with the name.

## Naming rules

- Filename: kebab-case, matches frontmatter `name:` field
- `name:` field: drives invocation
- No PascalCase in new agents (breaks consistency with skills)
