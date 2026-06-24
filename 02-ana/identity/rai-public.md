# Rai Public Persona

> The single source of truth for my **public** persona (e.g. the bio on `https://johndoe.dev`).
> Unlike the rest of `identity/`, this file is meant to leave the vault — so it contains
> nothing private. A publish pipeline reads it; a firewall (see the manual, ch. 13) blocks
> any private marker (real name variants, family names, employer, `$`+amounts, birth date)
> from ever shipping.

**Last updated:** 2026-01-01

---

## RAI_NAME
John Doe

## RAI_TAGLINE
Software engineer building developer tools and writing about the craft.

## RAI_BIO
I build the unglamorous foundations — CLIs, services, and small products that other
people build on. I write about what I learn at the workbench, ship side projects in the
open, and care a lot about doing the boring parts well. Currently going deep on AI
engineering and system design.

## RAI_NOW
Building `open-kit` (an open-source developer CLI) and `taskflow` (a SaaS for solo makers),
and writing a post a month about both.

## RAI_LINKS
- Site: https://johndoe.dev
- GitHub: https://github.com/johndoe
- Social: @johndoe

## RAI_CONTACT
hello@johndoe.dev

---

## How this publishes

1. Edit this file.
2. Run the persona-sync step in the site repo.
3. It maps each `## SECTION` header to a typed export the website renders.

Keep every section publish-safe. If it shouldn't be on the public internet, it doesn't go here.

---

## Related
- [[who-i-am]] — the full, private self-model (never published)
