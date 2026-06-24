# 03-rai/ Architecture

Rai's brain. One paragraph per top-level dir/file. See `CLAUDE.md` for how Rai behaves, `skills/MANIFEST.md` for skill groupings, `agents/MANIFEST.md` for agent tiers.

## Top-level layout

```
03-rai/
├── CLAUDE.md                        # behavior, identity-load paths, Algorithm summary
├── ARCHITECTURE.md                  # this file
├── .pai-protected.json              # secret redaction patterns (api keys, PII, local markers)
├── security-patterns.example.yaml   # security-validator fallback patterns
├── algorithm/
│   ├── latest -> v3.7.0.md
│   └── v3.7.0.md                    # canonical spec (ISC, phases, PRD schema)
├── identity/                        # Rai-only config (AI persona, rules, formatting)
│   ├── dai-identity.md              # AI persona traits
│   ├── ai-steering-rules.md         # behavioral rules
│   ├── response-format.md           # response shape preferences
│   └── security-patterns.yaml       # user-customized security patterns (runtime-active)
│                                    # John's own identity lives in ~/helm/02-ana/:
│                                    #   who-i-am.md, contacts.md, environment.md,
│                                    #   definitions.md, tech-stack.md. Life OS also there.
├── agents/                          # 10 personas (kebab-case)
│   ├── MANIFEST.md                  # tiers: specialists + methodology
│   └── *.md                         # architect, engineer, designer, pentester, qa-tester,
│                                    # reviewer, artist, intern, algorithm, researcher
├── skills/                          # 22 top-level entries: 19 routers + 3 leaves
│   ├── MANIFEST.md                  # router + sub-skill ownership map (post-2026-04-22 reorg)
│   ├── GAPS.md                      # open inbox of deferred work + tombstones
│   └── */                           # routers hold sub-skill .md files; leaves hold SKILL.md only
├── hooks/                           # event-driven hooks (20 .py files)
│   ├── lib/                         # shared utilities (paths, state_sweep, tab_setter, ...)
│   ├── scripts/                     # skill-called utilities (store_to_chromadb.py)
│   ├── context_mapping.json         # save-memory project-name mapping
│   └── *.py                         # 20 event handlers
├── config/
│   ├── settings.json                # permissions, hooks registration, status line
│   ├── mcp.json                     # MCP server config
│   ├── .skill-lock.json             # skill concurrency locks
│   └── statusline.sh                # terminal statusline script
├── memory/                          # runtime state + long-term records
│   ├── state/                       # per-session: current-work, tab-titles, algorithms
│   ├── work/                        # PRD per task (slug/tier/status)
│   ├── learning/                    # integrity logs, captured learnings
│   ├── relationship/                # daily user-signal notes
│   └── security/                    # security-validator event logs (JSONL per day)
└── semantic-memory/
    ├── chromadb/                    # persistent vector store (SQLite + HNSW)
    ├── pending/                     # session transcripts waiting for /process-sessions
    └── scripts/                     # py-chroma.sh wrapper
```

## Paragraph-per-directory

### `algorithm/`

Canonical spec for Rai's 7-phase problem-solving framework. `latest` is a pointer file containing the active version name (currently `v3.7.0.md`). CLAUDE.md holds only the operationally critical summary (tier table + capability rule). The `agents/algorithm.md` persona wraps it for explicit user invocation.

### `identity/`

Who Rai is serving. Identity files are loaded at SessionStart by `hooks/session-start.py` to produce the identity digest. The life operating system lives outside this folder at `~/helm/02-ana/` (identity, soul, family, health, financial, admin, travel, etc.). The `telos` skill reads and writes those files. `security-patterns.yaml` holds the user-customized patterns that `hooks/security-validator.py` loads first, falling back to `security-patterns.example.yaml` at the vault root. This is the only dir at `03-rai/` root that is treated as non-public.

### `agents/`

Claude Code agent definitions. Ten `.md` files, each with frontmatter (`name`, `description`, `tools`). Invoked via `Task(subagent_type: "<name>")` or `/Task`. See `agents/MANIFEST.md` for the specialist/methodology split.

### `skills/`

Claude Code skill definitions. 22 top-level entries: 19 routers (with sub-skill `.md` files inside) and 3 leaves (one `SKILL.md` each). Folder name matches frontmatter `name:` which drives `/invocation` at the top level. Routers dispatch to their sub-skill files internally. Claude Code discovers skills by depth-1 filesystem scan — sub-skills are not directly discoverable. Groupings and full inventory live in `skills/MANIFEST.md`; open backlog in `skills/GAPS.md`.

### `hooks/`

Event-driven handlers wired up in `config/settings.json`. 20 Python hooks cover SessionStart, UserPromptSubmit, PreToolUse, PostToolUse, Stop, SessionEnd. `lib/` holds shared utilities (notably `state_sweep.py` for SessionStart orphan cleanup, `paths.py` for standard directory resolution, `tab_setter.py` for WezTerm tab state). `scripts/` holds utility scripts that skills call explicitly (not event-triggered).

### `config/`

`settings.json` is the harness contract: permissions, hook registrations, plugins, status line command. `mcp.json` pins MCP servers. `.skill-lock.json` prevents concurrent skill runs. `statusline.sh` drives the prompt.

### `memory/`

Operational memory — what's happening and what has happened. `state/` is per-session runtime (swept on SessionStart for orphans, cleaned on SessionEnd). `work/` is the PRD-per-task record, one dir per task slug. `learning/` holds captured learnings and system integrity change logs (30-day retention). `relationship/` captures daily user-signal notes. `security/` is the security-validator's JSONL event trail by month.

### `semantic-memory/`

Long-term recall. `chromadb/` is the persistent vector store. `pending/` is the queue of raw session transcripts waiting for `/process-sessions` to summarize and ingest them into ChromaDB. `scripts/py-chroma.sh` is the Python/chromadb environment wrapper.

### `CLAUDE.md`

Rai's global instructions: identity load paths, Algorithm summary, naming standards, writing style, behavioral rules (never mention AI in git, never push without asking, etc.). Loaded into every Claude Code session.

### `.pai-protected.json`

252 lines of regex patterns for secret redaction — AWS, GCP, Stripe, API keys, plus custom local entity names and identity markers. Used by `hooks/lib/protected_scan.py` to block `git commit` when staged files match these patterns.

## Cross-file relationships

- **SessionStart** → `session-start.py` reads `identity/*` (Rai persona) plus `~/helm/02-ana/` anchors (`identity/{who-i-am,vision,mindset,goals}.md`, `ideas.md`, `contacts.md`, `environment.md`, `definitions.md`, `tech-stack.md`), writes identity digest to stdout
- **Pre-commit** → `security-validator.py` scans Bash `git commit` commands, calls `protected_scan.py` which reads `.pai-protected.json`
- **SessionEnd** → `save-memory.py` dumps transcript to `semantic-memory/pending/`
- **Skill-invoked** → `/process-sessions` calls `hooks/scripts/store_to_chromadb.py` to drain `pending/` into `chromadb/`
- **Self-healing** → SessionStart sweep (`hooks/lib/state_sweep.py`) clears orphan `memory/state/*` files from crashed sessions (6h threshold)
- **Algorithm tracking** → `algorithm-tracker.py` writes per-session phase history to `memory/state/algorithms/{uuid}.json`

## Out-of-scope

- Sub-skills inside routers follow the same kebab-case naming as top-level skills; filename matches frontmatter `name:`
- ChromaDB schema is owned by skills + `store_to_chromadb.py`, not documented here
- `13-archive/` and other sibling vault folders are outside Rai's scope
