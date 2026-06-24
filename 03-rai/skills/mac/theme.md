---
name: theme
description: Manages macOS theming end-to-end. Audits themes against Omarchy as the golden standard, adds/removes themes, verifies app adapters (WezTerm, VS Code, Cursor, Starship, JankyBorders, macOS appearance), manages wallpapers, inspects keybindings, debugs why an app did not adapt, and pairs light/dark variants. Invoked via /mac router. Handles any theme/wallpaper/appearance-related question on the Mac.
allowed-tools: Bash, Read, Grep, Glob, Edit, Write, WebFetch
---

# /mac-theme - macOS Theme System Manager

Omarchy is the **golden standard**. Every theme on this Mac must match its Omarchy source 1:1. No made-up colors.

## Supported Themes

| Theme | Mode | Source |
|-------|------|--------|
| catppuccin | dark | basecamp/omarchy@dev `themes/catppuccin/colors.toml` |
| gruvbox | dark | basecamp/omarchy@dev `themes/gruvbox/colors.toml` |
| nord | dark | basecamp/omarchy@dev `themes/nord/colors.toml` |
| tokyo-night | dark | basecamp/omarchy@dev `themes/tokyo-night/colors.toml` |
| miasma | dark | OldJobobo/omarchy-miasma-theme@master `colors.toml` |
| cobalt2 | dark | hoblin/omarchy-cobalt2-theme@main `colors.toml` |
| gruvbox-light | light | Kushal0924/omarchy-gruvbox-light-theme@main `colors.toml` |
| everforest | dark | basecamp/omarchy@master `themes/everforest/colors.toml` |
| kanagawa | dark | basecamp/omarchy@master `themes/kanagawa/colors.toml` |
| ristretto | dark | basecamp/omarchy@master `themes/ristretto/colors.toml` |
| rose-pine | dark | rose-pine/alacritty@main `dist/rose-pine.toml` (Main variant) |
| melange | dark | savq/melange-nvim@master `lua/melange/palettes/dark.lua` |
| bamboo | dark | ribru17/bamboo.nvim@master `lua/bamboo/palette.lua` (multiplex variant) |
| kanagawa-dragon | dark | rebelot/kanagawa.nvim@master `lua/kanagawa/colors.lua` (dragon palette) |
| nightfox | dark | EdenEast/nightfox.nvim@main `extra/nightfox/wezterm.toml` |
| duskfox | dark | EdenEast/nightfox.nvim@main `extra/duskfox/wezterm.toml` |
| nordfox | dark | EdenEast/nightfox.nvim@main `extra/nordfox/wezterm.toml` |

Canonical palettes baked in at `references/omarchy-palettes.toml`. Per-theme app settings at `references/app-mappings.toml`.

## Architecture

```
~/.config/themes/<name>/
    theme.lua          declarative palette + app mapping
    wallpapers/        PNG/JPG pack for this theme
~/.config/themes/current.lua -> <name>/theme.lua

~/.local/bin/theme     switcher (bash). subcommands: list, <name>, reload, regen, cycle, pick, wallpaper
~/.aerospace.toml      binds cmd-ctrl-t → theme cycle, cmd-ctrl-w → theme wallpaper next
~/.cache/theme/        last-active wallpaper per theme
~/.hammerspoon/init.lua  HUD alerts on theme change

~/.config/opencode/themes/<name>.json            generated TUI theme (1 per system theme)
~/.config/opencode/tui-plugins/theme-sync.ts     TUI plugin: live-reloads a RUNNING opencode
```

Apps affected: **WezTerm** (reads `current.lua`), **OpenCode** (generated custom TUI theme + live-reload plugin), **JankyBorders** (restarted with accent), **VS Code** + **Cursor** (settings.json `workbench.colorTheme`), **Starship** (`~/.config/starship.toml` palette), **macOS** (`AppleInterfaceStyle`), **wallpaper** (NSWorkspace helper).

OpenCode adaptation, two layers: (1) on **launch**, opencode reads `tui.json`/`kv.json` (both written by the switcher) so a fresh session already matches; (2) the **`theme-sync` TUI plugin** (registered in `tui.json` `plugin[]`) polls `current.lua` and calls the TUI's `api.theme.set()` so an **already-open** session repaints live — opencode has no built-in live theme reload, and its config watcher reloads agents/skills but not the theme. `--pure` skips the plugin (launch-time still works). The plugin is Mac-only (hardcoded `~` paths); the Ubuntu switcher would need the analogous wiring.

OpenCode theme generation (`update_opencode_theme` in the switcher): the Omarchy signature colors (`background`, `foreground`, the 16 ANSI accents) are written EXACT. But OpenCode also needs neutral chrome elevations the 16-color palette doesn't define (`backgroundPanel`/`backgroundElement`/`border`/`borderSubtle`/`textMuted`) — these are derived by blending `background → foreground` (dark themes step lighter, light themes step darker). The loud selection/accent color is reserved for `borderActive`/`primary`/markdown headings only; it must NEVER be a fill (mapping `backgroundElement = selection_bg` is what made the input box render as a solid garish block — e.g. gruvbox `selection_bg = #d65d0e` orange). After editing the generator, run **`theme regen`** to rebuild all 10 JSONs, then **restart opencode** (a running TUI loaded the old JSONs at startup; the live plugin re-applies on theme *change*, not on file content change).

## Subcommands

Invoke with `/mac-theme <subcommand> [args]`. Each subcommand below lists its purpose, usage, steps, and pass criteria.

---

### 1. audit — Omarchy parity check

Purpose: Find colors that drifted from the Omarchy source of truth. This is the reason this skill exists.

Usage: `/mac-theme audit [<theme>]`. No arg = audit all local themes.

Steps:
1. Read `references/omarchy-palettes.toml`.
2. For each local theme at `~/.config/themes/<name>/theme.lua`, parse background, foreground, cursor_bg, selection_bg, ansi[], brights[].
3. Compare to the canonical palette. Normalize hex to lowercase for comparison.
4. Report per-theme: PASS (1:1), DRIFT (any mismatch), MISSING (theme not in Omarchy source list).
5. For DRIFT, list every key that differs with `key: local_hex != omarchy_hex`.

Pass: all themes PASS.
Fix: `/mac-theme sync <theme>` rewrites `theme.lua` from canonical.

---

### 2. add — install theme from Omarchy

Purpose: Add a theme from the supported list with colors baked from the canonical source.

Usage: `/mac-theme add <name>`.

Steps:
1. If `<name>` not in supported list, stop and list valid names.
2. If `~/.config/themes/<name>/` already exists, ask to overwrite or abort.
3. Read palette from `references/omarchy-palettes.toml` and app mapping from `references/app-mappings.toml`.
4. Write `~/.config/themes/<name>/theme.lua` with this exact shape:
   ```lua
   return {
     name = "<name>",
     border = "<border hex>",           -- from app-mappings
     macos = "<dark|light>",            -- from palette.mode
     vscode = "<vs code theme>",
     cursor = "<cursor theme>",
     colors = {
       background = "<bg>",
       foreground = "<fg>",
       cursor_bg = "<cursor>",
       cursor_fg = "<bg>",
       selection_bg = "<sel_bg>",
       selection_fg = "<sel_fg>",
       ansi = { 8 normal hexes },
       brights = { 8 bright hexes },
     },
   }
   ```
5. Create `~/.config/themes/<name>/wallpapers/` (empty). Prompt user to `/mac-theme wallpapers sync <name>` to populate.
6. Run `/mac-theme audit <name>` to confirm 1:1.

Pass: audit returns PASS.

---

### 3. adapters — per-app health check

Purpose: After switching themes, verify every app actually updated.

Usage: `/mac-theme adapters [<theme>]`. Defaults to current.

Steps (for each app, compare expected vs actual):

| App | Where to read actual | Expected |
|-----|----------------------|----------|
| macOS appearance | `defaults read -g AppleInterfaceStyle` (empty = light) | `theme.macos` |
| VS Code | `~/Library/Application Support/Code/User/settings.json` → `workbench.colorTheme` | `theme.vscode` |
| Cursor | `~/Library/Application Support/Cursor/User/settings.json` → `workbench.colorTheme` | `theme.cursor` |
| Starship | grep `^palette` in `~/.config/starship.toml` | matches theme name |
| OpenCode | `~/.config/opencode/tui.json` + `~/.config/opencode/themes/<theme>.json` | `theme` matches theme name + custom JSON exists + `tui.json` `plugin[]` registers `tui-plugins/theme-sync.ts` (live reload) |
| JankyBorders | `pgrep -fl borders` and check launched with `active_color=<border>` | `theme.border` |
| WezTerm | `readlink ~/.config/themes/current.lua` | `<name>/theme.lua` |

Emit a table: `app | expected | actual | PASS/FAIL`. Any FAIL becomes a suggestion to run `/mac-theme debug <app>`.

---

### 4. coverage — installed-app theming audit

Purpose: Find theme-able apps on the Mac that the switcher does not touch.

Steps:
1. Known theme-able apps list (static): WezTerm, Ghostty, iTerm2, Alacritty, Kitty, Terminal.app, VS Code, Cursor, Zed, Xcode, Sublime Text, Neovim, Notion, Slack, Discord, Firefox, Arc, Raycast, Rectangle, JankyBorders.
2. Check `/Applications` and `~/Applications` with `mdfind`/`ls` or `brew list --cask` and `brew list`.
3. For each installed theme-able app, check if `~/.local/bin/theme` references it (`grep -E '<app>' ~/.local/bin/theme`).
4. Report table: `app | installed | wired_in_switcher | theme_file_for_current_theme`.

Gaps become candidates for wiring into `~/.local/bin/theme`.

---

### 5. keys — keybinding inspector

Purpose: Prove which config owns `cmd-ctrl-t` and `cmd-ctrl-w` and flag conflicts.

Steps:
1. Grep each possible owner:
   - `~/.aerospace.toml` for `cmd-ctrl-t` and `cmd-ctrl-w`
   - `~/.hammerspoon/init.lua` for `hs.hotkey.bind`
   - `~/.config/karabiner/karabiner.json` for matching `key_code` + `modifiers`
   - `~/Library/Application Support/com.raycast.macos/` (hotkeys plist) — best-effort via `defaults read`
   - `~/.config/skhd/skhdrc`
2. Emit table: `binding | owner | action | status`.
3. Status PASS if exactly one owner. WARN if none. FAIL if multiple.

Expected baseline: `aerospace.toml` owns both `cmd-ctrl-t` and `cmd-ctrl-w`, pointing at `~/.local/bin/theme cycle` and `wallpaper next` respectively. If something else owns them, that is a conflict — flag it.

---

### 6. wallpapers — pack management

Purpose: Manage wallpaper folders: list, dedup, sync from Omarchy.

Usage:
- `/mac-theme wallpapers list [<theme>]`
- `/mac-theme wallpapers check` — cross-theme md5 dedup, naming convention, missing folders
- `/mac-theme wallpapers sync <theme>` — download pack from Omarchy `backgrounds/` dir

Sync steps for `sync`:
1. Map theme to repo (same mapping as audit):
   - catppuccin/gruvbox/nord/tokyo-night → `basecamp/omarchy@dev/themes/<name>/backgrounds/`
   - miasma → `OldJobobo/omarchy-miasma-theme@master/backgrounds/`
   - cobalt2 → `hoblin/omarchy-cobalt2-theme@main/backgrounds/`
   - gruvbox-light → `Kushal0924/omarchy-gruvbox-light-theme@main/backgrounds/`
   - everforest → `basecamp/omarchy@master/themes/everforest/backgrounds/` + `OldJobobo/omarchy-everforest-bg-addon@master/` (supplemental)
   - kanagawa → `basecamp/omarchy@master/themes/kanagawa/backgrounds/` + `bjarneo/omarchy-kanagawa-dragon-theme@main/backgrounds/` (supplemental) + `philikarus/Kanagawa-wallpapers@main/wallpapers/landscape/` (supplemental)
   - ristretto → `basecamp/omarchy@master/themes/ristretto/backgrounds/`
2. `curl` the GitHub API `/contents/<path>`, download each file to `~/.config/themes/<name>/wallpapers/`.
3. Keep the upstream filenames. Do not rename.

Check steps:
1. For each theme folder, list wallpapers and `md5sum` each.
2. Report duplicates across themes.
3. Flag themes with zero wallpapers.

---

### 7. pair — light/dark twin binding

Purpose: Bind a dark theme to its light sibling so macOS appearance changes can flip between them.

Usage: `/mac-theme pair <dark> <light>` (e.g. `gruvbox gruvbox-light`).

Steps:
1. Validate both themes exist.
2. Validate `<dark>.macos == "dark"` and `<light>.macos == "light"`.
3. Append `light_variant = "<light>"` to `<dark>/theme.lua` (top-level field).
4. Append `dark_variant = "<dark>"` to `<light>/theme.lua`.
5. Print a one-liner launchd plist the user can install at `~/Library/LaunchAgents/com.local.theme-auto.plist` that watches `AppleInterfaceStyle` and runs the paired theme. Do NOT install without user approval.

---

### 8. debug — inspect why an app did not adapt

Purpose: Deep-dive a single app's actual state vs expected.

Usage: `/mac-theme debug <app>` or `/mac-theme debug all`.

Per-app steps:
- **vscode / cursor**: read settings.json, find `workbench.colorTheme`, show the line with line number. If absent, show top 5 lines around where it would be inserted.
- **starship**: `sed -n '1,60p' ~/.config/starship.toml`, highlight palette + [palettes.<name>] section.
- **opencode**: read `~/.config/opencode/tui.json`, `~/.local/state/opencode/kv.json`, and `~/.config/opencode/themes/<current>.json`; verify all point at the current theme.
- **borders**: `ps -o pid,args -p $(pgrep -f borders)` — show what args borders was started with.
- **wezterm**: `readlink ~/.config/themes/current.lua`; then show first 20 lines of that file.
- **macos**: `defaults read -g AppleInterfaceStyle 2>/dev/null || echo "light"`.
- **wallpaper**: `osascript -e 'tell application "System Events" to get picture of every desktop'`.

Emit findings with absolute paths so the user can jump.

---

### 9. remove — delete a theme

Usage: `/mac-theme remove <name>`.

Steps:
1. Refuse if `<name>` is the current theme. Suggest switching first.
2. Confirm with user before deleting.
3. Delete `~/.config/themes/<name>/` (including wallpapers).
4. Delete `~/.cache/theme/<name>.wallpaper` if exists.
5. Do not touch `~/.local/bin/theme` (it lists themes via directory glob).

---

### 10. list — overview

Usage: `/mac-theme list` or `/mac-theme` with no args.

Output columns:
- name
- mode (dark/light)
- current (★ if active)
- omarchy_match (✓ PASS / △ DRIFT / ✗ UNSUPPORTED)
- wallpaper_count

One line per theme. At the bottom, print the current theme's full palette preview as a color strip.

---

## Sync subcommand (used by audit fix)

`/mac-theme sync <theme>` — overwrite `<theme>/theme.lua` colors from `references/omarchy-palettes.toml`, leaving app-mapping fields intact. Use only after user confirms.

---

### 11. refresh-palettes — fetch upstream palette updates (maintenance)

Purpose: Pull the latest canonical palettes from the upstream Omarchy repos and update `references/omarchy-palettes.toml`.

Usage: `/mac-theme refresh-palettes`

Steps:
1. For each tracked theme, curl the upstream `colors.toml` to a temp file:
   ```bash
   for t in catppuccin gruvbox nord tokyo-night; do
     curl -s "https://raw.githubusercontent.com/basecamp/omarchy/dev/themes/$t/colors.toml" > /tmp/$t.toml
   done
   for t in everforest kanagawa ristretto; do
     curl -s "https://raw.githubusercontent.com/basecamp/omarchy/master/themes/$t/colors.toml" > /tmp/$t.toml
   done
   curl -s "https://raw.githubusercontent.com/OldJobobo/omarchy-miasma-theme/master/colors.toml" > /tmp/miasma.toml
   curl -s "https://raw.githubusercontent.com/hoblin/omarchy-cobalt2-theme/main/colors.toml" > /tmp/cobalt2.toml
   curl -s "https://raw.githubusercontent.com/Kushal0924/omarchy-gruvbox-light-theme/main/colors.toml" > /tmp/gruvbox-light.toml
   ```
2. Diff each fetch against the corresponding section in `references/omarchy-palettes.toml`.
3. Print the diff and ask the user before writing.
4. On confirm, update the file and bump the fetch date in the header comment.

---

## Fix suggestions

| Symptom | Fix |
|---------|-----|
| Audit shows DRIFT | `/mac-theme sync <theme>` then `/mac-theme adapters` to re-apply |
| VS Code didn't update | VS Code theme extension not installed. Check Extensions view for the theme name in `app-mappings.toml`. |
| Borders crashed | `~/.local/bin/theme` pkills then relaunches. If it stays dead, check `/tmp/borders.log`. |
| `cmd-ctrl-t` does nothing | Run `/mac-theme keys`. If aerospace owns it, reload aerospace with `aerospace reload-config`. |
| Wallpaper did not change | macOS caches per-desktop. `killall Dock` forces a refresh. |
| Theme `miasma` VS Code missing | No extension in marketplace. Import the raw JSON from `app-mappings.toml:vscode_source` as a custom color theme. |

## Rules

- **Never make up colors.** Every hex must come from `references/omarchy-palettes.toml` or a freshly fetched Omarchy source.
- **Write minimal diffs.** When editing `theme.lua` or app settings, change only the lines that must change.
- **No auto-install of launchd agents, brew casks, or VS Code extensions.** Always print the exact command and let the user run it.
- **Keep `~/.local/bin/theme` as the only switcher.** Do not duplicate logic in the skill. The skill inspects, validates, and edits configs; the bash script applies them.
- **Source of truth for local themes is `~/.config/themes/`**. Not `.claude/`, not Obsidian, not anywhere else.
- **Light themes must declare `macos = "light"`**. The switcher reads this field to set `AppleInterfaceStyle`.

## References

- `references/omarchy-palettes.toml` — baked canonical palettes for all 7 themes
- `references/app-mappings.toml` — VS Code / Cursor / border mappings per theme
- `~/.local/bin/theme` — switcher source
- `~/.aerospace.toml:104-107` — theme keybindings section

## Refresh palettes from upstream

This is now subcommand 11 above (`/mac-theme refresh-palettes`). The manual section was removed in favor of the formalized subcommand.
