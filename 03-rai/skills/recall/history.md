---
name: history
description: Semantic + filter queries over ChromaDB session memory. Invoked via /recall router.
allowed-tools: Bash, Read
argument-hint: [--search "query"] [--recent] [--pending] [--project X] [--type X] [--related ID] [--chain ID] [--files "*.py"]
---

# History Recall - Query ChromaDB Session Memory

Recall memories from ChromaDB session storage.

## Arguments

| Argument | Description |
|----------|-------------|
| (none) | Load ALL memories |
| `--recent` | Last 30 days only |
| `--search "query"` | Semantic search (top 50 results) |
| `--pending` | Show memories with passed revisit dates |
| `--project X` | Filter by project_name |
| `--type X` | Filter by session type (build/debug/explore/planning/brainstorm) |
| `--related ID` | Get sessions semantically related to session ID |
| `--chain ID` | Follow continuation chain from session ID |
| `--files "pattern"` | Sessions that modified files matching pattern |
| `--detailed ID` | Show full details for a specific session (all extracted fields) |

## Instructions

1. **Parse arguments** from `$ARGUMENTS`

2. **Query ChromaDB** using appropriate Python snippet:

### Default: All Memories
```bash
~/helm/03-rai/semantic-memory/scripts/py-chroma.sh -c "
import chromadb
import json
from pathlib import Path

client = chromadb.PersistentClient(path=str(Path.home() / 'helm/03-rai/semantic-memory/chromadb'))
collection = client.get_collection('memories')
result = collection.get(include=['metadatas', 'documents'])

for i, doc in enumerate(result.get('documents', [])):
    meta = result['metadatas'][i]
    duration = meta.get('duration_minutes', 0)
    duration_str = f' ({duration}m)' if duration else ''
    project = meta.get('project_name', '')
    project_str = f' [{project}]' if project else ''

    print(f\"📅 {meta.get('date', 'unknown')} | {meta.get('type', 'session')}{duration_str}{project_str} | {meta.get('mood', '')}\")
    print(f\"   {doc[:200]}...\")

    if meta.get('outcome'):
        print(f\"   📊 Outcome: {meta.get('outcome')}\")
    if meta.get('continues'):
        print(f\"   🔗 Continues: {meta.get('continues')}\")
    if meta.get('open'):
        print(f\"   ⚠️ Open: {meta.get('open')}\")
    if meta.get('ideas'):
        ideas = meta.get('ideas', '')
        if ideas and ideas != '[]':
            print(f\"   💡 Ideas: {ideas[:100]}\")
    if meta.get('files_modified'):
        files = meta.get('files_modified', '[]')
        try:
            files_list = json.loads(files) if isinstance(files, str) else files
            if files_list:
                print(f\"   📝 Files: {len(files_list)} modified\")
        except: pass
    if meta.get('revisit'):
        print(f\"   📌 Revisit: {meta.get('revisit')}\")
    print()
"
```

### With --recent flag
```bash
~/helm/03-rai/semantic-memory/scripts/py-chroma.sh -c "
import chromadb
from pathlib import Path
from datetime import datetime, timedelta

client = chromadb.PersistentClient(path=str(Path.home() / 'helm/03-rai/semantic-memory/chromadb'))
collection = client.get_collection('memories')
result = collection.get(include=['metadatas', 'documents'])

cutoff = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')

for i, doc in enumerate(result.get('documents', [])):
    meta = result['metadatas'][i]
    if meta.get('date', '') >= cutoff:
        print(f\"📅 {meta.get('date', 'unknown')} | {meta.get('type', 'session')} | {meta.get('mood', '')}\")
        print(f\"   {doc[:200]}...\")
        if meta.get('open'):
            print(f\"   ⚠️ Open: {meta.get('open')}\")
        if meta.get('ideas'):
            ideas = meta.get('ideas', '')
            if ideas and ideas != '[]':
                print(f\"   💡 Ideas: {ideas[:100]}\")
        print()
"
```

### With --search "query"
```bash
~/helm/03-rai/semantic-memory/scripts/py-chroma.sh -c "
import chromadb
from pathlib import Path

client = chromadb.PersistentClient(path=str(Path.home() / 'helm/03-rai/semantic-memory/chromadb'))
collection = client.get_collection('memories')
result = collection.query(query_texts=['SEARCH_QUERY_HERE'], n_results=50, include=['metadatas', 'documents', 'distances'])

for i, doc in enumerate(result.get('documents', [[]])[0]):
    meta = result['metadatas'][0][i]
    distance = result['distances'][0][i]
    print(f\"📅 {meta.get('date', 'unknown')} | {meta.get('type', 'session')} | similarity: {1-distance:.2f}\")
    print(f\"   {doc[:200]}...\")
    if meta.get('open'):
        print(f\"   ⚠️ Open: {meta.get('open')}\")
    print()
"
```

### With --pending flag
```bash
~/helm/03-rai/semantic-memory/scripts/py-chroma.sh -c "
import chromadb
from pathlib import Path
from datetime import datetime

client = chromadb.PersistentClient(path=str(Path.home() / 'helm/03-rai/semantic-memory/chromadb'))
collection = client.get_collection('memories')
result = collection.get(include=['metadatas', 'documents'])

today = datetime.now().strftime('%Y-%m-%d')

for i, doc in enumerate(result.get('documents', [])):
    meta = result['metadatas'][i]
    revisit = meta.get('revisit', '')
    if revisit and revisit <= today:
        print(f\"📅 {meta.get('date', 'unknown')} | REVISIT DUE: {revisit}\")
        print(f\"   {doc[:200]}...\")
        if meta.get('open'):
            print(f\"   ⚠️ Open: {meta.get('open')}\")
        print()
"
```

### With --project X
```bash
~/helm/03-rai/semantic-memory/scripts/py-chroma.sh -c "
import chromadb
from pathlib import Path

client = chromadb.PersistentClient(path=str(Path.home() / 'helm/03-rai/semantic-memory/chromadb'))
collection = client.get_collection('memories')
result = collection.get(include=['metadatas', 'documents'])

project = 'PROJECT_NAME_HERE'.lower()

for i, doc in enumerate(result.get('documents', [])):
    meta = result['metadatas'][i]
    project_name = meta.get('project_name', '').lower()
    context = meta.get('context', '').lower()
    tags = meta.get('tags', '').lower()
    if project in project_name or project in context or project in tags:
        duration = meta.get('duration_minutes', 0)
        duration_str = f' ({duration}m)' if duration else ''
        print(f\"📅 {meta.get('date', 'unknown')} | {meta.get('type', 'session')}{duration_str}\")
        print(f\"   {doc[:200]}...\")
        if meta.get('open'):
            print(f\"   ⚠️ Open: {meta.get('open')}\")
        print()
"
```

### With --type X (filter by session type)
```bash
~/helm/03-rai/semantic-memory/scripts/py-chroma.sh -c "
import chromadb
from pathlib import Path

client = chromadb.PersistentClient(path=str(Path.home() / 'helm/03-rai/semantic-memory/chromadb'))
collection = client.get_collection('memories')
result = collection.get(include=['metadatas', 'documents'])

session_type = 'TYPE_HERE'.lower()

for i, doc in enumerate(result.get('documents', [])):
    meta = result['metadatas'][i]
    if meta.get('type', '').lower() == session_type:
        duration = meta.get('duration_minutes', 0)
        project = meta.get('project_name', '')
        print(f\"📅 {meta.get('date', 'unknown')} | {meta.get('type')} ({duration}m) [{project}]\")
        print(f\"   {doc[:200]}...\")
        if meta.get('outcome'):
            print(f\"   📊 Outcome: {meta.get('outcome')}\")
        print()
"
```

### With --related ID (get semantically related sessions)
```bash
~/helm/03-rai/semantic-memory/scripts/py-chroma.sh -c "
import chromadb
import json
from pathlib import Path

client = chromadb.PersistentClient(path=str(Path.home() / 'helm/03-rai/semantic-memory/chromadb'))
collection = client.get_collection('memories')

session_id = 'SESSION_ID_HERE'

# Get the target session
target = collection.get(ids=[session_id], include=['documents', 'metadatas'])
if not target['documents']:
    print(f'Session {session_id} not found')
    exit()

target_doc = target['documents'][0]
target_meta = target['metadatas'][0]
print(f'Target session: {session_id}')
print(f'   {target_doc[:150]}...')
print()

# Check stored related_to
related_ids = json.loads(target_meta.get('related_to', '[]'))
if related_ids:
    print('Stored related sessions:')
    for rid in related_ids:
        r = collection.get(ids=[rid], include=['documents', 'metadatas'])
        if r['documents']:
            rm = r['metadatas'][0]
            print(f\"  📅 {rm.get('date')} | {rm.get('type')} | {rid}\")
            print(f\"     {r['documents'][0][:100]}...\")
    print()

# Also do semantic search for more
print('Semantically similar sessions:')
results = collection.query(query_texts=[target_doc], n_results=6, include=['metadatas', 'documents', 'distances'])
for i, doc in enumerate(results['documents'][0]):
    if results['ids'][0][i] == session_id:
        continue
    meta = results['metadatas'][0][i]
    similarity = 1 - results['distances'][0][i]
    print(f\"  📅 {meta.get('date')} | {meta.get('type')} | sim={similarity:.2f}\")
    print(f\"     {doc[:100]}...\")
"
```

### With --chain ID (follow continuation chain)
```bash
~/helm/03-rai/semantic-memory/scripts/py-chroma.sh -c "
import chromadb
import json
from pathlib import Path

client = chromadb.PersistentClient(path=str(Path.home() / 'helm/03-rai/semantic-memory/chromadb'))
collection = client.get_collection('memories')

session_id = 'SESSION_ID_HERE'
chain = []
current_id = session_id

# Follow the chain backwards (find what this continues)
while current_id:
    result = collection.get(ids=[current_id], include=['metadatas', 'documents'])
    if not result['documents']:
        break
    meta = result['metadatas'][0]
    chain.insert(0, (current_id, meta, result['documents'][0]))
    current_id = meta.get('continues', '')

# Follow forward (find what continues this)
current_id = session_id
all_results = collection.get(include=['metadatas'])
for i, meta in enumerate(all_results['metadatas']):
    if meta.get('continues') == session_id:
        forward_id = all_results['ids'][i]
        forward_result = collection.get(ids=[forward_id], include=['documents', 'metadatas'])
        if forward_result['documents']:
            chain.append((forward_id, forward_result['metadatas'][0], forward_result['documents'][0]))

print(f'Session chain ({len(chain)} sessions):')
for i, (sid, meta, doc) in enumerate(chain):
    marker = '>>> ' if sid == session_id else '    '
    duration = meta.get('duration_minutes', 0)
    print(f\"{marker}{i+1}. 📅 {meta.get('date')} | {meta.get('type')} ({duration}m)\")
    print(f\"       {doc[:100]}...\")
    if meta.get('continues'):
        print(f\"       🔗 Continues: {meta.get('continues')[:20]}...\")
"
```

### With --files "pattern" (sessions that modified matching files)
```bash
~/helm/03-rai/semantic-memory/scripts/py-chroma.sh -c "
import chromadb
import json
import fnmatch
from pathlib import Path

client = chromadb.PersistentClient(path=str(Path.home() / 'helm/03-rai/semantic-memory/chromadb'))
collection = client.get_collection('memories')
result = collection.get(include=['metadatas', 'documents'])

pattern = 'PATTERN_HERE'

for i, doc in enumerate(result.get('documents', [])):
    meta = result['metadatas'][i]
    files_json = meta.get('files_modified', '[]')
    try:
        files = json.loads(files_json) if isinstance(files_json, str) else files_json
    except:
        files = []

    matching_files = [f for f in files if fnmatch.fnmatch(f, pattern) or fnmatch.fnmatch(Path(f).name, pattern)]

    if matching_files:
        duration = meta.get('duration_minutes', 0)
        print(f\"📅 {meta.get('date', 'unknown')} | {meta.get('type', 'session')} ({duration}m)\")
        print(f\"   {doc[:150]}...\")
        print(f\"   📝 Matching files:\")
        for f in matching_files[:5]:
            print(f\"      - {f}\")
        if len(matching_files) > 5:
            print(f\"      ... and {len(matching_files) - 5} more\")
        print()
"
```

### With --detailed ID (show full session details)
```bash
~/helm/03-rai/semantic-memory/scripts/py-chroma.sh -c "
import chromadb
import json
from pathlib import Path

client = chromadb.PersistentClient(path=str(Path.home() / 'helm/03-rai/semantic-memory/chromadb'))
collection = client.get_collection('memories')

session_id = 'SESSION_ID_HERE'
result = collection.get(ids=[session_id], include=['documents', 'metadatas'])

if not result['documents']:
    print(f'Session {session_id} not found')
    exit()

doc = result['documents'][0]
meta = result['metadatas'][0]

def parse_json(val):
    if not val: return []
    try: return json.loads(val) if isinstance(val, str) else val
    except: return []

print('=' * 60)
print(f\"📅 Date: {meta.get('date', 'unknown')}\")
print(f\"📁 Project: {meta.get('project_name', 'unknown')}\")
print(f\"🏷️  Type: {meta.get('type', 'unknown')} | Mood: {meta.get('mood', 'unknown')} | Outcome: {meta.get('outcome', 'unknown')}\")
print(f\"⏱️  Duration: {meta.get('duration_minutes', 0)} minutes\")
print(f\"📂 CWD: {meta.get('cwd', 'unknown')}\")
print('=' * 60)

print(f\"\n📝 SUMMARY:\n{doc}\")

user_questions = parse_json(meta.get('user_questions'))
if user_questions:
    print(f\"\n❓ USER QUESTIONS:\")
    for q in user_questions:
        print(f\"   • {q}\")

key_quotes = parse_json(meta.get('key_quotes'))
if key_quotes:
    print(f\"\n💬 KEY QUOTES:\")
    for q in key_quotes:
        print(f\"   \\\"{q}\\\"\")

milestones = parse_json(meta.get('milestones'))
if milestones:
    print(f\"\n🎯 MILESTONES:\")
    for m in milestones:
        print(f\"   ✓ {m}\")

code_snippets = parse_json(meta.get('code_snippets'))
if code_snippets:
    print(f\"\n💻 CODE SNIPPETS:\")
    for c in code_snippets:
        print(f\"   ```\n   {c[:150]}{'...' if len(c) > 150 else ''}\n   ```\")

commands = parse_json(meta.get('commands_executed'))
if commands:
    print(f\"\n🔧 COMMANDS EXECUTED:\")
    for c in commands:
        print(f\"   $ {c}\")

errors = parse_json(meta.get('errors_encountered'))
if errors:
    print(f\"\n❌ ERRORS ENCOUNTERED:\")
    for e in errors:
        print(f\"   {e[:100]}{'...' if len(e) > 100 else ''}\")

resources = parse_json(meta.get('resources_used'))
if resources:
    print(f\"\n🔗 RESOURCES USED:\")
    for r in resources:
        print(f\"   {r}\")

files = parse_json(meta.get('files_modified'))
if files:
    print(f\"\n📄 FILES MODIFIED ({len(files)}):\")
    for f in files[:10]:
        print(f\"   {f}\")
    if len(files) > 10:
        print(f\"   ... and {len(files) - 10} more\")

ideas = parse_json(meta.get('ideas'))
if ideas:
    print(f\"\n💡 IDEAS:\")
    for i in ideas:
        print(f\"   • {i}\")

decisions = parse_json(meta.get('decisions'))
if decisions:
    print(f\"\n✅ DECISIONS:\")
    for d in decisions:
        print(f\"   • {d}\")

if meta.get('open'):
    print(f\"\n⚠️  OPEN QUESTION: {meta.get('open')}\")

if meta.get('continues'):
    print(f\"\n🔗 Continues session: {meta.get('continues')}\")

related = parse_json(meta.get('related_to'))
if related:
    print(f\"\n🔀 Related sessions: {', '.join(related)}\")

if meta.get('revisit'):
    print(f\"\n📌 Revisit by: {meta.get('revisit')}\")

print('=' * 60)
"
```

3. **Format output**:

```markdown
## 🧠 Session Memory

[Memory entries from ChromaDB query]

---

*Query: [describe what was searched/filtered]*
*Total memories: [count]*
```

## Example Output

### Default list view:
```
## 🧠 Session Memory

📅 2026-01-25 | build (45m) [my-project] | high
   Implemented data pipeline with Kafka streaming. Added CDC for real-time...
   📊 Outcome: completed
   📝 Files: 8 modified
   💡 Ideas: ["Use streaming instead of batch", "Add dead letter queue"]

📅 2026-01-24 | debug (20m) [my-project] | low
   Fixed authentication issue in API gateway. Token refresh was failing...
   🔗 Continues: abc123
   ⚠️ Open: Need to add rate limiting

---
*Query: --recent (last 30 days)*
*Total memories: 12*
```

### Detailed view (--detailed ID):
```
============================================================
📅 Date: 2026-01-25
📁 Project: my-project
🏷️  Type: build | Mood: high | Outcome: completed
⏱️  Duration: 45 minutes
📂 CWD: /Users/me/projects/my-project
============================================================

📝 SUMMARY:
Implemented real-time data pipeline using Kafka. Set up CDC with Debezium
for capturing database changes. Created consumer service to process events
and update the data warehouse. Added error handling with dead letter queue.
Tested end-to-end flow with sample data. Performance looks good at 1000 msg/s.

❓ USER QUESTIONS:
   • How do I set up CDC with Kafka?
   • Can we handle schema evolution?

💬 KEY QUOTES:
   "The key insight is that CDC captures changes at the database level"
   "Dead letter queues are essential for production reliability"

🎯 MILESTONES:
   ✓ Kafka producer configured
   ✓ Debezium CDC connector working
   ✓ Consumer service deployed
   ✓ End-to-end test passing

💻 CODE SNIPPETS:
   ```
   def process_event(event): consumer.subscribe([...
   ```

🔧 COMMANDS EXECUTED:
   $ docker-compose up -d kafka
   $ pytest tests/integration/

🔗 RESOURCES USED:
   https://debezium.io/documentation/
   https://kafka.apache.org/documentation/

📄 FILES MODIFIED (8):
   /src/pipeline/consumer.py
   /src/pipeline/producer.py
   /config/kafka.yaml
   ... and 5 more

💡 IDEAS:
   • Use streaming instead of batch processing
   • Add dead letter queue for failed messages

✅ DECISIONS:
   • Go with Debezium for CDC over custom solution

============================================================
```

## Schema Reference

ChromaDB metadata fields:

### Original Fields (v1)
- `date`: YYYY-MM-DD
- `context`: Mapped context name from cwd
- `type`: brainstorm|debug|planning|learning|build|explore (auto-inferred)
- `mood`: low|med|high (auto-inferred from sentiment)
- `tags`: comma-separated string
- `ideas`: JSON array string
- `decisions`: JSON array string
- `open`: unresolved question or empty
- `revisit`: YYYY-MM-DD or empty

### Metadata Fields (v2)
- `duration_minutes`: Session length in minutes
- `project_name`: Detected from .git/pyproject.toml/package.json/folder
- `files_modified`: JSON array of full file paths edited/written
- `tools_summary`: JSON dict of tool usage counts {"Edit": 5, "Bash": 12}
- `outcome`: completed|partial|blocked|exploration (auto-inferred)
- `continues`: Session ID this continues (auto-detected)
- `related_to`: JSON array of semantically related session IDs
- `cwd`: Working directory path

### Rich Extraction Fields (v3)
- `key_quotes`: JSON array of important insights/statements (max 5)
- `code_snippets`: JSON array of significant code written (max 3, 200 chars each)
- `commands_executed`: JSON array of important bash commands (max 5)
- `errors_encountered`: JSON array of error messages (max 3)
- `resources_used`: JSON array of URLs/docs referenced (max 5)
- `milestones`: JSON array of progress points (max 5)
- `user_questions`: JSON array of user's original questions (max 3)

### Adaptive Summary Length
| Duration | Summary Length |
|----------|----------------|
| < 15m | 3-5 sentences |
| 15-30m | 6-8 sentences |
| 30-60m | 8-12 sentences |
| 60m+ | 12-20 sentences |

## Benefits
- **Semantic search**: Find "auth sessions" even if exact words differ
- **No file loading**: Direct database queries
- **Local embeddings**: Uses sentence-transformers (all-MiniLM-L6-v2)
- **Scalable**: Handles thousands of memories efficiently
- **Relationship tracking**: Follow continuation chains and related sessions
- **File-based queries**: Find sessions that touched specific files
- **Rich extraction**: Preserve code, commands, errors, quotes for future reference
- **Adaptive depth**: Longer sessions get more detailed summaries
