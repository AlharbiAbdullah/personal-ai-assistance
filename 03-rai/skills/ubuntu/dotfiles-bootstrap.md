---
name: dotfiles-bootstrap
description: >
  The "spilled coffee" skill for Linux: restore the full Ubuntu + Hyprland
  environment from scratch in under 2 hours. USE WHEN setting up a fresh
  Ubuntu machine, recovering from disaster, or auditing what the current
  machine has that a rebuild would miss.
---

# Dotfiles Bootstrap (Ubuntu)

Assume this machine is gone. Rebuild Ubuntu 26.04 + Hyprland in under 2 hours,
nothing forgotten. Sibling of `/mac/dotfiles-bootstrap` — same philosophy,
apt instead of brew, Hyprland stack instead of AeroSpace.

## Philosophy

- **Declarative** — one script + package list describes the machine
- **Idempotent** — running it twice does no harm
- **Version-controlled** — dotfiles in git
- **Secrets separate** — never commit keys, tokens, SSH identities

## What this machine actually runs (rebuild inventory)

| Layer | Items |
|---|---|
| Desktop | hyprland, waybar, mako, fuzzel, hypridle, hyprlock, swaybg, hyprpolkitagent |
| Screenshot/clipboard | grim, slurp, wl-clipboard |
| Media/brightness keys | wpctl (pipewire), ddcutil (DDC/CI — user must be in `i2c` group) |
| Terminal | wezterm (`~/.wezterm.lua`, `enable_wayland=false` workaround), starship |
| Python | uv (curl installer → `~/.local/bin`; ships its own interpreters, no pyenv/build-deps) |
| Theme system | `~/.local/bin/theme`, `~/.config/themes/` (17 themes + wallpapers) |
| Scripts | `~/.local/bin/new-window`, `~/.local/bin/theme` |
| Apps | google-chrome (vendor deb), obsidian, code/cursor, gh |
| Vault | `~/helm` + Claude Code symlinks |

## The layout

```
~/dotfiles/
├── README.md
├── bootstrap.sh               # entry point
├── packages/
│   ├── apt.txt                # one package per line
│   └── snap.txt
├── hypr/                      # → ~/.config/hypr/
│   ├── hyprland.conf
│   ├── hypridle.conf
│   └── hyprlock.conf
├── waybar/  mako/  fuzzel/    # → ~/.config/<name>/
├── themes/                    # → ~/.config/themes/ (theme.lua files; wallpapers synced separately)
├── bin/                       # → ~/.local/bin/ (theme, new-window)
├── wezterm.lua                # → ~/.wezterm.lua
├── starship.toml              # → ~/.config/starship.toml
├── zsh/ or bash/              # shell rc files
├── git/.gitconfig
└── secrets/README.md          # gitignored — documents manual restores
```

## bootstrap.sh structure

```bash
#!/usr/bin/env bash
set -euo pipefail
DOTFILES="$HOME/dotfiles"

# 1. apt packages
sudo apt update
xargs -a "$DOTFILES/packages/apt.txt" sudo apt install -y

# 2. snaps
xargs -a "$DOTFILES/packages/snap.txt" -I{} sudo snap install {}

# 3. Vendor debs (not in apt)
which google-chrome >/dev/null || {
  wget -qO /tmp/chrome.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
  sudo apt install -y /tmp/chrome.deb
}

# 4. Link configs
mkdir -p ~/.config ~/.local/bin
for d in hypr waybar mako fuzzel themes; do
  ln -sfn "$DOTFILES/$d" "$HOME/.config/$d"
done
ln -sf "$DOTFILES/wezterm.lua"   "$HOME/.wezterm.lua"
ln -sf "$DOTFILES/starship.toml" "$HOME/.config/starship.toml"
ln -sf "$DOTFILES"/bin/*          "$HOME/.local/bin/"

# 5. Theme system init
"$HOME/.local/bin/theme" everforest || true

# 6. Manual steps prompt
cat <<'EOF'
=== DONE ===
Manual steps:
1. SSH + GPG keys from secure backup → ~/.ssh/, gpg --import
2. Sign into: GitHub (gh auth login), Chrome profile, Obsidian sync
3. Clone vault: git clone <helm remote> ~/helm
4. Claude Code symlinks (see below)
5. theme wallpapers sync (packs are not in the dotfiles repo)
6. Relog into Hyprland session
EOF
```

## apt.txt baseline

```
hyprland
waybar
mako-notifier
fuzzel
hypridle
hyprlock
swaybg
grim
slurp
wl-clipboard
ddcutil
wezterm
starship
git
gh
curl
wget
jq
ripgrep
fd-find
fzf
bat
build-essential
lm-sensors
smartmontools
fonts-jetbrains-mono
```

Adjust to reality: before writing the list, run
`apt-mark showmanual | sort` on the live machine and diff — that is the real
inventory, not memory.

Not in apt — installed via curl in bootstrap:
- **uv** (`curl -LsSf https://astral.sh/uv/install.sh | sh`) — replaces pyenv entirely
- **i2c group** (`sudo usermod -aG i2c $USER`) — required for ddcutil brightness keys; takes effect after relog

## Vault + Claude Code wiring (John-specific)

- Vault at `~/helm/`, symlinks:
  - `~/.claude/CLAUDE.md` → `~/helm/03-rai/CLAUDE.md`
  - `~/.claude/skills` → `~/helm/03-rai/skills`
- ChromaDB at `~/helm/03-rai/semantic-memory/chromadb/`
- Code projects live in `~/projects/`, not in the vault
- Document every symlink in `bootstrap.sh` so restore doesn't miss any

## What to keep separate (NOT in the repo)

- SSH/GPG private keys → encrypted backup + password manager
- API tokens → password manager / `~/.config/<tool>` restored manually
- Wallpaper packs → re-synced from Omarchy via `/ubuntu-theme wallpapers sync`
- Browser profile → Chrome sync

## Verification checklist

After running bootstrap:
- [ ] Hyprland session starts; waybar + mako up
- [ ] `theme` lists 17 themes; switching updates border + wezterm + starship
- [ ] SUPER+1..0 snaps between workspaces instantly
- [ ] CTRL+3 / CTRL+4 screenshots land in clipboard
- [ ] SUPER+L locks; volume keys work; brightness keys move the monitor (i2c group active — needs relog)
- [ ] `uv --version` works; `uv run python -c 'print(1)'` pulls an interpreter
- [ ] Git commits work (name + email); `gh auth status` green
- [ ] Claude Code reads the vault; skills resolve
- [ ] Obsidian opens vault
- [ ] WezTerm renders correctly (Wayland workaround still needed? check upstream)

## Anti-patterns

- Secrets in the dotfiles repo
- Editing live `~/.config` instead of the dotfiles source — drift is the killer
- Not regenerating `apt.txt` from `apt-mark showmanual` — list rots
- PPAs without recording them (`ls /etc/apt/sources.list.d/` belongs in the repo)
- Testing only on the live machine — a fresh VM run is the only proof

## Examples

- "Write me the bootstrap script for this machine"
- "What's installed here that my dotfiles repo would miss?"
- "Set up a fresh Ubuntu laptop to match this one"
- "Add the k3s tooling to the bootstrap"
