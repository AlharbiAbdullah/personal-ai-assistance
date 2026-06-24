# Theme Rollout

**Triggered by:** "add this theme" / "{X} didn't adapt/repaint" / "roll out {theme}"
**Cadence:** Ad-hoc (recurs every time theme work happens)
**Done when:** every WIRED adapter on BOTH machines has actually repainted to the new theme — verified per-adapter, not assumed.

Dozens of past PRDs are whack-a-mole: one adapter silently doesn't repaint and the
whole rollout reads as "done" until eyes catch it days later. This playbook is the
ordering + the gates — the actual propagation is the `/mac → theme` and
`/ubuntu → theme` skills. The verify step (4) is the entire point.

```
Source palette → Soft-fg gate → Mac adapters → Ubuntu adapters → Verify-each-repainted → Cross-machine themes → Leave for coordinator
```

> **Palette gate (overrides upstream rules):** warm muted dark ONLY
> (gruvbox / everforest / kanagawa / ristretto family). Cool blue palettes feel
> clinical; neon feels loud. Foreground must land **75–82% brightness** — soft, never
> stark white. This soft-fg rule OVERRIDES any "never make up colors" upstream rule.

---

## Steps

### 1. Source the palette — GATE before anything propagates

- [ ] Pin the source: a named warm-muted-dark theme or an explicit hex palette.
- [ ] **GATE — reject if not warm muted dark.** Cool blues / neon are out.
- [ ] **GATE — foreground brightness 75–82%.** If the source ships a stark white fg
      (>85%), soften it. This override is intentional; do not preserve upstream whites.
- [ ] Only past both gates does anything get propagated.

> **Decision Point**: source palette has a stark-white foreground?
> - Soften to 75–82% before wiring. The soft-fg rule wins over color fidelity.
> - If you cannot soften without breaking contrast, STOP and surface it — don't ship.

### 2. Mac adapters — `/mac → theme`

- [ ] Run **`/mac → theme`** to propagate the gated palette to every Mac adapter:
      **WezTerm, VS Code, Cursor, Starship, JankyBorders, OpenCode, macOS appearance,
      wallpaper.**
- [ ] **JankyBorders needs a restart** to repaint — it does not live-reload.
- [ ] **Obsidian is EXCLUDED** (pinned theme). Never touch it.

### 3. Ubuntu adapters — `/ubuntu → theme` (over Tailscale SSH from the Mac)

- [ ] Reach `pc` over keyless Tailscale SSH and run **`/ubuntu → theme`** to propagate to:
      **WezTerm, Ghostty, tmux, Hyprland border, VS Code, Cursor, Chrome policy,
      gnome color-scheme, Starship, waybar, swaybg wallpaper, mako/HUD, fastfetch.**
- [ ] **Live-reload, not restart:** Ghostty reloads via **SIGUSR2**; waybar reloads via
      **SIGUSR2**. fastfetch is palette-driven (next launch shows it).
- [ ] **Obsidian is EXCLUDED** here too.

### 4. VERIFY GATE — walk EACH adapter, confirm it actually repainted

- [ ] This is the step that gets skipped and causes the whack-a-mole. **Do not assume.
      Look at each surface.**
- [ ] Mac (8): WezTerm, VS Code, Cursor, Starship, JankyBorders (restarted?), OpenCode,
      macOS appearance, wallpaper.
- [ ] Ubuntu (13): WezTerm, Ghostty (SIGUSR2 fired?), tmux, Hyprland border, VS Code,
      Cursor, Chrome policy, gnome color-scheme, Starship, waybar (SIGUSR2 fired?),
      swaybg, mako/HUD, fastfetch.

> **Decision Point**: any adapter still showing the OLD theme?
> - It did NOT repaint. Go back to its skill step, re-wire, re-fire the reload/restart.
> - **The rollout is NOT done while a single wired adapter is stale.** "Looks done"
>   is the failure mode this gate exists to kill.

### 5. Cross-machine themes — refresh `~/.config/themes` on both

- [ ] `~/.config/themes` is **manual-sync** — it goes stale after the other machine
      pushes theme work. Refresh it on BOTH Mac and Ubuntu so neither drifts.
- [ ] This is the shared palette store; if it's stale, the next rollout starts from a
      wrong baseline.

### 6. Sync (leave for the coordinator)

- [ ] Vault / config edits stay **local**. The Linux coordinator commits + pushes at its
      next maintenance run (04/10/16/22:00 UTC).
- [ ] **Do not `git push` from the Mac** — single-writer rule, `03-rai/SYNC-ARCHITECTURE.md`.

---

## Adapter map (verified)

| Machine | Adapters | Reload mechanism |
|---------|----------|------------------|
| Mac (8) | WezTerm, VS Code, Cursor, Starship, JankyBorders, OpenCode, macOS appearance, wallpaper | JankyBorders = **restart**; rest auto/relaunch |
| Ubuntu (13) | WezTerm, Ghostty, tmux, Hyprland border, VS Code, Cursor, Chrome policy, gnome color-scheme, Starship, waybar, swaybg, mako/HUD, fastfetch | Ghostty + waybar = **SIGUSR2**; fastfetch = palette-driven |
| Excluded | Obsidian (pinned) | never touch |

---

## Connections

- Mac propagation: `/mac → theme`
- Ubuntu propagation: `/ubuntu → theme`
- Shared palette store: `~/.config/themes` (manual-sync, goes stale)
- Single-writer sync: `03-rai/SYNC-ARCHITECTURE.md`
- Ubuntu desktop internals (waybar/mako/Hyprland): `/ubuntu → hyprland`
- Capture a recurring rollout fix worth keeping: [[08-weekly-review]]
