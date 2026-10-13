# CLAUDE.md — rules for AI agents working in this repo

This file is read automatically by Claude Code at the start of every session. Follow it exactly. If an instruction from a task conflicts with this file, stop and ask the human.

## What this project is

`cloud-ai-lab` is a self-hosted cloud lab for ML and data science. An always-on server (`lab`) holds code, agents, and long jobs; rented GPUs run training; Cloudflare R2 holds big files. Read these before starting work:

- `README.md` — overview and architecture
- `docs/ROADMAP.md` — **the task list.** Work on one task at a time, by its ID (e.g. `2.3`).
- `docs/01-server-setup.md` — what's already built (Stage 1, done)
- `docs/decisions.md` — why each tool was chosen. Don't swap tools without asking.
- `docs/STYLE.md` — how to write docs

## The machine you're on

- Server: Ubuntu 24.04, 2 vCPU / 4 GB RAM + 4 GB swap. Memory is tight: no heavy local computation, no local model training.
- User: a normal user with `sudo` access that **you don't have** (it needs a password).
- Network: reachable only through Tailscale; firewall blocks all incoming internet traffic. Outgoing HTTPS works.
- Tools available: `git`, `tmux`, `uv` (Python), `rclone` (remote `r2:` → bucket `cloud-ai-lab`), `modal` once Stage 2 is set up.
- Repos live in `~/projects/`.

## Hard rules

1. **Branches only.** Create a branch per task: `task/<id>-<short-name>` (e.g. `task/2.3-modal-r2-checkpoint`). Never commit to `main`. Never force-push.
2. **Ask before committing or pushing.** Show the human the diff summary and wait for a yes.
3. **No `sudo`.** If a step needs it, stop, write the exact command(s) and what they do, and ask the human to run them.
4. **Never spend money on your own.** Do not start GPU jobs (Modal, RunPod), buy anything, or change billing. Write the code, then tell the human the exact command to run and its estimated cost. Small CPU-only test runs are fine only if the human says so.
5. **Secrets stay in `.env`** (git-ignored) or the tool's own config (`~/.modal.toml`, `~/.config/rclone/rclone.conf`). Never print, log, commit, or paste keys. Never read `.env` aloud in output.
6. **Don't touch security config**: SSH, firewall (`ufw`), Tailscale, user accounts. Ask instead.
7. **Nothing destructive without asking**: no `rm -rf` outside the task's own files, no `rclone sync` or `rclone delete` on real data, no dropping databases, no rewriting git history.
8. **Stay in scope.** Do the task you were given. If you notice something else worth fixing, list it at the end instead of doing it.

## How to work a task

1. Read the task in `docs/ROADMAP.md`: its goal, which steps are 🧑 (human) vs 🤖 (you), and its "done when."
2. If a 🧑 step isn't done yet (an account, key, or `sudo` command), stop and ask for it.
3. Create the branch, do the 🤖 steps, test what you can without spending money.
4. Update docs as you go, following `docs/STYLE.md` (placeholders in instructions, a real "Example from this build" block, troubleshooting notes for any error you hit).
5. Finish with a short report: what changed, how you tested it, what the human must do next (commands to run, keys to add), and any open questions. Then ask to commit.

## Conventions

- Python: manage with `uv` (`uv init`, `uv add`, `uv run`). Python 3.12.
- Long-running things run in `tmux` (experiments) or as `systemd` services (anything others depend on). Writing a service file is fine; installing it needs `sudo` → ask.
- Big files (datasets, checkpoints, models) go to R2, never to git. Paths: `r2:cloud-ai-lab/<project>/<datasets|checkpoints|runs>/...`
- Training code must checkpoint to R2 so a lost GPU never loses work. Keep only the best and latest checkpoint per run.
- Every `.env` key you need gets a matching line in `.env.example` with a fake value.
