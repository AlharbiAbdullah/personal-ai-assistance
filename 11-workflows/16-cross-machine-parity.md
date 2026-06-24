# Cross-Machine Parity

**Triggered by:** "do it on ubuntu too" / "mirror to the other machine" / "set up on both boxes"
**Cadence:** Per tool — runs often during a buildout (roughly weekly)
**Done when:** the tool/config works **LIVE on both machines**, with OS divergences correctly translated (not blind-copied).

The stated goal is a 1:1 mirror (dev-env at `~/work/Dev_Env`). Each port keeps
re-litigating the same OS-divergence + sync-direction lore — and that's exactly where
the mistakes happen. This playbook freezes that lore into gates so a port is a checklist,
not a re-derivation.

```
Delta gate → Read source → Port w/ translation → Single-writer gate → Verify LIVE → Leave for coordinator
```

> **Two gates carry the whole value.** The DELTA GATE stops blind copies (Mac zsh ≠
> Linux bash; launchd ≠ systemd). The SINGLE-WRITER GATE stops the Mac from pushing.
> Source of truth: `03-rai/SYNC-ARCHITECTURE.md`.

---

## Steps

### 1. Delta gate — enumerate what diverges BEFORE porting

- [ ] **Shell**: Mac = zsh ↔ Linux = bash. **NEVER set up zsh on Linux.** Target
      `.bashrc` / starship-bash / `fzf --bash`. A `.zshrc` copied to Linux is a bug.
- [ ] **Terminal**: WezTerm (Mac) ↔ Ghostty (Ubuntu). Ghostty live-reloads via SIGUSR2.
- [ ] **Window manager**: AeroSpace (Mac, Cmd-based tiling) ↔ Hyprland (Ubuntu, Wayland).
- [ ] **Scheduler**: launchd (Mac) ↔ systemd timers (Ubuntu). A launchd plist has no
      meaning on Linux — it becomes a `.timer` + `.service` unit.
- [ ] **Paths**: `~/Library/...`, `/Users/...` (Mac) ↔ `~/.config/...`, `~/.local/...`,
      `/home/...` (Linux). Map every absolute path.

> **Decision Point**: is this config genuinely 1:1, or does one side need a translated
> equivalent?
> - Pure data (themes, dotfile values, vault content) → ports nearly straight.
> - OS-bound mechanism (scheduler, WM, terminal, shell) → translate, don't copy. Write
>   the divergence down in this step before touching the target.

### 2. Read the source machine's config

- [ ] Read the working config on the machine where it already runs. Do not port from
      memory or from the repo if the live file is newer (Mac live aerospace/launchd
      can be ahead of the repo).
- [ ] For desktop look-and-feel work, route through **`/mac → theme`** or
      **`/ubuntu → theme`** so the full adapter set is in view (mac: WezTerm, VS Code,
      Cursor, Starship, JankyBorders, OpenCode, appearance, wallpaper · ubuntu: WezTerm,
      Ghostty, tmux, Hyprland border, VS Code, Cursor, Chrome policy, gnome color-scheme,
      Starship, waybar, swaybg, mako/HUD, fastfetch). **Obsidian is EXCLUDED — pinned.**

### 3. Port to the target with translation (not a blind copy)

- [ ] Apply the step-1 deltas: rewrite paths, swap shell idioms, convert the scheduler
      unit (launchd plist → systemd `.timer`+`.service` via **`/ubuntu → tips`**, or the
      reverse via **`/mac → automation`**).
- [ ] Desktop config: drive it with **`/ubuntu → theme`** / **`/ubuntu → hyprland`**
      (or the Mac equivalents). Themes cross-sync via `~/.config/themes` (manual-sync —
      it goes stale, so confirm you're porting the current palette, not a stale one).
- [ ] Ghostty/waybar reload via SIGUSR2; **JankyBorders needs a full restart**.

> **Decision Point**: did the target gain something the source lacks (e.g. a systemd
> `RECOVERY=1` env, a waybar module with no Mac analog)? That's allowed — 1:1 is about
> *parity of capability*, not byte-identical files. Note the intentional divergence.

### 4. Single-writer gate (the one that bites)

- [ ] Confirm the sync direction: **Linux (`pc`) is the SOLE coordinator and ONLY origin
      writer.** This Mac is a **passive replica**.
- [ ] **The Mac NEVER `git push`.** If you ported a vault/config file from the Mac side,
      its churn stays local for the coordinator's next run. Source: `03-rai/SYNC-ARCHITECTURE.md`.
- [ ] Reaching Ubuntu to apply or verify the port: **keyless Tailscale SSH** (`ssh pc`),
      never GitHub round-trips from the Mac.

### 5. Verify the tool runs LIVE on the target

- [ ] **The file landing is NOT "done."** Run the tool on the target machine and watch it
      work: reload the WM/terminal, fire the timer, source the shell, open the app.
- [ ] Scheduler ports: confirm the unit is enabled + the next run is scheduled (e.g.
      `systemctl --user list-timers` for the news timers `news-daily.timer` /
      `news-weekly.timer`); a `RECOVERY=1` manual run via
      `03-rai/skills/news-digest/scheduled/run-news-ubuntu.sh` proves it end-to-end.
- [ ] Theme/desktop ports: eyeball it live — palette applied, border restarted, no stark
      foreground (~75–82% brightness floor).

### 6. Sync (leave for the coordinator)

- [ ] Vault/config edits stay **local** on the Mac. The Linux coordinator commits + pushes
      at its next maintenance run (04/10/16/22:00 UTC).
- [ ] **Do not `git push` from the Mac** — single-writer rule, `03-rai/SYNC-ARCHITECTURE.md`.
- [ ] If the port lives in a **code project** under `~/projects/` (not the vault), that's
      the one case you commit it yourself — run **`/git → commit`** there.

---

## Connections

- Desktop adapters: `/mac → theme`, `/ubuntu → theme`, `/ubuntu → hyprland`
- Scheduler translation: `/ubuntu → tips`, `/mac → automation`
- Dotfiles bootstrap on a fresh box: `/mac → dotfiles-bootstrap`, `/ubuntu → dotfiles-bootstrap`
- Single-writer sync (read this before any cross-machine edit): `03-rai/SYNC-ARCHITECTURE.md`
- Dev-env mirror root: `~/work/Dev_Env`
- Code-project port (the one that DOES commit): `/git → commit`
