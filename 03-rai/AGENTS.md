# Rai — OpenCode harness instructions

OpenCode's brain entry file. This is the OpenCode counterpart to `03-rai/CLAUDE.md`
(which is Claude Code's). Both harnesses share the same identity, memory, skills, and
Algorithm — this file frames them the OpenCode way. Loaded via the `instructions` array
in `~/.config/opencode/opencode.jsonc`.

## How the brain loads on OpenCode

- **Identity** → `instructions` globs: `03-rai/identity/*.md` (Rai config) + `02-ana/identity/*.md` (John's self-model). Always on, every folder.
- **Memory** → the global plugin `~/.config/opencode/plugin/rai.ts` injects it, **cwd-aware**: full recent (capped) inside `~/helm`, last 7 days elsewhere. Older memories via `/recall`.
- **Skills** → native discovery of `~/.claude/skills/**/SKILL.md` (symlink → `03-rai/skills`). 34 routers.
- **Agents** → `~/.config/opencode/agent/*.md` (10 specialists).
- **Hooks** → `rai.ts` maps OpenCode events onto the existing Python hooks (security, side-effects, codemap, session-end).
- **Model** → `openai/gpt-5.5` (ChatGPT OAuth). Codex variants + 5.1/5.2 are blocked on the account.

## Folder map

Vault layout in `ARCHITECTURE.md`. Skill groupings in `skills/MANIFEST.md`. Agent tiers in
`agents/MANIFEST.md`. The vault root `~/helm/CLAUDE.md` documents folders 00–13.

## Identity auto-load contract

Every `*.md` in `03-rai/identity/` and `02-ana/identity/` loads at session start. To add or
remove a file from context, move it in or out of an `identity/` folder. Non-`.md` files in
identity/ are NOT auto-loaded.

## Session Memory

- `03-rai/memory/` — file memory (learning, relationship, security, state, work).
- `03-rai/semantic-memory/` — ChromaDB vector store + pending queue.
- Skills: `/process-sessions`, `/recall`, `/history-recall`.

## Algorithm — v3.7.0

Structured problem-solving. Full spec at `03-rai/algorithm/latest` (read on demand).
Phases: OBSERVE → THINK → PLAN → BUILD → EXECUTE → VERIFY → LEARN. Trivial tasks
(greetings, lookups) skip the Algorithm entirely.

### Effort Tiers

| Tier | Budget | ISC Range | Min Capabilities | When |
|------|--------|-----------|------------------|------|
| **Standard** | <2min | 8–16 | 1–2 | Normal request (DEFAULT) |
| **Extended** | <8min | 16–32 | 3–5 | Quality must be extraordinary |
| **Advanced** | <16min | 24–48 | 4–7 | Substantial multi-file work |
| **Deep** | <32min | 40–80 | 6–10 | Complex design |
| **Comprehensive** | <120min | 64–150 | 8–15 | No time pressure |

### Min Capabilities — CRITICAL FAILURE rule

If a tier requires N capabilities and you list one, you MUST invoke it. Writing prose that
resembles a skill's output is NOT invocation. Listing a capability without invoking it =
CRITICAL FAILURE. When in doubt, invoke MORE capabilities, not fewer.

### PRD

Every non-trivial task gets a PRD at `memory/work/{slug}/PRD.md`. AI is sole writer.
On OpenCode, the PRD dir is scaffolded by `auto-work-creation.py` via the `rai.ts`
`chat.message` hook.

## OpenCode-specific caveats

- **Enforcement is lighter than CC.** The Algorithm prose guides you here, but the
  session-end *scan* (`algorithm-scan.py`) needs a transcript adapter (OpenCode stores
  sessions in SQLite, not CC's JSONL). PRD scaffolding works; session-end memory *writes*
  are pending that adapter.
- **Security wall does not cover subagents.** `tool.execute.before` doesn't fire for
  task-spawned tool calls — don't treat a subagent as sandboxed.
- Setup + full mapping: `~/helm/12-system/tools/harnesses/open-code/`.
