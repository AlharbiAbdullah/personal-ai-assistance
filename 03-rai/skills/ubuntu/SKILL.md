---
name: ubuntu
description: >
  Ubuntu/Linux router. USE WHEN the user wants theme management, Hyprland or
  Wayland desktop config (keybinds, waybar, mako, fuzzel), Linux automation
  (systemd units, udev, cron), hardware diagnostics, dotfiles bootstrap, or
  Linux power-user tips. Routes between theme, hyprland, diagnostics,
  dotfiles-bootstrap, tips.
---

# Ubuntu

Ubuntu/Linux-specific skills for the Hyprland daily driver (Ubuntu 26.04 LTS).
Sibling of `/mac` — same idea, same theme system, Linux-shaped tooling.

## Routing table

| Task | Sub-skill | File to Read |
|------|-----------|--------------|
| Audit / add / remove themes; verify app adapters | theme | `theme.md` |
| Hyprland config: keybinds, animations, window rules, waybar, mako, fuzzel, hypridle/hyprlock; automation via systemd user units / cron / udev | hyprland | `hyprland.md` |
| Hardware diagnostics (thermal, memory, Wi-Fi, disk, USB, journal) | diagnostics | `diagnostics.md` |
| Bootstrap a fresh Ubuntu: apt packages, Hyprland stack, dotfiles | dotfiles-bootstrap | `dotfiles-bootstrap.md` |
| Power-user tips: shell, Wayland clipboard, apt/snap, systemd | tips | `tips.md` |

## How to use

1. Pick the sub-skill by task shape.
2. `Read` the file in this directory.
3. Follow that file's instructions.

## When two could fit

- **theme vs hyprland:** theme is appearance (colors, wallpapers, app adapters); hyprland is behavior (binds, rules, animations, desktop daemons).
- **hyprland vs tips:** hyprland authors new config/automation; tips is a reference catalog of native features.
- **dotfiles-bootstrap vs theme:** bootstrap is full-machine setup; theme is swapping appearance on an already-configured machine.

## Cross-references

- macOS sibling → `/mac` (theme system is a 1:1 port; canonical palettes are SHARED at `../mac/references/omarchy-palettes.toml` — single source of truth, do not fork)
- Docker / Kubernetes / CI → `/devops`
- Security hardening → `/security`
