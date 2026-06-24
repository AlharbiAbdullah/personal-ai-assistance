#!/bin/bash
# Trigger codemap update on structure-changing bash commands
# Only fires for: rm, rmdir, mkdir, mv (structural changes)

PROJECT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
CODEMAP_DIR="$PROJECT_ROOT/.codemap"

# Only proceed if .codemap/ exists
if [ ! -d "$CODEMAP_DIR" ]; then
    exit 0
fi

# Get the bash command that was executed
BASH_CMD="${CLAUDE_TOOL_ARG_COMMAND:-}"

# Only trigger on structure-changing commands
case "$BASH_CMD" in
    rm\ *|rmdir\ *|mkdir\ *|mv\ *)
        # Skip if operating on system/hidden dirs
        if [[ "$BASH_CMD" == *"node_modules"* ]] || \
           [[ "$BASH_CMD" == *".git/"* ]] || \
           [[ "$BASH_CMD" == *"__pycache__"* ]] || \
           [[ "$BASH_CMD" == *".codemap/"* ]]; then
            exit 0
        fi

        echo ""
        echo "[CODEMAP] Structure changed via: ${BASH_CMD:0:60}..."
        echo "[CODEMAP] Update .codemap/codemap.md - reflect changes in Structure section."
        echo ""
        ;;
    *)
        # Not a structure-changing command, exit silently
        exit 0
        ;;
esac
