# Setup

From zero to your first session. Plan for ~15 minutes. None of this is hard — it's mostly
putting files in the right place and telling Claude Code where to look.

> **The short version:** clone this into `~/helm`, symlink a handful of files into `~/.claude`,
> replace "John Doe" with you, and start Claude Code in `~/helm`.

---

## 0. Prerequisites

Install these first:

| Tool | Why | Check |
|------|-----|-------|
| [Claude Code](https://claude.com/claude-code) | The host this runs inside | `claude --version` |
| Python 3.9+ | The hooks are Python (mostly stdlib) | `python3 --version` |
| [uv](https://github.com/astral-sh/uv) | Runs the vector-memory step in an isolated env | `uv --version` |
| git | Clone + track your vault | `git --version` |

> macOS = zsh, Linux = bash — both work. The examples below are shell-agnostic.

---

## 1. Get the kit

Clone it to **`~/helm`** (the default path the system expects):

```bash
git clone <your-fork-url> ~/helm
cd ~/helm
```

> Want a different folder name? You can — but `03-rai/config/settings.json` and
> `03-rai/hooks/lib/paths.py` default to `~/helm`. If you use another path, set the
> environment variable `PAI_DIR=/path/to/your/03-rai` and update the `$HOME/helm/...`
> paths in `settings.json`. For a first run, `~/helm` is the path of least resistance.

---

## 2. Wire it into Claude Code

Claude Code reads its config from `~/.claude`. We point a few entries there at the brain in
`03-rai`. **Back up anything you already have first** — this won't delete your data, but don't
clobber an existing setup blind:

```bash
# Back up an existing config if you have one
[ -e ~/.claude ] && cp -a ~/.claude ~/.claude.backup-$(date +%Y%m%d)

mkdir -p ~/.claude

# Link the brain into Claude Code (force-replaces only these specific entries)
ln -sfn  ~/helm/03-rai/CLAUDE.md            ~/.claude/CLAUDE.md
ln -sfn  ~/helm/03-rai/hooks                ~/.claude/hooks
ln -sfn  ~/helm/03-rai/skills               ~/.claude/skills
ln -sfn  ~/helm/03-rai/agents               ~/.claude/agents
ln -sfn  ~/helm/03-rai/memory               ~/.claude/MEMORY
ln -sfn  ~/helm/03-rai/config/settings.json ~/.claude/settings.json
ln -sfn  ~/helm/03-rai/config/mcp.json      ~/.claude/mcp.json
ln -sfn  ~/helm/03-rai/config/statusline.sh ~/.claude/statusline.sh
```

That's the whole integration: identity, skills, agents, hooks, memory, settings, and the
status line now come from your vault.

---

## 3. Verify the wiring

```bash
ls -l ~/.claude/skills        # should point into ~/helm/03-rai/skills
python3 ~/helm/03-rai/hooks/session-start.py >/dev/null && echo "hooks run OK"
uv run --python 3.12 --with chromadb python3 -c "import chromadb; print('chromadb OK')"
```

If those three succeed, the machine side is done.

---

## 4. Make it yours (the important part)

Right now the assistant thinks you're **John Doe**. Replace the persona with the real you:

1. **Identity** — edit every file in `02-ana/identity/`. Start with `who-i-am.md`, `goals.md`,
   `projects.md`, and `tech-stack.md`. This is what auto-loads each session; it's the single
   highest-leverage thing you'll do.
2. **Your PII markers** — open `03-rai/.pai-protected.json` and put *your* name, family names,
   employer, email pattern, etc., so the security hook can protect them.
3. **Personalize a few skills** (optional, do later):
   - News: `03-rai/skills/news-digest/config.yaml` + the `REGION_SUBSTRINGS` / `REGION_BOUNDED`
     constants near the top of `present_v5.py` — set your interests and region.
   - Writing voice: drop 3–5 samples of your writing into `02-ana/voice-samples/`.
   - Security rules: tune `03-rai/identity/security-patterns.yaml` to your environment.
4. **Clear the examples** when ready: the sample journal entry, `02-ana/financial/budget.md`
   placeholders, and `north-star.md` are illustrations — overwrite them with real content.

> You don't have to do all of this up front. Identity first; the rest as you go.

---

## 5. (Optional) Rename the assistant

The assistant is called **Rai**. To rename it (e.g. to "PAI", "Jarvis", or your own):

```bash
# preview the matches first
grep -rl '\bRai\b' ~/helm/03-rai/identity ~/helm/03-rai/CLAUDE.md
# then replace across the brain (pick your name)
grep -rl '\bRai\b' ~/helm/03-rai | xargs sed -i '' 's/\bRai\b/YourName/g'   # macOS
# (on Linux, use:  sed -i 's/\bRai\b/YourName/g')
```

The folder `03-rai` can keep its name — it's only a path.

---

## 6. First session

```bash
cd ~/helm
claude
```

Then ask it: **"Who am I, and what am I working on?"** If it answers from your identity files,
the auto-load is working and you're live. Try a skill next — `/research`, `/architecture`, or
`/news-digest`.

---

## 7. (Optional) Going further

- **Daily news digest** — see [manual ch. 15](./12-system/manual/15-news-digest.md). The
  `requests` package is needed for some collectors: `pip install --user requests`.
- **Multiple machines** — see [`03-rai/SYNC-ARCHITECTURE.md`](./03-rai/SYNC-ARCHITECTURE.md).
  Single machine? Ignore it.
- **Publishing your own fork publicly** — uncomment the `02-ana/` and `03-rai/memory/` lines in
  `.gitignore` so your private life and accumulated memory stay out of the public repo.

---

## Troubleshooting

- **Identity didn't load** — confirm `~/.claude/CLAUDE.md` resolves to `~/helm/03-rai/CLAUDE.md`
  and that `02-ana/identity/` has your `.md` files.
- **A hook errored on start** — run it directly: `python3 ~/helm/03-rai/hooks/session-start.py`.
- **chromadb step fails** — make sure `uv` is installed; the wrapper is
  `03-rai/semantic-memory/scripts/py-chroma.sh`.
- **Anything else** — the [troubleshooting chapter](./12-system/manual/20-troubleshooting.md)
  covers the common failures in depth.

Welcome aboard. Make it yours.
