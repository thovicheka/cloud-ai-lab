# Roadmap

The task list for building the rest of the lab. Each task has an ID, a goal, steps marked **🧑 human** or **🤖 agent**, and a **done when** check.

**How to use it:** give an agent one task at a time — *"Read CLAUDE.md and docs/ROADMAP.md, then do task 2.2 on a new branch."* The agent stops when it reaches a 🧑 step and tells you exactly what to do. Tick tasks here when they're merged.

**Who does what, always:** 🧑 accounts, payments, API keys, `sudo`, starting paid GPU jobs, merging to `main`. 🤖 code, config files, tests, docs.

**Suggested order:** Stage A → 2 → 3 → 6 → 4 → 5. (A is the first real project on the lab; 2–3 are the ML core; 6 is a quick win; 4–5 use everything else.)

**Orchestration today:** none yet — **the human is the orchestrator**, running one Claude Code session (in `tmux`) and assigning tasks. Two or three sessions can run in parallel later, each in its own `tmux` window and branch. Automated orchestration is Stage 5.

---

## Stage 0 — Agent on the server

- [x] **0.1 Install Claude Code on `lab`** — 🧑
  - 🧑 `curl -fsSL https://claude.ai/install.sh | bash`, then `source ~/.bashrc`, `claude --version`
  - 🧑 `tmux new -s claude` → `cd ~/projects/cloud-ai-lab` → `claude` → log in with the **Claude subscription** (not an API key); open the printed link on the laptop, paste the code back
  - **Done when:** Claude Code's prompt is running inside `tmux` on the server.

- [x] **0.2 Document Stage 0** — 🤖
  - 🤖 Add the install/login steps (with troubleshooting) to `docs/00-agent-setup.md`, following STYLE.md.
  - **Done when:** the doc exists on a branch, ready for review.

---

## Stage A — Deploy AI News (first real project on the lab)

Separate repo: `~/projects/ai-news` (its own GitHub repo and its own `CLAUDE.md`). Goal: fetches and summarizes news every morning, serves a **public** website, and runs a Telegram bot — 24/7, no laptop needed.

- [ ] **A.1 Bring the repo to the server** — 🧑
  - 🧑 Push the project to GitHub (project account) if it isn't there; `git clone` it into `~/projects/ai-news`.
  - **Done when:** the code is on the server.

- [ ] **A.2 Audit and plan** — 🤖
  - 🤖 Read the code; list its stack, entry points (fetcher, summarizer, website, bot), dependencies, required env vars, and anything tied to the old laptop (paths, local files).
  - 🤖 Write `ai-news/CLAUDE.md` (copy the hard rules from this repo) and a short deployment plan.
  - **Done when:** a written plan exists and the human agrees with it.

- [ ] **A.3 Environment and secrets** — 🤖 + 🧑
  - 🤖 Set up the `uv` environment; create `.env.example` listing every key with fake values.
  - 🧑 Create `.env` with real values (LLM API key with a **monthly spend limit**, Telegram bot token, etc.).
  - **Done when:** every part starts manually without errors.

- [ ] **A.4 Daily schedule** — 🤖 + 🧑
  - 🤖 Write a `systemd` timer (or cron entry) that runs the fetch-and-summarize job each morning (Asia/Phnom_Penh time), with logging.
  - 🧑 Install it (`sudo`).
  - **Done when:** a test run triggers on schedule and its log shows success.

- [ ] **A.5 Website and bot as services** — 🤖 + 🧑
  - 🤖 Write `systemd` service files for the website and the bot (auto-restart, start on boot, logs). Website listens on `0.0.0.0:<port>`.
  - 🧑 Install and start them (`sudo`).
  - **Done when:** `http://lab:<port>` opens from the laptop, the bot answers, and both survive `sudo reboot`.

- [ ] **A.6 Make the website public** — 🧑 + 🤖
  - 🧑 Buy a domain and add it to Cloudflare (or decide on Tailscale Funnel instead — no domain, `*.ts.net` URL).
  - 🧑 `cloudflared` login (needs a browser).
  - 🤖 Write the tunnel config and its `systemd` service; 🧑 install it.
  - **The firewall stays closed** — the tunnel is outgoing only.
  - **Done when:** the site opens on a phone **off Tailscale**, at the public URL.

- [ ] **A.7 Hardening and docs** — 🤖
  - 🤖 Check the public site exposes nothing private (no admin pages, debug mode off, no secrets in pages or logs). Add basic rate limiting if there are any AI-backed per-user features.
  - 🤖 Write `ai-news/docs/deploy.md` (STYLE.md format) and a short entry here.
  - **Done when:** checks pass and docs are on a branch.

---

## Stage 2 — GPU compute (Modal)

- [x] **2.1 Modal account and limits** — 🧑
  - 🧑 Sign up with the project GitHub account; **set a monthly spending limit**; `uv tool install modal --with python-dotenv` (`modal secret create --from-dotenv` needs it); `modal token new`.
  - **Done when:** `modal token new` reports success on the server.

- [x] **2.2 Hello-GPU job** — 🤖 (🧑 runs it)
  - 🤖 Write `jobs/hello_gpu.py`: a Modal function on the cheapest GPU that prints `nvidia-smi` and a tiny PyTorch matmul. Estimate the cost.
  - 🧑 Run `modal run jobs/hello_gpu.py`.
  - **Done when:** output shows the GPU name and the job stops by itself.

- [x] **2.3 R2 from Modal** — 🤖 + 🧑
  - 🧑 Store the R2 keys as a Modal secret (`modal secret create r2 ...`).
  - 🤖 Shared helper `lab/storage.py` (upload/download/list with `boto3`, paths per CLAUDE.md conventions); a job that writes a file to R2.
  - **Done when:** the file appears in `r2:cloud-ai-lab/...`.

- [x] **2.4 Checkpointed training template** — 🤖 (🧑 runs it)
  - 🤖 `jobs/train_template.py`: small model (e.g. MNIST), checkpoints to R2 every N steps, keeps best + latest only, **resumes from the latest checkpoint** if restarted.
  - 🧑 Run it, stop it mid-way, run again.
  - **Done when:** the second run resumes instead of starting over.

- [x] **2.5 Document Stage 2** — 🤖 → `docs/02-gpu-compute.md`

---

## Stage 3 — Experiment tracking (Weights & Biases)

- [x] **3.1 W&B account** — 🧑 Sign up; store the API key as a Modal secret and in `.env`.
- [ ] **3.2 Log the template** — 🤖 Add W&B to `train_template.py`: config, metrics, sample images/audio, link to the R2 checkpoint path. **Done when:** a run shows charts on wandb.ai.
- [ ] **3.3 Document Stage 3** — 🤖 → `docs/03-experiment-tracking.md`

---

## Stage 6 — Notifications (Telegram)

(Separate from the AI News bot.)

- [x] **6.1 Bot token** — 🧑 Create a bot with @BotFather; put the token and your chat ID in `.env`.
- [x] **6.2 Notifier** — 🤖 `lab/notify.py`: `notify(text)` sends a message; call it on job start / finish / failure in the templates (with duration and estimated cost). **Done when:** a test job sends all three messages.
- [x] **6.3 Document** — 🤖 → `docs/06-notifications.md`

---

## Stage 4 — Job queue (Prefect)

- [x] **4.1 Design** — 🤖 Propose: self-hosted Prefect server vs Prefect Cloud free tier, memory use on a 4 GB box, how flows call Modal. 🧑 Pick one. → **Picked: self-hosted** ([design](04-job-queue-design.md))
- [ ] **4.2 Set up** — 🤖 config + service files; 🧑 install (`sudo`).
- [ ] **4.3 Wrap jobs** — 🤖 Prefect flows around the Modal jobs with states (queued / running / completed / failed / awaiting approval), retries, and `notify()` calls. Paid GPU flows require 🧑 approval before running.
- [ ] **4.4 Document** — 🤖 → `docs/04-job-queue.md`

---

## Stage 5 — Agents

- [ ] **5.1 Rules per role** — 🤖 draft, 🧑 approve: which tools and permissions each agent gets (coordinator, coding, professor). Permissions come from tools granted, not prompts.
- [ ] **5.2 Professor agent** — 🧑 API key with a spend limit. 🤖 Script: pull a W&B run's metrics and plots → send to Claude with a "you're my professor" prompt → written analysis. **Done when:** it explains a real run.
- [ ] **5.3 Coordinator** — 🤖 Loop with tools `create_task`, `list_tasks`, `run_coding_agent` (headless Claude Code on its own branch/worktree), `read_result`. Cost guard: hard cap on calls per task. **Done when:** it completes a small doc task end to end on a branch.
- [ ] **5.4 Document** — 🤖 → `docs/05-agents.md`

---

## Done

- [x] **Stage 1 — Server, access, dev tools, storage** → [01-server-setup.md](01-server-setup.md)
