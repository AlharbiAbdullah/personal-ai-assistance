#!/bin/bash
# Omarchy-adaptive statusline for Claude Code
# Reads colors from ~/.config/omarchy/current/theme/colors.toml
# Inspired by ccstatusline powerline layout

input=$(cat)

# --- color loading from omarchy theme ---
COLORS_FILE="$HOME/.config/omarchy/current/theme/colors.toml"
LIGHT_MODE=0
[ -f "$HOME/.config/omarchy/current/theme/light.mode" ] && LIGHT_MODE=1

get_color() {
  local key="$1" default="$2"
  if [ -f "$COLORS_FILE" ]; then
    local val
    val=$(grep -m1 "^${key} " "$COLORS_FILE" | sed 's/.*= *"\(.*\)"/\1/')
    [ -n "$val" ] && echo "$val" && return
  fi
  echo "$default"
}

hex_to_rgb() {
  local hex="${1#\#}"
  printf '%d;%d;%d' "0x${hex:0:2}" "0x${hex:2:2}" "0x${hex:4:2}"
}

fg() { printf '\033[38;2;%sm' "$(hex_to_rgb "$1")"; }
bg() { printf '\033[48;2;%sm' "$(hex_to_rgb "$1")"; }
rst() { printf '\033[0m'; }

# load theme palette
C_ACCENT=$(get_color "accent" "#89b4fa")
C_FG=$(get_color "foreground" "#cdd6f4")
C_BG=$(get_color "background" "#1e1e2e")
C_GREEN=$(get_color "color2" "#a6e3a1")
C_YELLOW=$(get_color "color3" "#f9e2af")
C_BLUE=$(get_color "color4" "#89b4fa")
C_MAGENTA=$(get_color "color5" "#f5c2e7")
C_CYAN=$(get_color "color6" "#94e2d5")
C_RED=$(get_color "color1" "#f38ba8")
C_DIM=$(get_color "color8" "#585b70")
C_CURSOR=$(get_color "cursor" "#f5e0dc")

# --- extract data via jq ---
if ! command -v jq >/dev/null 2>&1; then
  echo "jq required"
  exit 1
fi

cwd=$(echo "$input" | jq -r '.workspace.current_dir // .cwd // "?"' 2>/dev/null)
cwd=$(echo "$cwd" | sed "s|^${HOME}|~|")
model=$(echo "$input" | jq -r '.model.display_name // "Claude"' 2>/dev/null)
version=$(echo "$input" | jq -r '.version // ""' 2>/dev/null)

# context window
ctx_size=$(echo "$input" | jq -r \
  '.context_window.context_window_size // 200000' 2>/dev/null)
ctx_used=$(echo "$input" | jq -r \
  '(.context_window.current_usage.input_tokens // 0)
   + (.context_window.current_usage.cache_creation_input_tokens // 0)
   + (.context_window.current_usage.cache_read_input_tokens // 0)' \
  2>/dev/null)

ctx_pct=0
if [ "$ctx_used" -gt 0 ] 2>/dev/null; then
  ctx_pct=$(( ctx_used * 100 / ctx_size ))
fi
ctx_remain=$(( 100 - ctx_pct ))
(( ctx_remain < 0 )) && ctx_remain=0
(( ctx_remain > 100 )) && ctx_remain=100

# git
git_branch=""
git_dirty=""
if git rev-parse --git-dir >/dev/null 2>&1; then
  git_branch=$(git branch --show-current 2>/dev/null \
    || git rev-parse --short HEAD 2>/dev/null)
  if [ -n "$(git status --porcelain 2>/dev/null | head -1)" ]; then
    git_dirty="*"
  fi
fi

# theme name
theme_name=""
if [ -f "$HOME/.config/omarchy/current/theme.name" ]; then
  theme_name=$(cat "$HOME/.config/omarchy/current/theme.name")
fi

# --- progress bar ---
bar() {
  local pct="$1" width="${2:-15}" filled empty
  (( pct < 0 )) && pct=0; (( pct > 100 )) && pct=100
  filled=$(( pct * width / 100 ))
  empty=$(( width - filled ))
  local bar_str=""
  for ((i=0; i<filled; i++)); do bar_str+="$3"; done
  for ((i=0; i<empty; i++)); do bar_str+="$4"; done
  echo "$bar_str"
}

# context color: green > yellow > red based on remaining
if [ "$ctx_remain" -le 20 ]; then
  CTX_COLOR="$C_RED"
elif [ "$ctx_remain" -le 40 ]; then
  CTX_COLOR="$C_YELLOW"
else
  CTX_COLOR="$C_GREEN"
fi

# --- powerline separator ---
SEP=""

# --- render ---

# Line 1: dir | git | model | version
printf '%s%s %s %s' "$(bg "$C_ACCENT")" "$(fg "$C_BG")" "$cwd" "$(rst)"
printf '%s%s' "$(fg "$C_ACCENT")" "$SEP"

if [ -n "$git_branch" ]; then
  printf ' %s%s%s%s ' "$(fg "$C_GREEN")" "$git_branch" "$git_dirty" "$(rst)"
fi

printf '%s%s%s' "$(fg "$C_MAGENTA")" "$model" "$(rst)"

if [ -n "$version" ] && [ "$version" != "null" ]; then
  printf ' %sv%s%s' "$(fg "$C_DIM")" "$version" "$(rst)"
fi

# Line 2: context bar | theme
printf '\n'
ctx_bar=$(bar "$ctx_remain" 15 "+" "-")
printf ' %sctx %s%% %s[%s]%s' \
  "$(fg "$CTX_COLOR")" "$ctx_remain" \
  "$(fg "$C_DIM")" "$(fg "$CTX_COLOR")${ctx_bar}$(fg "$C_DIM")" \
  "$(rst)"

if [ -n "$theme_name" ]; then
  printf '  %s%s%s' "$(fg "$C_CYAN")" "$theme_name" "$(rst)"
fi

printf '\n'
