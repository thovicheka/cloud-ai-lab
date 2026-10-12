# Documentation Style Guide

How every doc in this repo is written, so they all read the same way: clear, consistent, and usable by someone who isn't the author.

---

## 1. The README is the front door

Within about 30 seconds, a reader should be able to:
- understand what the project is and who it's for,
- see the architecture diagram,
- jump to the stage they need.

Keep it short. Detail belongs in the stage docs.

## 2. Every stage doc has the same shape

Use this order, every time:

1. **What you'll have working by the end** — one or two sentences stating the goal.
2. **Prerequisites** — what must already be done or installed (link earlier stages).
3. **Steps** — numbered, each with real copy-paste commands and a one-line "what this does."
4. **Verify it worked** — a short check with the exact output to expect.

Throughout the steps, add **troubleshooting notes** wherever a step commonly breaks:

> **If you see** `Permission denied (publickey)`, **it means** the server doesn't have your public key yet. Run step B4.

Copy-ready template:

````markdown
# Stage N — <Title>

**What you'll have working by the end:** <goal>

## Prerequisites
- <stage or tool>

## Steps

### 1. <Action>
```bash
<command>
```
*What it does:* <one line>

> **If you see** `<error>`, **it means** <cause>. <fix>.

## Verify it worked
```bash
<check command>
```
Expected: `<output>`
````

## 3. Keep the "why" separate from the "how"

- Stage docs say **how**. Keep them clean and skimmable.
- Reasoning, trade-offs, and rejected alternatives go in [`decisions.md`](decisions.md).
- If a step needs context, link to the matching section in `decisions.md` instead of explaining inline.

## 4. Write for someone who isn't you

- Spell out what felt obvious in the moment: how long a command takes, what a scary-looking prompt means, which window to run it in (laptop vs server).
- Add **adaptation notes** so the docs work as a template, not a copy of one setup:

> **Adapting:** using DigitalOcean instead of Hetzner? Everything after server creation is identical.

- Say which machine each command runs on when it isn't obvious: *(on your laptop)* / *(on the server)*.

## 5. Placeholders, never secrets

- Use placeholders for anything personal or sensitive: `<server-ip>`, `<username>`, `<github-username>`, `<bucket-name>`.
- Never commit API keys, tokens, passwords, or real IPs. Show masked values if needed: `ANTHROPIC_API_KEY=sk-ant-***`.
- Secrets live in `.env` (git-ignored) on the server only.

## 6. Document right after finishing a stage

- Write or update a stage doc as soon as the stage works, while the errors are fresh.
- Real mistakes make the best troubleshooting notes. Include them.
- Tick checklist items only after they've actually been done and verified.

---

## Small conventions

- Commands in fenced code blocks with a language (`bash`, `yaml`, …), one action per block where possible.
- Headings in sentence case; file names numbered by stage (`01-server-setup.md`, `02-storage-r2.md`, …).
- Screenshots only for web-console steps (e.g. creating a server or bucket), saved in `docs/images/`. Never screenshot terminal commands; write them as text so they can be copied.
- Prices and versions change: date them or say "check the provider's current price."
