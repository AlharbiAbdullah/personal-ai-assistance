#!/bin/bash
# Codemap Update Suggester
# Runs after Write operations to suggest codemap update when structure changes
#
# Tracks new files created. When threshold reached, suggests /map-updater

PROJECT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
TRACKER_FILE="/tmp/claude-new-files-$$"
THRESHOLD=${CODEMAP_THRESHOLD:-5}

# Get the file that was just written (passed as argument or from environment)
NEW_FILE="${1:-$CLAUDE_TOOL_ARG_FILE_PATH}"

# Only track if it's a new file (not an edit)
if [ -n "$NEW_FILE" ] && [ ! -f "$TRACKER_FILE" ]; then
    echo "0" > "$TRACKER_FILE"
fi

if [ -f "$TRACKER_FILE" ]; then
    count=$(cat "$TRACKER_FILE")
    count=$((count + 1))
    echo "$count" > "$TRACKER_FILE"

    # Suggest after threshold new files
    if [ "$count" -eq "$THRESHOLD" ]; then
        echo "[CodeMapUpdater] $THRESHOLD files created - consider /map-updater to update navigation map" >&2
    fi

    # Remind at intervals
    if [ "$count" -gt "$THRESHOLD" ] && [ $((count % 5)) -eq 0 ]; then
        echo "[CodeMapUpdater] $count files created - CODEMAP.md may be stale" >&2
    fi
fi
