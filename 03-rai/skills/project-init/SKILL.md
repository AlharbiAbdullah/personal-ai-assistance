---
name: project-init
description: >
  Interactive wizard to bootstrap project-level Claude Code configuration.
  USE WHEN the user runs /project-init or asks to set up `.claude/`,
  `project_memory/`, CLAUDE.md, MCPs, or hooks for a new or existing
  project. Detects existing state (CREATE vs ENHANCE mode), reads project
  signals from spec.md/plan.md/package.json/pyproject.toml, suggests
  relevant skills, and generates the full setup.
---

# Project Init Wizard

Interactive setup for project-level Claude Code configuration.

## Phase 1: Detection

Check project state:

```
Does .claude/ exist?
├── Yes → ENHANCE mode
└── No  → CREATE mode

Also check for:
- spec.md, plan.md, CLAUDE.md, README.md
- package.json, pyproject.toml, go.mod, Cargo.toml
- Existing .claude/settings.json
- Existing .mcp.json
- Existing project_memory/
```

## Phase 2: Read Context

If any exist, read and extract signals:

| File | Extract |
|------|---------|
| spec.md | Requirements, features, integrations |
| plan.md | Architecture, modules, patterns |
| CLAUDE.md | Existing conventions |
| README.md | Project purpose, tech stack |
| package.json | Dependencies, scripts, type (frontend/backend) |
| pyproject.toml | Python deps, project type |

**Signal extraction patterns:**

```
API/REST/GraphQL → suggest: api-test, solution_architect
ETL/pipeline/data/warehouse → suggest: data_architect
frontend/React/Vue/UI → suggest: frontend-design, e2e
auth/security/JWT/OAuth → suggest: security-review
test/TDD/coverage → suggest: tdd, test
Docker/container/k8s → suggest: docker
```

## Phase 3: Smart Questions

### Pattern: Signal → Suggestion → Open-ended

1. **Present findings first:**
   "I found [spec.md/plan.md/etc]. Here's what I see: [summary]"

2. **Ask targeted Y/N based on signals:**
   For each signal found, ask one question.

3. **Open-ended follow-up:**
   - "Any other skills you want?"
   - "Specific hooks needed?"
   - "MCPs to configure? (GitHub, JIRA, etc.)"

### Question Templates

**If API signals found:**
```
Your spec mentions REST endpoints. Add these skills?
- /api-test (contract/behavior tests)
- /solution_architect (API design patterns)
```

**If data signals found:**
```
I see data pipeline references. Add /data_architect skill?
```

**If frontend signals found:**
```
Frontend detected. Add these skills?
- /frontend-design (UI components)
- /e2e (end-to-end tests)
```

**If auth signals found:**
```
Auth/security mentioned. Add /security-review skill?
```

**If testing signals found:**
```
Testing focus detected. Add /tdd skill for test-first development?
```

**If Docker signals found:**
```
Container references found. Add /docker skill?
```

**Always ask:**
```
Any other skills to add? (comma-separated or "none")
```

```
Configure any MCPs? Options:
- GitHub (issue/PR integration)
- Custom MCP URL
- Skip
```

```
Any hooks needed?
- PostToolUse (trigger on Write/Bash)
- SessionEnd (end of session)
- None
```

## Phase 4: Generation

### Directory Structure

```
PROJECT_ROOT/
├── .claude/
│   ├── settings.json    (hooks: project memory + any custom)
│   ├── hooks/           (project-level hook scripts)
│   │   ├── project-session-save.py
│   │   └── project-session-recall.py
│   └── skills/          (if project-specific skills)
├── project_memory/
│   ├── pending/         (raw transcripts, unprocessed)
│   ├── sessions/        (processed session JSONs, kept forever)
│   ├── chromadb/        (vector store for semantic recall)
│   ├── summaries/       (human-readable markdown summaries)
│   └── accumulated_knowledge.json  (merged knowledge from all sessions)
├── .mcp.json            (if MCPs selected)
├── .codemap/            (auto-updated navigation map)
└── CLAUDE.md            (project conventions)
```

### Project Memory Setup

**ALWAYS set up project memory.** This is not optional.

1. Create the directory structure:

```bash
mkdir -p project_memory/{pending,sessions,chromadb,summaries}
```

2. Copy hook scripts from the skill's scripts/ directory:

```bash
cp ~/.claude/skills/project-init/scripts/project-session-save.py .claude/hooks/
cp ~/.claude/skills/project-init/scripts/project-session-recall.py .claude/hooks/
chmod +x .claude/hooks/project-session-save.py
chmod +x .claude/hooks/project-session-recall.py
```

3. Initialize accumulated_knowledge.json from template:

```bash
cp ~/.claude/skills/project-init/scripts/accumulated_knowledge_template.json project_memory/accumulated_knowledge.json
```

4. Add .gitignore entries for project memory data:

```
# Project Memory (personal, not shared)
project_memory/pending/
project_memory/sessions/
project_memory/chromadb/
project_memory/summaries/

# Keep the structure and accumulated knowledge
!project_memory/accumulated_knowledge.json
```

### settings.json Template

**Always include project memory hooks.** Add other hooks as requested.

```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 .claude/hooks/project-session-recall.py"
          }
        ]
      }
    ],
    "SessionEnd": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 .claude/hooks/project-session-save.py"
          }
        ]
      }
    ]
  }
}
```

If additional hooks are needed (PostToolUse, etc.), merge them into the same settings.json.

### .mcp.json Template

Only create if MCPs selected:

```json
{
  "server-name": {
    "type": "http",
    "url": "MCP_URL",
    "headers": {
      "Authorization": "Bearer ${ENV_VAR}"
    }
  }
}
```

### CLAUDE.md Template

```markdown
# Project: {NAME}

## Overview
{Brief description from README/spec}

## Tech Stack
{Detected or user-specified}

## Conventions

### Code Style
- {language-specific conventions}

### Testing
- {testing approach}

### Git
- Branch naming: feature/, bugfix/, hotfix/
- Commit style: conventional commits

## Key Paths
- Source: {src path}
- Tests: {test path}
- Config: {config path}

## Skills Available
{List of installed skills}

## MCPs Configured
{List of MCPs or "None"}

## Project Memory

This project uses project-level session memory. Key knowledge is accumulated in `project_memory/accumulated_knowledge.json` and loaded at every session start.

### Processing Project Sessions

When there are pending sessions in `project_memory/pending/`, process them:

1. Read each pending session JSON
2. Extract the following fields per session:

| Field | What to Extract | Purpose |
|-------|-----------------|---------|
| summary | 3-15 sentence summary (length based on content density) | Quick recall |
| decisions | Architectural/design choices with "what", "why", "alternatives_rejected" | Prevent re-debating |
| patterns | Code patterns established with "pattern", "files", "reason" | Consistency |
| gotchas | Bugs/issues found with "what", "fix", "prevent" | Avoid repeating mistakes |
| technical_learnings | Library behaviors, API quirks, non-obvious facts | Institutional knowledge |
| open_threads | Unfinished work, pending items | Continuation |
| files_modified | Files changed this session | Recent context |
| dependencies_added | New packages/versions | Dependency awareness |
| tags | Topic tags for the session | Categorization |

3. Save processed session to `project_memory/sessions/YYYY-MM-DD_NNN.json`
4. Save human-readable summary to `project_memory/summaries/YYYY-MM-DD_NNN.md`
5. Merge into `project_memory/accumulated_knowledge.json`:
   - **Decisions**: Append new, deduplicate by "what"
   - **Patterns**: Append new, merge files lists for same pattern
   - **Gotchas**: Append new, deduplicate by "what"
   - **Technical learnings**: Append new, deduplicate exact matches
   - **Open threads**: Add new, REMOVE threads that were resolved in this session
   - **Dependencies**: Update added/removed/changed
   - **Recent files**: Replace with last 3 sessions' modified files
   - **Tags index**: Union of all session tags
   - Update `last_updated` and increment `total_sessions`
6. Archive raw file: `mv project_memory/pending/FILE.json project_memory/sessions/`

### Processed Session Schema

```json
{
  "session_id": "2026-02-13_001",
  "date": "2026-02-13",
  "duration_minutes": 45,
  "type": "build|debug|planning|learning|explore|brainstorm",
  "outcome": "completed|partial|blocked|exploration",
  "summary": "Implemented JWT auth middleware with refresh token rotation",
  "decisions": [
    {
      "what": "Use RS256 over HS256 for JWT signing",
      "why": "Allows public key verification without sharing secrets",
      "alternatives_rejected": ["HS256 — simpler but requires shared secret"]
    }
  ],
  "patterns": [
    {
      "pattern": "All middleware follows (req, res, next) → try/catch → next(err)",
      "files": ["src/middleware/auth.ts"],
      "reason": "Consistent error propagation to global handler"
    }
  ],
  "gotchas": [
    {
      "what": "Forgot to await async token verification",
      "fix": "Added await to jwt.verify() — it returns a Promise with RS256",
      "prevent": "Always await jwt.verify when using async algorithms"
    }
  ],
  "technical_learnings": [
    "Express middleware order matters — auth must come after body-parser",
    "jsonwebtoken library's verify() is sync with HS256 but async with RS256"
  ],
  "open_threads": [
    "Refresh token storage — currently in-memory, needs Redis or DB"
  ],
  "files_modified": ["src/middleware/auth.ts", "src/routes/auth.ts"],
  "dependencies_added": ["jsonwebtoken@9.0.0"],
  "tags": ["auth", "middleware", "jwt"]
}
```

### Accumulated Knowledge Schema

```json
{
  "last_updated": "2026-02-13",
  "total_sessions": 23,
  "decisions": [
    {
      "what": "Use RS256 over HS256 for JWT signing",
      "why": "Allows public key verification without sharing secrets",
      "alternatives_rejected": ["HS256"],
      "decided": "2026-02-13",
      "session": "2026-02-13_001"
    }
  ],
  "patterns": [
    {
      "pattern": "All middleware follows (req, res, next) → try/catch → next(err)",
      "files": ["src/middleware/*.ts"],
      "reason": "Consistent error propagation",
      "established": "2026-02-13"
    }
  ],
  "gotchas": [
    {
      "what": "jwt.verify is async with RS256",
      "prevent": "Always await jwt.verify with async algorithms",
      "learned": "2026-02-13"
    }
  ],
  "technical_learnings": [
    {
      "learning": "Express middleware order matters — auth after body-parser",
      "learned": "2026-02-13"
    }
  ],
  "open_threads": [
    {
      "thread": "Refresh token storage needs Redis or DB",
      "opened": "2026-02-13",
      "session": "2026-02-13_001"
    }
  ],
  "dependencies": {
    "added": {"jsonwebtoken": "9.0.0"},
    "removed": {},
    "changed": {}
  },
  "recent_files": ["src/middleware/auth.ts", "src/routes/auth.ts"],
  "tags_index": ["auth", "middleware", "jwt"]
}
```
```

## Phase 5: Copy Skills

For each selected skill, copy from global to project:

```bash
mkdir -p .claude/skills/{skill-name}
cp -r ~/.agents/skills/{skill-name}/* .claude/skills/{skill-name}/
```

Only copy if user wants project-local skills. Otherwise, global skills work fine.

## Phase 6: Codemap

If CREATE mode (new project):
```
Run /map-updater? (recommended for new projects)
```

## Phase 7: Summary

Display what was created/modified:

```
## Setup Complete

### Created:
- .claude/settings.json (project memory hooks + any custom hooks)
- .claude/hooks/project-session-save.py (SessionEnd — saves transcripts)
- .claude/hooks/project-session-recall.py (SessionStart — loads knowledge)
- project_memory/ (pending, sessions, chromadb, summaries)
- project_memory/accumulated_knowledge.json (empty, ready for first session)
- CLAUDE.md (project conventions + memory processing instructions)
- .mcp.json (if MCPs selected)

### Skills Added:
- {list}

### Project Memory:
- SessionEnd hook saves transcripts to project_memory/pending/
- SessionStart hook loads accumulated_knowledge.json
- Process pending sessions by asking Claude: "process project memory sessions"
- All decisions, patterns, gotchas, and learnings accumulate across sessions

### Next Steps:
1. Review CLAUDE.md and customize conventions
2. Set environment variables for MCPs (if any)
3. Run /map-updater to generate codemap
4. Start working — project memory captures everything automatically

Commit .claude/ to git? (y/n)
```

## Rules

1. **Never overwrite without asking** - If file exists, show diff and ask
2. **Minimal by default** - Only create what's needed (except project memory — always create)
3. **Smart defaults** - Infer from project context
4. **Git-friendly** - Offer to commit setup
5. **Explain choices** - Tell user why you suggest each skill
6. **Project memory is mandatory** - Always set up project_memory/ structure and hooks

## Example Flow

```
User: /project-init

Claude: Let me check your project setup...

Found:
- spec.md (has requirements)
- plan.md (has architecture)
- pyproject.toml (Python project)
- No .claude/ directory
- No project_memory/

Mode: CREATE (new setup)

From your docs, I see:
- ETL pipelines for data ingestion
- REST API for data access
- PostgreSQL as primary store

Suggested skills:
1. /data_architect - ETL patterns, data modeling [Y/n]
2. /api-test - API contract testing [Y/n]
3. /security-review - Auth/data security [Y/n]

User: y, y, n

Any other skills? (comma-separated or "none")

User: docker

MCPs to configure?
- GitHub [Y/n]
- Custom URL [Y/n]

User: y, n

Creating setup...

[Creates .claude/, CLAUDE.md, .mcp.json, project_memory/]

Done! Created:
- CLAUDE.md (project conventions)
- .claude/settings.json (project memory hooks)
- .claude/hooks/ (session save + recall scripts)
- project_memory/ (pending, sessions, chromadb, summaries)
- project_memory/accumulated_knowledge.json (initialized)
- .mcp.json (GitHub MCP - set GITHUB_PERSONAL_ACCESS_TOKEN)

Skills available: /data_architect, /api-test, /docker

Project memory active:
- Sessions auto-saved on exit
- Knowledge loaded on start
- Process pending: "process project memory sessions"

Run /map-updater now? [Y/n]
```
