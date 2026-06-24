---
name: diagnostics
description: >
  Ubuntu/Linux hardware + software diagnostics. USE WHEN the machine is slow,
  hot, losing Wi-Fi, running out of memory or disk, crashing, or behaving
  weird. Covers thermal, memory, CPU, disk, network, USB, journal, Wayland.
---

# Ubuntu Diagnostics

Machine is misbehaving. Isolate the problem systematically.

## When to use

- System feels slow; fan is loud
- Apps crash or hang; compositor glitches
- Wi-Fi drops or is slow
- External displays / USB devices acting up
- Battery drains fast
- Disk full or slow

## When NOT to use

- A specific app is broken — reinstall it or file a bug
- Desktop config / keybind issues — use `hyprland.md`

## Triage

Start here, in order:

### 1. Live resource snapshot

```bash
top -bn1 | head -20              # CPU hogs
free -h                          # memory + swap
df -h /                          # root disk
journalctl -p err -b --no-pager | tail -30   # errors since boot
systemctl --failed               # dead services
```

### 2. Per-subsystem deep dive

Pick the tab that matched, below.

## CPU + thermal

```bash
# Frequency + governor
grep MHz /proc/cpuinfo | sort -u | head
cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor

# Temps (lm-sensors; `sudo apt install lm-sensors && sudo sensors-detect` once)
sensors

# Throttling evidence
journalctl -k -b | grep -iE 'thermal|throttl'

# Who's burning CPU
ps -eo pid,pcpu,comm --sort=-pcpu | head -10
```

High temps: dust, ambient, runaway process, or `performance` governor stuck on.
Laptop on `powersave` feeling slow → check `powerprofilesctl get`.

## Memory pressure

```bash
free -h                          # available is the number that matters
ps -eo pid,pmem,rss,comm --sort=-rss | head -15
cat /proc/pressure/memory        # PSI: some/full avg10 — >10 sustained = real pressure
swapon --show
```

- `available` healthy: fine, cached memory is reclaimable — don't chase "high used".
- Swapping aggressively (`vmstat 1` si/so columns nonzero): close Chrome tabs, Electron apps.
- OOM kills: `journalctl -k -b | grep -i oom`.

## Disk space + health

```bash
df -h
sudo du -xsh /var/* ~/.cache/* ~/* 2>/dev/null | sort -h | tail -20
find ~ -type f -size +1G 2>/dev/null

# Common Ubuntu hogs
journalctl --disk-usage          # cap with: sudo journalctl --vacuum-size=500M
sudo apt clean                   # apt package cache
snap list --all | awk '/disabled/{print $1, $3}'   # old snap revisions
du -sh ~/.cache ~/.local/share/Trash

# SMART health
sudo apt install smartmontools
sudo smartctl -H /dev/nvme0n1
sudo smartctl -a /dev/nvme0n1 | grep -iE 'wear|temperature|hours'
```

Old snap revisions: `sudo snap set system refresh.retain=2`.

## Network

```bash
# Wi-Fi signal + link
nmcli device wifi list
iw dev $(iw dev | awk '/Interface/{print $2}') link

# DNS
resolvectl status | head -20
dig google.com

# Path + reachability
ping -c 5 1.1.1.1
mtr -rwc 10 google.com           # traceroute + loss in one

# Who's using bandwidth
sudo apt install iftop; sudo iftop
ss -tunap | head -20             # active sockets
```

Wi-Fi dropping: `journalctl -u NetworkManager -e` for disconnect reasons;
check power-save (`iw dev <if> get power_save`, disable to test); 2.4 vs 5GHz;
driver messages in `journalctl -k | grep -i <driver>`.

## Journal + crashes

```bash
journalctl -b -p warning --no-pager | tail -50   # this boot, warnings up
journalctl -b -1 -e                              # previous boot (after a freeze)
journalctl -u <service> -e                       # one service
journalctl --user -u <unit> -e                   # user unit
coredumpctl list                                 # crashed processes
coredumpctl info <pid>                           # stack trace
ls /var/crash/                                   # apport reports
```

## Hyprland / Wayland specific

```bash
hyprctl version
cat $XDG_RUNTIME_DIR/hypr/$HYPRLAND_INSTANCE_SIGNATURE/hyprland.log | tail -50
echo $XDG_SESSION_TYPE           # must be "wayland"

# App won't render / blurry → it's running XWayland
hyprctl clients | grep -B2 xwayland

# GPU
glxinfo -B 2>/dev/null | head    # mesa-utils
journalctl -k -b | grep -iE 'drm|gpu|amdgpu|i915|nvidia' | tail -20
```

Electron apps blurry on Wayland → launch with `--ozone-platform=wayland`
(already exported via `ELECTRON_OZONE_PLATFORM_HINT=auto` in hyprland.conf).

## External devices

```bash
lsusb; lsusb -t                  # USB tree + speed
sudo dmesg -w                    # live — plug the device in and watch
hyprctl monitors                 # displays as Hyprland sees them
ls /sys/class/drm/*/status       # connector state (connected/disconnected)
```

Flaky device: different port, different cable, check `dmesg` for resets.

## Battery / power

```bash
upower -i $(upower -e | grep BAT)   # capacity, health, rate
powerprofilesctl get                 # balanced / power-saver / performance
sudo apt install powertop; sudo powertop   # per-process wakeups
```

Health = energy-full / energy-full-design. Under 80% → battery is aging.

## Resets (least → most invasive)

1. Restart the misbehaving app
2. Restart the failing service: `systemctl --user restart <unit>` / `sudo systemctl restart <unit>`
3. Relog (restarts Hyprland session)
4. Reboot
5. Boot previous kernel (GRUB → Advanced) — isolates kernel regressions
6. `sudo apt install --reinstall <pkg>`
7. Fresh install — see `dotfiles-bootstrap.md`; that's why it exists

## Anti-patterns

- Rebooting as the first move — read the journal first; evidence dies with the session
- Chasing "high memory used" when `available` is fine — Linux caches aggressively by design
- Killing random processes — look them up first
- Installing "system cleaners" — `journalctl --vacuum`, `apt clean`, snap retain cover it
- Editing /etc by hand without noting it — undocumented drift makes the next rebuild painful

## Examples

- "Laptop is hot and the fan won't stop"
- "Why did the machine freeze last night?"
- "Wi-Fi keeps dropping on this network"
- "Root partition is full — what's safe to delete?"
- "External monitor not detected after replug"
