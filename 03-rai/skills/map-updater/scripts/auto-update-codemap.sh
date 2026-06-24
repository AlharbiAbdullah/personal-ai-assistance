#!/bin/bash
# Auto-update codemap when project structure changes
# Triggers on: new file, new folder, deleted file/folder

PROJECT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
CODEMAP_DIR="$PROJECT_ROOT/.codemap"

# Only proceed if .codemap/ exists in this project
if [ ! -d "$CODEMAP_DIR" ]; then
    exit 0
fi

# Skip changes inside .codemap itself
FILE_PATH="${CLAUDE_TOOL_ARG_FILE_PATH:-$1}"
if [[ "$FILE_PATH" == *"/.codemap/"* ]]; then
    exit 0
fi

# Skip hidden/system directories
if [[ "$FILE_PATH" == *"/node_modules/"* ]] || \
   [[ "$FILE_PATH" == *"/.git/"* ]] || \
   [[ "$FILE_PATH" == *"/__pycache__/"* ]] || \
   [[ "$FILE_PATH" == *"/.venv/"* ]] || \
   [[ "$FILE_PATH" == *"/venv/"* ]]; then
    exit 0
fi

echo ""
echo "[CODEMAP] Structure changed: $FILE_PATH"
echo "[CODEMAP] Update .codemap/codemap.md - reflect new/removed files in Structure section."
echo ""
