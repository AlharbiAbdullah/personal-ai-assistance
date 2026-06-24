---
name: tips
description: >
  Ubuntu/Linux power-user tips, hidden settings, native features people miss.
  USE WHEN the user wants the "right" way to do something on Linux or
  discovers they've been fighting the OS.
---

# Ubuntu Tips

Native features worth knowing on this Hyprland + Ubuntu 26.04 machine.
Shortcuts that save hours over a year.

## This machine's bind map (muscle memory)

- `SUPER + 1..0` — workspaces (instant, no animation)
- `SUPER + SHIFT + 1..0` — throw window to workspace
- `SUPER + arrows` — focus · `SUPER + SHIFT + arrows` — move window
- `SUPER + return` — wezterm · `SUPER + D` — fuzzel · `SUPER + B` — chrome · `SUPER + O` — obsidian
- `SUPER + W` — close · `SUPER + F` — fullscreen · `SUPER + SHIFT + space` — float
- `CTRL + 3` — full screenshot → clipboard · `CTRL + 4` — region → clipboard · `Print` — file in ~/Pictures
- `SUPER + CTRL + T` — theme cycle · `SUPER + CTRL + W` — next wallpaper
- `SUPER + L` — lock · `ALT + SHIFT` — us ⇄ ara layout
- Volume/mute keys — wpctl (work on lock screen) · Brightness keys — ddcutil over DDC/CI (desktop monitor, no kernel backlight)

## Wayland clipboard from the terminal

The `pbcopy`/`pbpaste` of this machine:

```bash
echo "hi" | wl-copy                  # copy
wl-paste                             # paste
wl-paste --list-types                # what's on the clipboard
grim -g "$(slurp)" - | wl-copy       # region screenshot → clipboard
wl-copy < image.png                  # put an image on the clipboard
```

## Shell power (bash)

- `Ctrl+R` — reverse history search (fzf takes it over if wired)
- `Ctrl+A / Ctrl+E / Ctrl+U / Ctrl+W / Ctrl+L` — line start/end, clear line, delete word, clear screen
- `Ctrl+Z` → `fg` — suspend/resume
- `!!` — last command (`sudo !!` is the classic) · `!$` — last arg · `Alt+.` — cycle last args
- `cd -` — previous directory
- `^foo^bar` — re-run last command with substitution

## apt / snap fluency

```bash
apt list --installed 2>/dev/null | grep <pkg>
apt show <pkg>                       # description, deps, size
apt-cache search <term>             # find a package
apt-mark showmanual                  # what YOU installed (vs deps)
sudo apt autoremove --purge          # drop orphaned deps + configs
apt-file search <missing-binary>     # which package ships a file (apt install apt-file)

snap list
snap info <name>
sudo snap set system refresh.retain=2   # stop hoarding old revisions
```

`command-not-found` already tells you the package when you typo a binary.

## systemd fluency

```bash
systemctl --user list-timers         # your scheduled jobs
systemctl status <unit>              # state + recent log lines in one
journalctl -u <unit> -e              # full log, jump to end
journalctl -f                        # live tail everything
systemd-analyze blame                # what slowed down boot
systemctl --failed                   # anything dead right now
busctl / loginctl lock-session       # lock from a script
```

`systemctl edit <unit>` — override a vendor unit without touching /usr.

## Files + navigation

```bash
xdg-open .                           # `open .` equivalent
nautilus --select <file>             # reveal in file manager
fd <pattern>                         # find, but good (fd-find)
rg <pattern>                         # grep, but good
ncdu /                               # interactive disk usage (apt install ncdu)
stat <file>                          # everything about a file
```

## Hidden gems

- **fuzzel --dmenu** — pipe anything in, get a picker. Instant custom menus.
- **GTK dark mode for legacy apps**: `gsettings set org.gnome.desktop.interface color-scheme prefer-dark`
- **`systemd-run --user --on-calendar=...`** — one-shot scheduled command, no unit file
- **`script -r` / `scriptreplay`** — record and replay a terminal session
- **`/proc/pressure/{cpu,memory,io}`** — PSI: is the machine *actually* under pressure
- **`timedatectl`, `localectl`, `hostnamectl`** — system facts in one command each
- **`ip -br a`** — readable network interface summary
- **`tldr <cmd>`** — examples instead of manpages (apt install tldr)
- **Magic SysRq** `Alt+SysRq+REISUB` — last-resort safe reboot of a frozen box (if enabled)

## Hyprland niceties

```bash
hyprctl clients                      # every window + class (for rules)
hyprctl dispatch workspace e+1       # scriptable everything
hyprctl keyword general:gaps_in 0    # live-tweak without editing config
hyprctl reload                       # also on SUPER+SHIFT+R
```

Arabic layout: `ALT+SHIFT` toggles; waybar can show the active layout
(`hyprland/language` module) if you ever lose track.

## Obscure but useful

```bash
notify-send "title" "body"           # toast via mako (HUD from any script)
loginctl lock-session                # lock programmatically
cat /etc/os-release                  # exact OS version
ldd <binary>                         # what libs it needs
strace -f -e trace=file <cmd>        # what files a command actually touches
lsof +D <dir>                        # who has files open in a dir
fuser -v <file>                      # which process holds a file
```

## Productivity patterns

- **One workspace per project** — SUPER+number is instant; let muscle memory do the routing
- **fuzzel-dmenu scripts for repeated choices** — power menu, project picker, bookmark opener
- **systemd user timers over cron** — they log to journalctl and inherit session env
- **`apt-mark showmanual` quarterly** — feeds the dotfiles rebuild list

## Examples

- "What's the Linux equivalent of pbcopy?"
- "How do I find which package provides a command?"
- "Schedule a script without writing a unit file"
- "Lock the screen from a script"
