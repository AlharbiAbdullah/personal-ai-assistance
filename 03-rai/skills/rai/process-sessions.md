---
name: process-sessions
description: Process pending session transcripts and save summaries to ChromaDB
allowed-tools: Bash, Read, Glob
argument-hint: [--dry-run]
---

# Process Sessions - Manual Memory Processing

Process pending session transcripts from `~/helm/03-rai/semantic-memory/pending/` and store summaries in ChromaDB.

## Why Manual?

- Cron job fails because Claude CLI subprocess needs OAuth session
- This skill runs during active session → Claude summarizes directly (no subprocess)

## Arguments

| Argument | Description |
|----------|-------------|
| (none) | Process all pending sessions |
| `--dry-run` | Show what would be processed (no writes/deletes) |

## Instructions

### Step 1: List Pending Files

```bash
ls -la ~/helm/03-rai/semantic-memory/pending/*.json 2>/dev/null || echo "No pending files"
```

### Step 2: For Each Pending File

1. **Read the JSON file** using the Read tool
2. **Extract metadata** from the file (new fields available):
   - `cwd`: Working directory
   - `project_name`: Detected project name
   - `duration_minutes`: Session length
   - `tools_summary`: {"Edit": 5, "Bash": 12, ...}
   - `files_modified`: ["/path/to/file.py", ...]

3. **Auto-infer session type** from `tools_summary`:
   - If Edit + Write > 50% of tool usage → "build"
   - If Grep + Read + Glob > 70% of tool usage → "explore"
   - If conversation mentions "error", "fix", "bug" → "debug"
   - If Task tool with Plan agent used → "planning"
   - Otherwise → "brainstorm"

4. **Auto-infer mood** from conversation sentiment:
   - Frustration keywords ("stuck", "not working", "error", "failed") → "low"
   - Progress keywords ("done", "working", "fixed", "shipped", "complete") → "high"
   - Neutral/exploratory → "med"

5. **Infer outcome**:
   - If final messages show completion → "completed"
   - If session mentions being blocked → "blocked"
   - If mostly reading/searching → "exploration"
   - Otherwise → "partial"

6. **Detect continuation**: Check if `cwd` or `project_name` matches recent sessions in ChromaDB

7. **Check if session should be saved** (BEFORE calculating summary):

```python
def should_save_session(transcript) -> bool:
    # Plan mode = ALWAYS save (thoughtful conversations)
    if was_plan_mode(transcript):  # Check for EnterPlanMode tool use
        return True

    # Non-plan mode: check interaction count
    user_message_count = count_user_messages(transcript)  # type: user only
    if user_message_count < 4:
        return False  # Trivial session, skip entirely

    return True
```

| Condition | Action |
|-----------|--------|
| Plan mode session | ALWAYS save |
| Non-plan, >= 4 user messages | Save with content scoring |
| Non-plan, < 4 user messages | **Archive without saving to ChromaDB** |

8. **Calculate Content Density Score** (for sessions that pass step 7):

Score based on **what actually happened**, NOT duration:

```python
score = 0

# High-value content (actual work/decisions)
score += len(milestones) * 3        # max 5 → 15 pts
score += len(code_snippets) * 2     # max 3 → 6 pts
score += len(decisions) * 2         # variable
score += len(ideas) * 1.5           # variable

# Medium-value content (context/substance)
score += len(key_quotes) * 1        # max 5 → 5 pts
score += len(errors_encountered) * 1 # max 3 → 3 pts
score += len(user_questions) * 0.5  # max 3 → 1.5 pts

# Message count (back-and-forth engagement)
user_message_count = count_user_messages(transcript)
score += min(user_message_count * 0.5, 10)  # cap at 10 pts

# Tool intensity (actual editing vs just reading)
edit_write_count = tools.get("Edit", 0) + tools.get("Write", 0)
score += min(edit_write_count, 10)  # cap at 10 pts

# Files modified (tangible output)
score += min(len(files_modified), 5) # cap at 5 pts

# NOTE: Duration is IGNORED - session left open 18hrs still scores low
```

**Score → Summary Length:**

| Score | Summary Length | Interpretation |
|-------|----------------|----------------|
| 0-5   | 2-3 sentences | Trivial/abandoned session |
| 6-15  | 4-6 sentences | Light work or exploration |
| 16-25 | 7-10 sentences | Solid working session |
| 26-40 | 10-15 sentences | Productive session |
| 40+   | 15-20 sentences | Major session (breakthrough/build) |

**Outcome Multiplier:**

```python
multipliers = {
    "completed": 1.0,
    "partial": 0.85,
    "blocked": 0.9,   # still valuable to document blockers
    "exploration": 0.7
}
final_score = score * multipliers[outcome]
```

9. **Extract rich content** from the transcript:

| Field | What to Extract | Max Items |
|-------|-----------------|-----------|
| `key_quotes` | Memorable insights, important statements from user or assistant | 5 |
| `code_snippets` | Significant code written (functions, classes, queries) - truncate to 200 chars each | 3 |
| `commands_executed` | Important bash commands run (not trivial ones like ls, cd) | 5 |
| `errors_encountered` | Error messages that came up during session | 3 |
| `resources_used` | URLs, documentation links, file paths referenced | 5 |
| `milestones` | Significant progress points ("fixed X", "implemented Y") | 5 |
| `user_questions` | The user's original questions/requests (first few messages) | 3 |

10. **Generate memory entry** with all fields:

```json
{
  "type": "brainstorm|debug|planning|learning|build|explore",
  "mood": "low|med|high",
  "outcome": "completed|partial|blocked|exploration",
  "summary": "ADAPTIVE LENGTH based on content score - see step 8",
  "ideas": ["idea1", "idea2"],
  "decisions": ["decision1"],
  "tags": ["tag1", "tag2"],
  "open": "unresolved question or null",
  "revisit": "YYYY-MM-DD or null",
  "key_quotes": ["important insight here"],
  "code_snippets": ["def important_func(): ..."],
  "commands_executed": ["pytest -v", "git push origin main"],
  "errors_encountered": ["ModuleNotFoundError: xyz"],
  "resources_used": ["https://docs.example.com/api"],
  "milestones": ["Fixed authentication bug", "Deployed v2.0"],
  "user_questions": ["How do I implement X?", "Why is Y failing?"]
}
```

11. **Store in ChromaDB** using the helper script (wrapped so chromadb is available):

```bash
~/helm/03-rai/semantic-memory/scripts/py-chroma.sh \
  ~/helm/03-rai/hooks/scripts/store_to_chromadb.py \
  --session-id "SESSION_ID" \
  --context "CONTEXT_FROM_FILE" \
  --date "YYYY-MM-DD" \
  --type "TYPE" \
  --mood "MOOD" \
  --summary "SUMMARY_TEXT" \
  --ideas '["idea1", "idea2"]' \
  --decisions '["decision1"]' \
  --tags '["tag1", "tag2"]' \
  --open "OPEN_QUESTION_OR_EMPTY" \
  --revisit "REVISIT_DATE_OR_EMPTY" \
  --duration DURATION_MINUTES \
  --project-name "PROJECT_NAME" \
  --files-modified '["file1.py", "file2.py"]' \
  --tools-summary '{"Edit": 5, "Bash": 12}' \
  --outcome "OUTCOME" \
  --continues "PREVIOUS_SESSION_ID_OR_EMPTY" \
  --cwd "/path/to/project" \
  --key-quotes '["quote1", "quote2"]' \
  --code-snippets '["snippet1", "snippet2"]' \
  --commands-executed '["cmd1", "cmd2"]' \
  --errors-encountered '["error1"]' \
  --resources-used '["url1", "url2"]' \
  --milestones '["milestone1", "milestone2"]' \
  --user-questions '["question1", "question2"]'
```

12. **Archive the processed file** (skip if `--dry-run`):

```bash
mv ~/helm/03-rai/semantic-memory/pending/FILENAME.json ~/helm/13-archive/historical-sessions/FILENAME.json
```

### Step 3: Report Results

```markdown
## Session Processing Complete

Processed: X sessions
Skipped: Y sessions (errors)

### Processed Sessions:
- session_id_1 (build, 45m): "brief summary..." [related: 2]
- session_id_2 (debug, 15m): "brief summary..." [continues: session_id_1]
```

## Dry Run Mode

When `--dry-run` is passed:
- Read and summarize files as normal
- Show what WOULD be stored (print the JSON)
- Do NOT call store_to_chromadb.py
- Do NOT delete files

## Transcript Formatting

When reading messages, extract text content:
- Skip `<local-command...` entries and system tags
- Skip thinking blocks (type: "thinking")
- For summary: Focus on substantive exchanges
- For user_questions: Extract from first 3-5 user messages
- For commands: Look for Bash tool_use with actual commands
- For errors: Look for tool_result with is_error=true or error messages
- For code: Look for Edit/Write tool_use with file content
- Truncate long content appropriately (500 chars for messages, 200 for code)

## Auto-Inference Rules

### Type Inference (from tools_summary)
```python
total_tools = sum(tools_summary.values())
edit_write = tools_summary.get("Edit", 0) + tools_summary.get("Write", 0)
read_search = tools_summary.get("Read", 0) + tools_summary.get("Grep", 0) + tools_summary.get("Glob", 0)

if edit_write / total_tools > 0.5:
    session_type = "build"
elif read_search / total_tools > 0.7:
    session_type = "explore"
elif "Task" in tools_summary and "Plan" in conversation:
    session_type = "planning"
elif any(word in conversation.lower() for word in ["error", "fix", "bug", "broken"]):
    session_type = "debug"
else:
    session_type = "brainstorm"
```

### Mood Inference (from sentiment)
```python
low_signals = ["stuck", "not working", "error", "failed", "frustrated", "can't", "won't work"]
high_signals = ["done", "working", "fixed", "shipped", "complete", "success", "great"]

if any(signal in conversation.lower() for signal in low_signals):
    mood = "low"
elif any(signal in conversation.lower() for signal in high_signals):
    mood = "high"
else:
    mood = "med"
```

### Continuation Detection
Check if current session's `project_name` or `cwd` matches a recent session (last 7 days):
```python
# Query ChromaDB for sessions with matching project_name
results = collection.get(
    where={"project_name": current_project_name},
    include=["metadatas"]
)
# If found recent session, set continues=that_session_id
```

## Example Workflow

```
/process-sessions

Found 4 pending sessions:
- session_abc123.json (2026-01-27, build)
- session_def456.json (2026-01-26, debug)
- session_ghi789.json (2026-01-25, planning)
- session_trivial.json (2026-01-25, minimal)

Checking session_trivial.json...
- User messages: 2 (< 4 threshold)
- Plan mode: No
⊘ SKIPPED: Trivial session (< 4 user messages), archived without ChromaDB save

Processing session_abc123.json...
- Save check: 8 user messages, non-plan → SAVE
- Content score calculation:
  · milestones: 3 × 3 = 9 pts
  · code_snippets: 3 × 2 = 6 pts
  · decisions: 2 × 2 = 4 pts
  · Edit+Write tools: 10 pts (capped)
  · files_modified: 5 pts (capped)
  · user_messages: 4 pts (8 × 0.5)
  · Total: 38 pts → 10-15 sentences
- Auto-inferred: type=build (Edit:45, Write:12, Bash:8)
- Auto-inferred: mood=high ("fixed", "working")
- Auto-inferred: outcome=completed (multiplier: 1.0)
✓ Stored: build session about data pipelines [score: 38]

Processing session_def456.json...
- Save check: 6 user messages, non-plan → SAVE
- Content score calculation:
  · milestones: 1 × 3 = 3 pts
  · errors_encountered: 2 × 1 = 2 pts
  · user_messages: 3 pts (6 × 0.5)
  · Edit+Write tools: 2 pts
  · Total: 10 pts → 4-6 sentences
- Auto-inferred: type=debug (mentions "error", "fix")
- Auto-inferred: mood=low ("stuck")
- Auto-inferred: outcome=partial (multiplier: 0.85 → final: 8.5)
- Continues: session_abc123 (same project)
✓ Stored: debug session fixing auth issues [score: 8.5]

Processing session_ghi789.json...
- Save check: Plan mode detected → ALWAYS SAVE
- Content score calculation:
  · milestones: 5 × 3 = 15 pts (capped)
  · key_quotes: 5 × 1 = 5 pts
  · decisions: 4 × 2 = 8 pts
  · ideas: 3 × 1.5 = 4.5 pts
  · user_messages: 10 pts (capped)
  · Total: 42.5 pts → 15-20 sentences
- Auto-inferred: type=planning
- Auto-inferred: mood=high
- Auto-inferred: outcome=completed (multiplier: 1.0)
✓ Stored: planning session for new architecture [score: 42.5]

---
Processed: 3 sessions
Skipped: 1 session (trivial, deleted)
```

## Extraction Guidelines

### Key Quotes
Look for statements that capture important insights:
- User realizations ("I think the issue is...")
- Technical insights ("The key is to...")
- Decisions made ("Let's go with X because...")
- Lessons learned ("Next time we should...")

### Code Snippets
Preserve significant code, truncate to 200 chars:
- New functions/classes written
- Important queries (SQL, API calls)
- Configuration changes
- NOT trivial edits or imports

### Commands Executed
Track important bash commands:
- Deployment commands (git push, docker build)
- Test commands (pytest, npm test)
- Database operations
- NOT trivial (ls, cd, cat)

### Errors Encountered
Capture the actual error text:
- Exception messages
- Build failures
- Test failures
- API errors

### Resources Used
Extract URLs and important paths:
- Documentation links
- Stack Overflow answers
- API documentation
- Key files modified

### Milestones
Identify progress points:
- "Fixed the authentication bug"
- "Deployed to production"
- "Completed the refactor"
- "Tests passing"
