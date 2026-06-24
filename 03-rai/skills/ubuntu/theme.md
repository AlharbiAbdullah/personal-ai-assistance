---
name: theme
description: Manages Linux theming end-to-end. Audits themes against Omarchy as the golden standard, adds/removes themes, verifies app adapters (WezTerm, Hyprland border, VS Code, Cursor, Starship, swaybg wallpaper), manages wallpapers, inspects keybindings, debugs why an app did not adapt. Invoked via /ubuntu router. Handles any theme/wallpaper/appearance-related question on the Linux machine.
allowed-tools: Bash, Read, Grep, Glob, Edit, Write, WebFetch
---

# /ubuntu-theme - Linux Theme System Manager

Omarchy is the **golden standard**. Every theme on this machine must match its
Omarchy source 1:1. No made-up colors.

This is the Linux port of `/mac-theme`. Same `theme.lua` format, same themes,
same canonical palettes. **Palettes and supported-theme list live in the Mac
skill's references — do NOT duplicate them here:**

- `../mac/references/omarchy-palettes.toml` — canonical palettes + upstream sources
- `../mac/references/app-mappings.toml` — VS Code / Cursor / border mappings

## Architecture

```
~/.config/themes/<name>/
    theme.lua          declarative palette + app mapping (same shape as Mac)
    wallpapers/        PNG/JPG pack for this theme
~/.config/themes/current.lua -> <name>/theme.lua

~/.local/bin/theme     switcher (bash). subcommands: list, <name>, reload, cycle, pick, wallpaper
~/.config/hypr/hyprland.conf   binds SUPER+CTRL+T → theme cycle, SUPER+CTRL+W → theme wallpaper next
~/.cache/theme/        last-active wallpaper per theme
```

Apps affected: **Ghostty** (regenerates `~/.config/ghostty/theme.conf`, live-reload
via `SIGUSR2`), **tmux** (regenerates `~/.config/tmux/theme.conf`, sourced by
`~/.tmux.conf`, live `tmux source-file` on the running server — rounded-pill
status line using TWO palette colors: bar is transparent (bg=`background`), the
**accent** (`border` last-6) marks the active-window pill + pane border, the
theme's **blue** (`ansi[4]`) frames the session + clock pills; pill caps are
Nerd-Font rounded glyphs U+E0B6/U+E0B4),
**Hyprland border** (`hyprctl keyword general:col.active_border`),
**VS Code** (`~/.config/Code/User/settings.json` → `workbench.colorTheme`; auto-installs
the theme's `vscode_ext`), **Chrome** (`BrowserThemeColor` managed policy at
`/etc/opt/chrome/policies/managed/color.json` + live `--refresh-platform-policy` —
Omarchy's mechanism; tints the **frame only**, toolbar stays a neutral surface by
design), **Starship** (`~/.config/starship.toml` palette), **waybar** (`theme-colors.css` +
`SIGUSR2`), **OS color-scheme** (`gsettings org.gnome.desktop.interface
color-scheme` + `gtk-theme`, driven by the theme's `macos` dark/light marker —
sets the freedesktop portal `org.freedesktop.appearance color-scheme`, so
Chrome/Firefox/Electron and "use device theme" sites like YouTube/Google and
GTK4/libadwaita apps follow), **wallpaper** (swaybg restart), **HUD** (notify-send → mako).

**Obsidian is intentionally EXCLUDED** (user choice, 2026-06-10): it stays pinned
to the "Obsidian Nord" community theme (`cssTheme` in each vault's
`appearance.json`). The old `update_obsidian_theme` adapter (generated
`theme-palette.css` snippet per vault) was removed from the switcher. Do not
re-wire it without asking.

**Chrome one-time setup** (so per-switch policy writes need no sudo — same as Omarchy):
`sudo mkdir -p /etc/opt/chrome/policies/managed && sudo chmod a+rw /etc/opt/chrome/policies/managed`.
Note: `BrowserColorScheme` is NOT a real stock-Chrome policy (only Omarchy's patched
chromium honors it); `BrowserThemeColor` is the only key that works.

**theme.lua fields**: `vscode` = exact `workbench.colorTheme` label; `vscode_ext` =
marketplace extension id (auto-installed if missing). The old `cursor` field is gone.

Note: `theme.lua` keeps the `macos = "dark|light"` field for cross-machine
parity with the Mac. On Linux it is only a light/dark marker — nothing reads it
yet. Do not remove it; the same theme files should work on both machines.

## Subcommands

Invoke with `/ubuntu-theme <subcommand> [args]`.

---

### 1. audit — Omarchy parity check

Purpose: find colors that drifted from the Omarchy source of truth.

Usage: `/ubuntu-theme audit [<theme>]`. No arg = audit all local themes.

Steps:
1. Read `../mac/references/omarchy-palettes.toml`.
2. For each local theme at `~/.config/themes/<name>/theme.lua`, parse background, foreground, cursor_bg, selection_bg, ansi[], brights[].
3. Compare to the canonical palette. Normalize hex to lowercase.
4. Report per-theme: PASS (1:1), DRIFT (any mismatch), MISSING (not in Omarchy source list).
5. For DRIFT, list every key that differs with `key: local_hex != omarchy_hex`.

Pass: all themes PASS. Fix: `/ubuntu-theme sync <theme>`.

---

### 2. add — install theme from Omarchy

Usage: `/ubuntu-theme add <name>`.

Steps:
1. If `<name>` not in the supported list (see palettes file), stop and list valid names.
2. If `~/.config/themes/<name>/` exists, ask to overwrite or abort.
3. Read palette + app mapping from the Mac references.
4. Write `~/.config/themes/<name>/theme.lua` with the exact same shape the Mac skill documents (name, border, macos, vscode, cursor, colors{}).
5. Create `~/.config/themes/<name>/wallpapers/` (empty). Prompt user to `/ubuntu-theme wallpapers sync <name>`.
6. Run `/ubuntu-theme audit <name>` to confirm 1:1.

---

### 3. adapters — per-app health check

Purpose: after switching themes, verify every app actually updated.

Usage: `/ubuntu-theme adapters [<theme>]`. Defaults to current.

| App | Where to read actual | Expected |
|-----|----------------------|----------|
| Ghostty | `cat ~/.config/ghostty/theme.conf` | palette matches `current.lua` |
| tmux | `tmux show -gv window-status-current-format` (running server) / `cat ~/.config/tmux/theme.conf` | bar `bg`=`background` (transparent); active-window pill `bg`=accent; session/clock pill `bg`=`ansi[4]`; `pane-active-border-style fg`=accent |
| Hyprland border | `hyprctl getoption general:col.active_border` | `theme.border` |
| VS Code | `~/.config/Code/User/settings.json` → `workbench.colorTheme` | `theme.vscode` (must be an installed label) |
| Chrome | `cat /etc/opt/chrome/policies/managed/color.json` | `BrowserThemeColor` = `theme.background` |
| OS color-scheme | `gsettings get org.gnome.desktop.interface color-scheme` | `prefer-dark` if `theme.macos==dark` else `prefer-light` |
| Portal (Chrome/YouTube source) | `gdbus call --session --dest org.freedesktop.portal.Desktop --object-path /org/freedesktop/portal/desktop --method org.freedesktop.portal.Settings.Read org.freedesktop.appearance color-scheme` | `1` (dark) / `2` (light) |
| Obsidian (excluded) | `<vault>/.obsidian/appearance.json` → `cssTheme` | `"Obsidian Nord"` (pinned, switcher never touches it); no `theme-palette` snippet |
| Starship | grep `^palette` in `~/.config/starship.toml` | matches theme name |
| Wallpaper | `pgrep -a swaybg` → `-i <path>` | a file under `<theme>/wallpapers/` |

Emit a table: `app | expected | actual | PASS/FAIL`. Any FAIL → suggest `/ubuntu-theme debug <app>`.

---

### 4. coverage — installed-app theming audit

Purpose: find theme-able apps on this machine that the switcher does not touch.

Steps:
1. Known theme-able apps: WezTerm, Alacritty, Kitty, foot, tmux, VS Code, Cursor, Zed, Neovim, GNOME terminal, waybar, mako, fuzzel, hyprlock, GTK apps (gsettings color-scheme), Obsidian, Chrome.
2. Check installs: `which <bin>`, `apt list --installed 2>/dev/null | grep`, `snap list`.
3. For each installed theme-able app, check if `~/.local/bin/theme` references it (`grep -E '<app>' ~/.local/bin/theme`).
4. Report table: `app | installed | wired_in_switcher | notes`.

Known gaps worth flagging: **mako**, **fuzzel**, **hyprlock**
are not yet wired into the switcher. Each gap is a candidate edit to `~/.local/bin/theme`.
(**waybar**, **GTK/OS dark-light** via `color-scheme`, and **tmux** are now wired in.)

**Obsidian is NOT a gap** — it was deliberately removed from the switcher
(2026-06-10) and pinned to the "Obsidian Nord" theme. Do not report it as a
candidate or re-wire it.

**fastfetch** is NOT a switcher gap — it is intentionally palette-driven, not
regenerated per theme. Config: `~/.config/fastfetch/config.jsonc` (Omarchy's
layout — boxed Hardware/Software/Age sections, tree connectors, nerd icons),
adapted for Ubuntu. Every color is an ANSI name (`green`/`blue`/`magenta` keys,
bright-black `[90m` borders) or named logo color — never hardcoded hex — so
it resolves through Ghostty's themed `palette` (`~/.config/ghostty/theme.conf`,
which the switcher regenerates) and follows the active theme automatically with
zero switcher changes. The Software box's theme line reads the live theme name
from `~/.config/themes/current.lua` and prints a palette-dot strip. Do not wire
it into `~/.local/bin/theme`; there is nothing per-theme to regenerate.

---

### 5. keys — keybinding inspector

Purpose: prove which config owns `SUPER+CTRL+T` and `SUPER+CTRL+W`, flag conflicts.

Steps:
1. Grep each possible owner:
   - `~/.config/hypr/hyprland.conf` for `SUPER CTRL, T` and `SUPER CTRL, W`
   - `hyprctl binds` for the live state (config may not be reloaded)
2. Emit table: `binding | owner | action | status`.
3. Status PASS if exactly one owner. WARN if none. FAIL if multiple.

Expected baseline: `hyprland.conf` owns both, pointing at `~/.local/bin/theme cycle`
and `theme wallpaper next`. If the live `hyprctl binds` disagrees with the file,
suggest `hyprctl reload`.

---

### 6. wallpapers — pack management

Usage:
- `/ubuntu-theme wallpapers list [<theme>]`
- `/ubuntu-theme wallpapers check` — cross-theme md5 dedup, missing folders
- `/ubuntu-theme wallpapers sync <theme>` — download pack from the Omarchy `backgrounds/` dir

Sync uses the same theme→repo mapping documented in `../mac/theme.md` (§6).
Download to `~/.config/themes/<name>/wallpapers/`, keep upstream filenames.

---

### 7. debug — inspect why an app did not adapt

Usage: `/ubuntu-theme debug <app>` or `debug all`.

Per-app steps:
- **wezterm**: `readlink ~/.config/themes/current.lua`; show first 20 lines of target. If colors stale, `touch ~/.wezterm.lua` (the switcher's nudge) and check WezTerm's `automatically_reload_config`.
- **border**: `hyprctl getoption general:col.active_border`. If wrong, the keyword call failed — run `~/.local/bin/theme reload` and check Hyprland is running (`$HYPRLAND_INSTANCE_SIGNATURE`).
- **vscode**: read settings.json, show the `workbench.colorTheme` line. The value MUST be an installed contributed theme label (`code --list-extensions`; check each ext's `package.json` → `contributes.themes[].label`) or VS Code silently falls back to its default. The switcher auto-installs `theme.vscode_ext` if missing.
- **tmux**: `cat ~/.config/tmux/theme.conf` (generated, sourced by `~/.tmux.conf` via a guarded `if-shell`). On a running server compare `tmux show -gv status-style` against the file — if it lags, the switcher's `tmux source-file` didn't fire (no server was up at switch time; it self-heals on the next `theme` run or tmux start). `tmux source-file` only hits the default socket — sessions on a non-default socket won't live-update until restarted.
- **chrome**: `cat /etc/opt/chrome/policies/managed/color.json` (needs the one-time `chmod a+rw` setup). If unchanged in a running Chrome, the `--refresh-platform-policy` nudge didn't fire — confirm `pgrep -x chrome` and the `google-chrome-stable` binary. Verify live state at `chrome://policy` (BrowserThemeColor under Platform policies). Frame-only by design: it tints the frame; the toolbar stays neutral (near-white in light mode). An exact toolbar color would need a full generated Chrome theme (not built — chosen tradeoff to keep switching live/no-restart). Stock Chrome has no policy to force light/dark, but the switcher now sets the OS `color-scheme` (see the **color-scheme** debug entry below) so Chrome's web content (`prefers-color-scheme`) follows the theme — YouTube/Google must be set to "use device theme" for this to show.
- **color-scheme**: `gsettings get org.gnome.desktop.interface color-scheme` (expect `prefer-dark`/`prefer-light` per the theme's `macos` marker). The value Chrome/Firefox actually read is the portal's: `gdbus call --session --dest org.freedesktop.portal.Desktop --object-path /org/freedesktop/portal/desktop --method org.freedesktop.portal.Settings.Read org.freedesktop.appearance color-scheme` → `1`=dark, `2`=light, `0`=no-preference (sites fall back to light). If the portal stays `0` after a switch, confirm `xdg-desktop-portal-gtk` or `-gnome` is running (`pgrep -af xdg-desktop-portal`). If a site ignores it, its appearance is pinned (not "use device theme"). gsettings persists in dconf, so it survives reboot without a re-apply.
- **obsidian**: intentionally excluded from the switcher — verify `cssTheme` is `"Obsidian Nord"` in `<vault>/.obsidian/appearance.json` and that no `theme-palette` entry/snippet lingers. If colors look wrong, the fix is in Obsidian itself, not the switcher.
- **starship**: `sed -n '1,60p' ~/.config/starship.toml`, highlight `palette` + `[palettes.<name>]`. A missing `[palettes.<name>]` section means the prompt silently falls back.
- **wallpaper**: `pgrep -a swaybg`. If dead, `~/.local/bin/theme wallpaper next` respawns it. Check the cached path in `~/.cache/theme/<name>.wallpaper` still exists.
- **hud**: `pgrep -x mako` — notify-send goes nowhere if mako is down.

Emit findings with absolute paths.

---

### 8. remove — delete a theme

Usage: `/ubuntu-theme remove <name>`.

Steps:
1. Refuse if `<name>` is current. Suggest switching first.
2. Confirm with user before deleting.
3. Delete `~/.config/themes/<name>/` and `~/.cache/theme/<name>.wallpaper`.
4. Do not touch `~/.local/bin/theme` (it globs the themes dir).

---

### 9. list — overview

Usage: `/ubuntu-theme list` or no args.

Columns: name, mode (dark/light), current (★), omarchy_match (✓/△/✗), wallpaper_count.
At the bottom, print the current theme's palette as a color strip.

---

### 10. sync — overwrite from canonical (audit fix)

`/ubuntu-theme sync <theme>` — rewrite `<theme>/theme.lua` colors from
`../mac/references/omarchy-palettes.toml`, leaving app-mapping fields intact.
Only after user confirms.

---

## Fix suggestions

| Symptom | Fix |
|---------|-----|
| Audit shows DRIFT | `/ubuntu-theme sync <theme>` then `adapters` to re-apply |
| Border didn't change | `hyprctl reload` then `theme reload`; verify `hyprctl getoption general:col.active_border` |
| WezTerm stale | `touch ~/.wezterm.lua`; confirm config auto-reload is on |
| VS Code didn't update | Theme extension not installed — check Extensions for the name in `app-mappings.toml` |
| Wallpaper black screen | swaybg died; `theme wallpaper next`. Cached path may point at a deleted file |
| `SUPER+CTRL+T` does nothing | `/ubuntu-theme keys`; if config and live binds differ, `hyprctl reload` |
| No HUD on switch | mako not running; `pgrep -x mako`, restart via `mako &` or relog |

## Rules

- **Never make up colors.** Every hex comes from `../mac/references/omarchy-palettes.toml` or a freshly fetched Omarchy source.
- **Shared references live under `/mac`.** One source of truth for both machines. Palette updates go through `/mac-theme refresh-palettes`.
- **Write minimal diffs.** Change only the lines that must change.
- **Keep `~/.local/bin/theme` as the only switcher.** The skill inspects, validates, and edits configs; the bash script applies them.
- **Source of truth for local themes is `~/.config/themes/`.**
- **Keep `theme.lua` cross-machine compatible** — same fields as the Mac, including `macos`.

## References

- `../mac/references/omarchy-palettes.toml` — canonical palettes (shared)
- `../mac/references/app-mappings.toml` — per-theme app mappings (shared)
- `~/.local/bin/theme` — switcher source
- `~/.config/hypr/hyprland.conf` — THEME + WALLPAPER bind section
