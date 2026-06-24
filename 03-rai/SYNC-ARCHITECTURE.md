# Sync Architecture (optional)

Most users run this vault on **one machine** and can ignore this file. It documents an
**optional** pattern for keeping the same vault in sync across two or more machines.

## The problem

The vault is a git repo. If you edit it on two machines, naive `git pull/push` from both
sides produces merge conflicts — especially on binary/derived state (the ChromaDB index,
session state). You want exactly one machine to be the source of truth.

## The pattern: single coordinator

Pick **one machine as the sole coordinator**. Only the coordinator:
- writes to the git remote (`origin`),
- rebuilds the ChromaDB semantic index,
- runs the scheduled maintenance job.

Every other machine is a **passive replica** that receives changes from the coordinator
(e.g. over SSH on a private network) and never pushes to `origin` itself.

```
  ┌─────────────────┐        push/pull         ┌──────────┐
  │   COORDINATOR    │ ───────────────────────▶ │  origin  │  (GitHub)
  │  (one machine)   │                          └──────────┘
  │  - sole origin   │
  │    writer        │        SSH (private net)
  │  - builds index  │ ───────────────────────▶ ┌─────────────────┐
  │  - runs cron     │                          │     REPLICA      │
  └─────────────────┘                           │  (other machines)│
                                                │  read-only sync  │
                                                └─────────────────┘
```

## Wiring it (placeholders — fill in your own)

| Role | Host | User | Private IP (e.g. Tailscale) |
|------|------|------|------------------------------|
| Coordinator | `<coordinator-host>` | `<user>` | `100.64.0.1` |
| Replica | `<replica-host>` | `<user>` | `100.64.0.2` |

1. Put both machines on a private mesh network (e.g. Tailscale) so the coordinator can
   reach the replica over SSH without exposing anything publicly.
2. On the **coordinator**, schedule a maintenance job (cron / systemd timer / launchd) that:
   commits local changes → pulls/merges → rebuilds the index → pushes to `origin` →
   pushes the updated tree to each replica over SSH.
3. On a **replica**, the wake/refresh step is pull-only: fetch from the coordinator, never
   push to `origin`.

The reference maintenance scripts live in `03-rai/skills/rai/scheduled/`. Adapt the host
names, users, and IPs to your setup, or delete them if you run a single machine.

## Rules that keep it from breaking

- **One origin writer.** Only the coordinator pushes to GitHub. Replicas that push cause
  divergence.
- **Don't sync derived state.** The ChromaDB index is rebuilt from source memory; let each
  machine (or just the coordinator) regenerate it rather than syncing the binary store.
  It is gitignored for this reason.
- **Fast-forward only on the replica.** A replica that has diverged should reset to the
  coordinator's tree, not merge.
