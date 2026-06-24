#!/usr/bin/env bash
# /ask-model — single-shot OpenRouter call with JSONL logging.
#
# Usage:
#   call.sh <model-alias> <task> <prompt-file> [system-file]
#
# model-alias: gemini | gpt
# task:        write | translate | judge | critique | summarize | freeform
# prompt-file: path to a file containing the user prompt (the actual content/task)
# system-file: optional path to a file containing the system prompt
#
# Env:
#   OPENROUTER_API_KEY  required
#
# Output: prints the model's response to stdout. Appends a JSONL log entry to
# ~/helm/03-rai/memory/ai-calls/YYYY-MM-DD.jsonl.

set -euo pipefail

if [[ $# -lt 3 ]]; then
  echo "usage: call.sh <gemini|gpt> <task> <prompt-file> [system-file]" >&2
  exit 2
fi

ALIAS="$1"
TASK="$2"
PROMPT_FILE="$3"
SYSTEM_FILE="${4:-}"

if [[ -z "${OPENROUTER_API_KEY:-}" ]]; then
  echo "error: OPENROUTER_API_KEY env var not set" >&2
  echo "       export it in ~/.zshrc or pass via env, then retry" >&2
  exit 3
fi

case "$ALIAS" in
  gemini) MODEL="google/gemini-3.1-pro-preview" ;;
  gpt)    MODEL="openai/gpt-5.5" ;;
  claude) MODEL="anthropic/claude-opus-4.7" ;;
  *)
    echo "error: unknown model alias '$ALIAS'. expected: gemini | gpt | claude" >&2
    exit 2
    ;;
esac

[[ -f "$PROMPT_FILE" ]] || { echo "error: prompt file not found: $PROMPT_FILE" >&2; exit 2; }
PROMPT=$(cat "$PROMPT_FILE")

SYSTEM=""
if [[ -n "$SYSTEM_FILE" && -f "$SYSTEM_FILE" ]]; then
  # Preprocess INCLUDE: directives. Any line `INCLUDE: <path>` (tilde-expanded)
  # is replaced with the file's contents, wrapped in a section header.
  # Loops to a fixed point so an included file can itself contain INCLUDEs
  # (e.g. a CORPUS.md that includes a glob of sample files).
  SYSTEM=$(cat "$SYSTEM_FILE")
  for _ in 1 2 3 4 5; do
    grep -q '^INCLUDE: ' <<<"$SYSTEM" || break
    SYSTEM=$(printf '%s\n' "$SYSTEM" | awk '
      /^INCLUDE: / {
        path = $0
        sub(/^INCLUDE: /, "", path)
        gsub(/^~/, ENVIRON["HOME"], path)
        printf "\n=== INCLUDED FROM: %s ===\n", path
        while ((getline line < path) > 0) print line
        close(path)
        printf "=== END INCLUDE ===\n\n"
        next
      }
      { print }
    ')
  done
fi

LOG_DIR="$HOME/helm/03-rai/memory/ai-calls"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/$(date -u +%Y-%m-%d).jsonl"

# Build messages JSON via jq (avoids quoting hell).
if [[ -n "$SYSTEM" ]]; then
  MESSAGES=$(jq -n --arg sys "$SYSTEM" --arg user "$PROMPT" \
    '[{role:"system",content:$sys},{role:"user",content:$user}]')
else
  MESSAGES=$(jq -n --arg user "$PROMPT" \
    '[{role:"user",content:$user}]')
fi

PAYLOAD=$(jq -n --arg model "$MODEL" --argjson messages "$MESSAGES" \
  '{model:$model, messages:$messages, max_tokens:32000, usage:{include:true}}')

STARTED_AT=$(date -u +%Y-%m-%dT%H:%M:%SZ)

RESPONSE=$(curl -sS https://openrouter.ai/api/v1/chat/completions \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -H "Content-Type: application/json" \
  -H "HTTP-Referer: https://johndoe.dev" \
  -H "X-Title: Rai / ask-model" \
  -d "$PAYLOAD")

ERR=$(jq -r '.error.message // empty' <<<"$RESPONSE")
if [[ -n "$ERR" ]]; then
  echo "error from OpenRouter: $ERR" >&2
  jq -n \
    --arg ts "$STARTED_AT" \
    --arg model "$MODEL" \
    --arg task "$TASK" \
    --arg err "$ERR" \
    '{ts:$ts, model:$model, task:$task, error:$err}' >> "$LOG_FILE"
  exit 4
fi

CONTENT=$(jq -r '.choices[0].message.content // ""' <<<"$RESPONSE")
PROMPT_TOKENS=$(jq -r '.usage.prompt_tokens // 0' <<<"$RESPONSE")
COMPLETION_TOKENS=$(jq -r '.usage.completion_tokens // 0' <<<"$RESPONSE")
TOTAL_TOKENS=$(jq -r '.usage.total_tokens // 0' <<<"$RESPONSE")
COST=$(jq -r '.usage.cost // 0' <<<"$RESPONSE")
GEN_ID=$(jq -r '.id // ""' <<<"$RESPONSE")

jq -n \
  --arg ts "$STARTED_AT" \
  --arg model "$MODEL" \
  --arg alias "$ALIAS" \
  --arg task "$TASK" \
  --arg gen_id "$GEN_ID" \
  --argjson prompt_tokens "$PROMPT_TOKENS" \
  --argjson completion_tokens "$COMPLETION_TOKENS" \
  --argjson total_tokens "$TOTAL_TOKENS" \
  --arg cost "$COST" \
  --arg prompt_excerpt "$(printf '%s' "$PROMPT" | head -c 400)" \
  --arg response_excerpt "$(printf '%s' "$CONTENT" | head -c 400)" \
  '{ts:$ts, model:$model, alias:$alias, task:$task, gen_id:$gen_id, prompt_tokens:$prompt_tokens, completion_tokens:$completion_tokens, total_tokens:$total_tokens, cost:($cost|tonumber? // 0), prompt_excerpt:$prompt_excerpt, response_excerpt:$response_excerpt}' \
  >> "$LOG_FILE"

printf '%s\n' "$CONTENT"
