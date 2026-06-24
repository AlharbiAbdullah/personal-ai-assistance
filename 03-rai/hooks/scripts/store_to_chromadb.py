#!/usr/bin/env python3
"""
Store session summary to ChromaDB.

Called by /process-sessions skill to store summarized sessions.
Extracted from summarize_sessions.py to support manual processing.

Usage:
    python3 store_to_chromadb.py \
        --session-id "abc123" \
        --context "my-project" \
        --date "2026-01-27" \
        --type "brainstorm" \
        --mood "high" \
        --summary "Session summary text..." \
        --ideas '["idea1", "idea2"]' \
        --decisions '["decision1"]' \
        --tags '["tag1", "tag2"]' \
        --open "unresolved question" \
        --revisit "2026-02-01" \
        --duration 45 \
        --project-name "my-project" \
        --files-modified '["file1.py", "file2.py"]' \
        --tools-summary '{"Edit": 5, "Bash": 12}' \
        --outcome "completed" \
        --continues "previous-session-id" \
        --cwd "/path/to/project" \
        --key-quotes '["important insight here", "another quote"]' \
        --code-snippets '["def func(): pass", "SELECT * FROM"]' \
        --commands-executed '["git push", "pytest"]' \
        --errors-encountered '["ModuleNotFoundError: xyz"]' \
        --resources-used '["https://docs.example.com"]' \
        --milestones '["Fixed auth bug", "Deployed to prod"]' \
        --user-questions '["How do I X?", "Why is Y failing?"]'
"""

import argparse
import json
import sys
from pathlib import Path

import chromadb

CHROMADB_DIR = Path.home() / "helm" / "03-rai" / "semantic-memory" / "chromadb"


def get_chromadb_collection():
    """Get or create ChromaDB collection."""
    CHROMADB_DIR.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(CHROMADB_DIR))
    return client.get_or_create_collection(
        name="memories",
        metadata={"hnsw:space": "cosine"},
    )


def parse_json_arg(value: str) -> list:
    """Parse JSON array argument, return empty list on failure."""
    if not value:
        return []
    try:
        result = json.loads(value)
        return result if isinstance(result, list) else []
    except json.JSONDecodeError:
        return []


def find_related_sessions(collection, summary: str, current_id: str, threshold: float = 0.85) -> list:
    """Find semantically related sessions using embedding similarity."""
    try:
        results = collection.query(
            query_texts=[summary],
            n_results=5,
            include=["distances"],
        )
        related = []
        for i, distance in enumerate(results.get("distances", [[]])[0]):
            similarity = 1 - distance
            session_id = results.get("ids", [[]])[0][i]
            if similarity >= threshold and session_id != current_id:
                related.append(session_id)
            if len(related) >= 3:
                break
        return related
    except Exception:
        return []


def main():
    """Store session summary in ChromaDB."""
    parser = argparse.ArgumentParser(description="Store session summary to ChromaDB")
    parser.add_argument("--session-id", required=True, help="Unique session ID")
    parser.add_argument("--context", default="brainstorm", help="Project/context name")
    parser.add_argument("--date", required=True, help="Session date (YYYY-MM-DD)")
    parser.add_argument("--type", default="brainstorm", help="Session type")
    parser.add_argument("--mood", default="med", help="Session mood (low/med/high)")
    parser.add_argument("--summary", required=True, help="Session summary text")
    parser.add_argument("--ideas", default="[]", help="JSON array of ideas")
    parser.add_argument("--decisions", default="[]", help="JSON array of decisions")
    parser.add_argument("--tags", default="[]", help="JSON array of tags")
    parser.add_argument("--open", default="", help="Open/unresolved question")
    parser.add_argument("--revisit", default="", help="Revisit date (YYYY-MM-DD)")
    # New fields (v2)
    parser.add_argument("--duration", type=int, default=0, help="Session duration in minutes")
    parser.add_argument("--project-name", default="", help="Detected project name")
    parser.add_argument("--files-modified", default="[]", help="JSON array of modified file paths")
    parser.add_argument("--tools-summary", default="{}", help="JSON dict of tool usage counts")
    parser.add_argument("--outcome", default="", help="Session outcome: completed|partial|blocked|exploration")
    parser.add_argument("--continues", default="", help="ID of previous session this continues")
    parser.add_argument("--cwd", default="", help="Working directory path")
    # New fields (v3) - rich extraction
    parser.add_argument("--key-quotes", default="[]", help="JSON array of important quotes/insights")
    parser.add_argument("--code-snippets", default="[]", help="JSON array of important code written")
    parser.add_argument("--commands-executed", default="[]", help="JSON array of significant bash commands")
    parser.add_argument("--errors-encountered", default="[]", help="JSON array of error messages")
    parser.add_argument("--resources-used", default="[]", help="JSON array of URLs/docs referenced")
    parser.add_argument("--milestones", default="[]", help="JSON array of progress milestones")
    parser.add_argument("--user-questions", default="[]", help="JSON array of user's original questions")

    args = parser.parse_args()

    # Parse JSON arrays/objects
    ideas = parse_json_arg(args.ideas)
    decisions = parse_json_arg(args.decisions)
    tags = parse_json_arg(args.tags)
    files_modified = parse_json_arg(args.files_modified)
    # New v3 fields
    key_quotes = parse_json_arg(args.key_quotes)
    code_snippets = parse_json_arg(args.code_snippets)
    commands_executed = parse_json_arg(args.commands_executed)
    errors_encountered = parse_json_arg(args.errors_encountered)
    resources_used = parse_json_arg(args.resources_used)
    milestones = parse_json_arg(args.milestones)
    user_questions = parse_json_arg(args.user_questions)

    try:
        tools_summary = json.loads(args.tools_summary) if args.tools_summary else {}
    except json.JSONDecodeError:
        tools_summary = {}

    # Prepare metadata
    metadata = {
        "date": args.date,
        "context": args.context,
        "type": args.type,
        "mood": args.mood,
        "tags": ",".join(tags),
        "ideas": json.dumps(ideas),
        "decisions": json.dumps(decisions),
        "open": args.open,
        "revisit": args.revisit,
        # v2 fields
        "duration_minutes": args.duration,
        "project_name": args.project_name,
        "files_modified": json.dumps(files_modified),
        "tools_summary": json.dumps(tools_summary),
        "outcome": args.outcome,
        "continues": args.continues,
        "cwd": args.cwd,
        # v3 fields - rich extraction
        "key_quotes": json.dumps(key_quotes),
        "code_snippets": json.dumps(code_snippets),
        "commands_executed": json.dumps(commands_executed),
        "errors_encountered": json.dumps(errors_encountered),
        "resources_used": json.dumps(resources_used),
        "milestones": json.dumps(milestones),
        "user_questions": json.dumps(user_questions),
    }

    # Create document text for embedding (include key content for semantic search)
    document = args.summary
    if user_questions:
        document += f" Questions: {'; '.join(user_questions[:3])}"
    if ideas:
        document += f" Ideas: {', '.join(ideas)}"
    if decisions:
        document += f" Decisions: {', '.join(decisions)}"
    if milestones:
        document += f" Milestones: {'; '.join(milestones)}"
    if errors_encountered:
        document += f" Errors: {'; '.join(errors_encountered[:2])}"

    # Store in ChromaDB
    try:
        collection = get_chromadb_collection()

        # Find semantically related sessions before storing
        related_to = find_related_sessions(collection, document, args.session_id)
        metadata["related_to"] = json.dumps(related_to)

        collection.add(
            ids=[args.session_id],
            documents=[document],
            metadatas=[metadata],
        )
        related_msg = f" (related to {len(related_to)} sessions)" if related_to else ""
        print(f"Stored {args.session_id} in ChromaDB{related_msg}")
        return 0
    except Exception as e:
        print(f"Error storing in ChromaDB: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
