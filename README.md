# Personal AI Assistance (PAI)

**A complete personal AI "second brain" you run inside [Claude Code](https://claude.com/claude-code).**

PAI is a full, working system — not a prompt, not a wrapper. It's a Markdown "vault" plus a
brain of skills, agents, hooks, and a structured problem-solving algorithm that turns Claude
Code into an assistant that *knows you*: your goals, your projects, your voice, your rhythm.
It remembers across sessions, follows your rules, and helps you run your work and your life.

This repository is a **starter kit**. Everything is here and runnable; the personal data is a
fictional **"John Doe"** persona you replace with your own. Clone it, make it yours, and the
assistant grows into a second brain that's actually about you.

> The assistant is named **Rai** by default. It's just a name — rename it to whatever you like
> (see [SETUP](./SETUP.md)).

---

## The idea

Most AI assistants forget you the moment the chat ends. PAI flips that. You externalize the
things that make help *good* — who you are, what you're building, how you write, what you value —
into plain Markdown files. The assistant loads them every session, works against them, and
writes back what it learns. Over time it stops being a generic chatbot and becomes *yours*.

It rests on two halves:

- **`02-ana/` — you.** Your identity, goals, projects, journal, finances, family, voice.
  Auto-loaded every session so the assistant always has context. (Private. Never published.)
- **`03-rai/` — the brain.** The machinery: 35 skills, 12 specialist agents, ~38 hooks, a
  7-phase problem-solving algorithm, file + vector memory, and config.

Around them sit numbered folders for capturing ideas, doing research, taking notes, tracking
work, and running a daily news digest — a whole knowledge-and-life operating system.

---

## What's inside

```
personal-ai-assistance/
├── 02-ana/         YOU — identity (auto-loaded), journal, todos, finances, family, voice
├── 03-rai/         THE BRAIN — skills, agents, hooks, algorithm, config, memory
│   ├── skills/       35 skills: /research, /architecture, /writing, /news-digest, /investment, …
│   ├── agents/       12 specialists: architect, engineer, debugger, reviewer, researcher, …
│   ├── hooks/        ~38 lifecycle hooks: identity load, memory, security, session naming
│   ├── algorithm/    the 7-phase method (OBSERVE → THINK → PLAN → BUILD → EXECUTE → VERIFY → LEARN)
│   ├── config/       settings.json, mcp.json, statusline, security patterns
│   ├── memory/       file memory — starts empty, fills as you use it
│   └── semantic-memory/  vector recall (ChromaDB) — rebuilt locally
├── 00-landing → 13-archive   capture pipeline, inbox, projects, learning, knowledge, news, archive
└── 12-system/manual/   a 23-chapter manual that documents every screw and bolt
```

The capture and idea pipelines move things from a quick note to finished work:

```
00-landing → 01-inbox → (research + rate) → knowledge / ideas / projects / learning
09-ideas:  Seed → Plant → Tree → Graduated → a real project
```

---

## What it can do

- **Know you.** Identity auto-loads so every answer is in your context, not a vacuum.
- **Run structured work.** The algorithm scales effort to the task and writes a short PRD for
  anything non-trivial, so big work is planned before it's built.
- **Specialize on demand.** Type `/architecture`, `/research`, `/writing`, `/testing`,
  `/security`, `/devops` and more — each routes to focused skills and expert agents.
- **Remember.** File memory plus a vector index let it recall past decisions and context.
- **Keep a rhythm.** `/routine` runs your journal and day/week prep; `/life` tracks your
  self-model and captures wisdom.
- **Produce.** A personalized daily **news digest**, knowledge notes, idea pipelines, an
  optional investing practice, and bilingual (English + Arabic) writing support.
- **Stay safe.** A security validator hook blocks catastrophic commands and watches for secrets.

Read the **[manual](./12-system/manual/README.md)** for the full tour, or the
**[cheatsheet](./12-system/manual/21-cheatsheet.md)** for one page.

---

## Requirements

- **[Claude Code](https://claude.com/claude-code)** (the CLI, desktop, or IDE extension).
- **Python 3** (the hooks are Python; mostly standard library).
- **[uv](https://github.com/astral-sh/uv)** — used to run the vector-memory step in an isolated env.
- **git** — to clone and to track your vault.
- A Markdown editor like **[Obsidian](https://obsidian.md)** is nice for browsing the vault, but optional.

---

## Get started

→ **[SETUP.md](./SETUP.md)** walks you from zero to your first session in a few minutes:
clone it, wire it into Claude Code, replace John Doe with you, and go.

---

## A note on the examples

This kit ships with a fictional **John Doe** persona so you can see the system in motion — a
sample identity, an example journal entry, a budget template, a learning board. The manual and
skills reference these as illustrations. **Replace them with your own** as you adopt the vault;
the mechanics underneath are real and battle-tested.

---

## Credits & inspiration

This project was inspired — heavily — by **[PAI · Personal AI Infrastructure](https://github.com/danielmiessler/Personal_AI_Infrastructure)** by **[Daniel Miessler](https://danielmiessler.com)**. PAI is the original idea and the primary source this kit grew out of: the philosophy of treating Claude Code as the *engine* and building your own personal layer on top of it, the identity that loads every session, the seven-phase problem-solving algorithm (OBSERVE → THINK → PLAN → BUILD → EXECUTE → VERIFY → LEARN), and the hooks-and-skills architecture all trace back to Daniel's work.

If you find this useful, go to the source: read [Daniel's writing on building a Personal AI Infrastructure](https://danielmiessler.com/blog/personal-ai-infrastructure) and explore [the PAI project](https://github.com/danielmiessler/Personal_AI_Infrastructure). This kit is one person's adaptation of those ideas — the credit for the concept is his.

And the whole thing runs on **[Claude Code](https://claude.com/claude-code)** by Anthropic — the engine underneath it all.

---

## License

[MIT](./LICENSE). Use it, fork it, make it yours. If you build something good on top, sharing
it back is appreciated but not required.

*Built as a gift, so others can have a second brain too.*
