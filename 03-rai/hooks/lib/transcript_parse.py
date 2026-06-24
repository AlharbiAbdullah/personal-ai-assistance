"""Shared transcript JSONL walker."""

import json
from pathlib import Path
from typing import Iterator


def iter_transcript(transcript_path: str) -> Iterator[dict]:
    """Yield parsed JSON entries from a transcript JSONL file. Silent on failure."""
    if not transcript_path:
        return
    path = Path(transcript_path)
    if not path.exists():
        return
    try:
        with path.open() as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    yield json.loads(line)
                except json.JSONDecodeError:
                    continue
    except Exception:
        return


def iter_assistant_tool_uses(transcript_path: str) -> Iterator[dict]:
    """Yield every tool_use block from assistant messages."""
    for entry in iter_transcript(transcript_path):
        if entry.get("type") != "assistant":
            continue
        content = entry.get("message", {}).get("content", [])
        if not isinstance(content, list):
            continue
        for item in content:
            if isinstance(item, dict) and item.get("type") == "tool_use":
                yield item


def extract_modified_files(transcript_path: str) -> list[str]:
    """Unique file_path values from Edit/Write/NotebookEdit tool calls, in order."""
    paths: list[str] = []
    seen: set[str] = set()
    for tool_use in iter_assistant_tool_uses(transcript_path):
        name = tool_use.get("name", "")
        if name not in ("Edit", "Write", "NotebookEdit"):
            continue
        fp = tool_use.get("input", {}).get("file_path", "")
        if fp and fp not in seen:
            seen.add(fp)
            paths.append(fp)
    return paths


def extract_user_messages(transcript_path: str) -> list[str]:
    """Yield user message text in order. Handles list/string content forms."""
    out: list[str] = []
    for entry in iter_transcript(transcript_path):
        if entry.get("type") != "user":
            continue
        content = entry.get("message", {}).get("content", "")
        if isinstance(content, str):
            if content.strip():
                out.append(content)
        elif isinstance(content, list):
            for item in content:
                if isinstance(item, dict) and item.get("type") == "text":
                    txt = item.get("text", "")
                    if txt.strip():
                        out.append(txt)
    return out
