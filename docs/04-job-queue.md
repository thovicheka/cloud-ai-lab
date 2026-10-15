# Stage 4 — Job queue (Prefect)

**What you'll have working by the end:** a self-hosted Prefect server and worker on the lab server, running as `systemd` services, with a web UI at `http://lab:4200` over Tailscale. GPU jobs run as Prefect flows with clear states (Scheduled, Running, Paused, Completed, Failed, Cancelled). Any flow that costs money pauses first and asks for your approval on Telegram, with a cost estimate and a link. Nothing reaches Modal until you approve it in the UI.

**Status:** ✅ done (tasks 4.1–4.4). The services, the deployments, and the approval gate's pause, decline, and approve paths all work on the real server; one approved `hello-gpu` run reached a T4 on Modal (step 9).

**How to read this guide:** instructions use placeholders like `<username>`; replace them with your own values. After key steps, an **Example from this build** block shows the real commands and output from the author's setup:

| Placeholder | In this build |
|---|---|
| `<username>` | `thovicheka` |
| `<server-name>` | `lab` (Tailscale MagicDNS name) |
| `<repo>` | `~/projects/cloud-ai-lab` (where you and agents work on branches) |
| `<runtime>` | `~/projects/lab-runtime` (the copy of `main` the services run) |
| `<pool>` | `lab` (Prefect work pool) |

**Which machine:** everything runs **on the server**, except opening the UI and approving runs, which you do in a browser on the laptop or phone (over Tailscale).

Why self-hosted Prefect and not Prefect Cloud: see [decisions.md](decisions.md#job-queue-prefect) and the full comparison in [04-job-queue-design.md](04-job-queue-design.md).

## Contents
- [How it fits together](#how-it-fits-together)
- [Prerequisites](#prerequisites)
- Steps: [1. Add Prefect](#1-add-prefect) · [2. Point the CLI at the server](#2-point-the-cli-at-the-server) · [3. Create the runtime worktree](#3-create-the-runtime-worktree) · [4. Link `.env` into it](#4-link-env-into-it) · [5. Install the services](#5-install-the-two-services) · [6. Check them](#6-check-the-services) · [7. Register deployments](#7-register-the-deployments) · [8. Run a free flow](#8-run-a-free-flow) · [9. Run a paid flow](#9-run-a-paid-flow-through-the-approval-gate) · [10. Parameters and later starts](#10-run-with-parameters-later-or-on-a-schedule) · [11. Update after a merge](#11-update-the-services-after-each-merge)
- [How the approval gate works](#how-the-approval-gate-works)
- [Limits](#limits)
- [Verify it worked](#verify-it-worked)

---

## How it fits together

```
 Laptop / phone ──(Tailscale)──► http://lab:4200  (UI: runs, Resume button)
                                       │
 lab server                            ▼
   prefect-server.service   API + UI + scheduler, runs stored in SQLite (~/.prefect/prefect.db)
   prefect-worker.service   polls work pool "lab", starts each flow run as a subprocess
        │
        └─ flow run (in ~/projects/lab-runtime)
             1. estimate cost → Telegram "⏸️ Awaiting approval, ~$X" + link
             2. Paused … you tick "approve" and Resume in the UI
             3. task: Modal app.run() + function.remote()  ──►  GPU on Modal
             4. Telegram ▶️ Started → ✅ Finished / ❌ Failed
```

- The **server** keeps the queue, the run history, and the UI. The **worker** runs flows on this box. Flows only wait on the network; the GPU work happens on Modal, so they're light (~90 MB each).
- Both services run from **`<runtime>`**, a git worktree of `main`. Agents switching branches in `<repo>` never change what the services run.
- Flows call the same Modal functions as `modal run jobs/...`, as ephemeral apps: no `modal deploy` step, and the code that runs is the code in `<runtime>`.

## Prerequisites
- [Stage 1](01-server-setup.md): Tailscale, the firewall (`ufw` allows all traffic on `tailscale0`, so port 4200 is reachable from your devices only), and `uv`.
- [Stage 2](02-gpu-compute.md): a Modal account (with a **$0 spending limit** in this build) and the jobs in `jobs/`.
- [Stage 6](06-notifications.md): `lab/notify.py` and the Telegram keys in `<repo>/.env`.
- `sudo` on the server, to install the two services.
- About 0.35 GB of free RAM (measured: server ~235 MB, worker ~80 MB idle).

---

## Steps

### 1. Add Prefect
```bash
cd ~/projects/cloud-ai-lab
uv add prefect
```
*What it does:* adds Prefect (3.8.8 in this build) to `pyproject.toml` and `uv.lock`. Prefect needs no Postgres or Redis for one user on one box; it uses SQLite.

> **Adapting:** cloning this repo? Prefect is already in `uv.lock`; run `uv sync` instead.

<details><summary>Example from this build</summary>

```console
$ uv add prefect
...
 + prefect==3.8.8
 + sqlalchemy==2.1.4
 + uvicorn==0.54.0
...
$ uv run prefect version
Version:              3.8.8
API version:          0.8.4
Python version:       3.12.3
...
Server:
  Database:           sqlite
  SQLite version:     3.45.1
```
**Result:** ✅
</details>

### 2. Point the CLI at the server
```bash
uv run prefect profile use local
uv run prefect config set PREFECT_UI_URL=http://<server-name>:4200
```
*What it does:* makes every `prefect` command on the server talk to the installed service at `http://127.0.0.1:4200/api`, and print UI links that open from your laptop. Without it, `prefect` commands start a throwaway temporary server each time.

> **If you see** `Error connecting to Prefect server using profile 'local'`, **it means** the server isn't installed yet (step 5). The profile still switched; ignore it for now.

<details><summary>Example from this build</summary>

```console
$ uv run prefect profile use local
Error connecting to Prefect server using profile 'local'     # expected: not installed yet
$ uv run prefect config set PREFECT_UI_URL=http://lab:4200
Updated profile 'local'.
$ cat ~/.prefect/profiles.toml
active = "local"
[profiles.local]
PREFECT_API_URL = "http://127.0.0.1:4200/api"
PREFECT_UI_URL = "http://lab:4200"
```
**Result:** ✅
</details>

### 3. Create the runtime worktree
```bash
git worktree add ~/projects/lab-runtime main
cd ~/projects/lab-runtime && uv sync
```
*What it does:* checks out `main` a second time in `<runtime>`, with its own `.venv`. The services run from here, so they always run merged code, whatever branch is checked out in `<repo>`.

Two rules come with it:
- `main` is now checked out in `<runtime>`, so `git switch main` in `<repo>` fails. Start task branches with `git fetch origin && git switch -c task/<id>-<name> origin/main`.
- Never edit, commit, or switch branches in `<runtime>`. Only the update routine (step 11) touches it.

> **If you see** `fatal: 'main' is already used by worktree at '.../lab-runtime'`, **it means** you tried to check out `main` in `<repo>`. That's expected; branch from `origin/main` instead.

<details><summary>Example from this build</summary>

```console
$ git worktree add ~/projects/lab-runtime main
Preparing worktree (checking out 'main')
HEAD is now at b71f207 Merge pull request #15 from thovicheka/task/4.2-prefect-setup
$ git worktree list
/home/thovicheka/projects/cloud-ai-lab  b71f207 [task/4.2-runtime-worktree]
/home/thovicheka/projects/lab-runtime   b71f207 [main]
$ cd ~/projects/lab-runtime && uv sync
...
$ .venv/bin/prefect version | head -1
Version:              3.8.8
$ du -sh .venv
341M	.venv
$ git switch main          # back in ~/projects/cloud-ai-lab
fatal: 'main' is already used by worktree at '/home/thovicheka/projects/lab-runtime'
```
**Result:** ✅ (the last error is expected)
</details>

### 4. Link `.env` into it
```bash
ln -s ~/projects/cloud-ai-lab/.env ~/projects/lab-runtime/.env
```
*What it does:* `.env` is git-ignored, so the worktree doesn't get one. `lab/notify.py` reads `.env` from the checkout it runs in, so without this, flows can't send Telegram messages. A symlink keeps one file of secrets instead of two copies.

<details><summary>Example from this build</summary>

```console
$ readlink ~/projects/lab-runtime/.env
/home/<username>/projects/cloud-ai-lab/.env
```
**Result:** ✅ (every run in step 9 sent its Telegram messages: approval request, 🚫 Declined, ▶️ Started, ✅ Finished)
</details>

### 5. Install the two services
The unit files are in `deploy/`:
- `prefect-server.service`: `prefect server start` on `0.0.0.0:4200`. The UI calls `http://lab:4200/api`, analytics are off, `MemoryHigh=500M` / `MemoryMax=700M`, restarts on failure.
- `prefect-worker.service`: a process worker on work pool `lab` (created on first start), at most **2 flow runs at once** (`--limit 2`), `MemoryHigh=700M` / `MemoryMax=900M`, always restarts.

> **Adapting:** both files hard-code `User=thovicheka` and `/home/thovicheka/projects/lab-runtime`. Change them to your user and path first.

```bash
cd ~/projects/lab-runtime
sudo cp deploy/prefect-server.service deploy/prefect-worker.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now prefect-server.service
sudo systemctl enable --now prefect-worker.service
```
*What it does:* copies both units into systemd's folder, makes systemd read them, then starts each one now and at every boot. The worker starts after the server.

<details><summary>Example from this build</summary>

```console
$ sudo cp deploy/prefect-server.service deploy/prefect-worker.service /etc/systemd/system/
$ sudo systemctl daemon-reload
$ sudo systemctl enable --now prefect-server.service
Created symlink ... → /etc/systemd/system/prefect-server.service.
$ sudo systemctl enable --now prefect-worker.service
Created symlink ... → /etc/systemd/system/prefect-worker.service.
```
**Result:** ✅

The services were first installed from `<repo>`, then moved to `<runtime>` (step 3) with a second `sudo cp` + `daemon-reload` + `restart`. Install straight from `<runtime>` and you skip that.
</details>

### 6. Check the services
```bash
systemctl status prefect-server prefect-worker --no-pager
curl -s http://127.0.0.1:4200/api/health
sudo journalctl -u prefect-worker -n 20 --no-pager
```
*What it does:* both should be `active (running)`, the API should answer `true` (give the server ~10 s after a start), and the worker log should say `Worker 'lab-worker' started!`. Reading system logs needs `sudo` unless your user is in the `adm` group.

Then *(on the laptop)* open **http://\<server-name\>:4200**. Expected: the Prefect dashboard; **Work Pools → lab** shows Status **Ready**.

> **If you see** `status=203/EXEC`, **it means** `<runtime>/.venv/bin/prefect` is missing. Run `cd ~/projects/lab-runtime && uv sync`, then `sudo systemctl restart prefect-server prefect-worker`.
>
> **If you see** the dashboard load but say it can't reach the API, **it means** the browser can't resolve `lab`. Check that `ping lab` works from the laptop (Tailscale MagicDNS).

<details><summary>Example from this build</summary>

```console
$ systemctl status prefect-server prefect-worker --no-pager
● prefect-server.service ... Active: active (running)   Memory: 229.7M (max: 700.0M)
● prefect-worker.service ... Active: active (running)   Memory: 79.1M (max: 900.0M)
$ curl -s http://127.0.0.1:4200/api/health
true
$ sudo journalctl -u prefect-worker -n 20 --no-pager
... Worker 'lab-worker' started!
$ free -h          # ~7 min after start
               total        used        free      shared  buff/cache   available
Mem:           3.7Gi       1.9Gi       197Mi       4.8Mi       1.9Gi       1.8Gi
Swap:          4.0Gi       512Ki       4.0Gi
```
On the laptop, http://lab:4200 opened; **Work Pools → lab**: Status **Ready**, Type **Process**. **Result:** ✅ ~314 MB for both services, under the design estimate of 0.4–0.8 GB.
</details>

### 7. Register the deployments
A **deployment** tells the server "this flow exists, and the worker on pool `lab` runs it from this folder". Register each flow once, **from `<runtime>`**:
```bash
cd ~/projects/lab-runtime
uv run python flows/hello.py          # hello: free smoke test, no Modal
uv run python -m flows.hello_gpu      # hello-gpu: nvidia-smi + a matmul on a T4
uv run python -m flows.train          # train-mnist: the checkpointed training template
uv run prefect deployment ls
```
*What it does:* each script calls `.from_source(<its checkout>).deploy(work_pool_name="lab")`. Nothing is uploaded; the deployment stores the folder it was registered from, and the worker reads the code there at the start of every run. So after a merge, `git pull` in `<runtime>` is enough (step 11). Register again only for a **new** flow, or after changing a flow's name or parameters.

> **If you see** a run's logs say `set_working_directory` with `.../cloud-ai-lab`, **it means** that deployment was registered from `<repo>`, so it runs whatever branch is checked out there. Register it again from `<runtime>`.

<details><summary>Example from this build</summary>

**Registered from the wrong folder first (`hello`, task 4.2):**
```console
$ uv run prefect deployment inspect hello/hello
    'pull_steps': [{'prefect.deployments.steps.set_working_directory':
                    {'directory': '/home/thovicheka/projects/cloud-ai-lab'}}],
```
**Result:** ❌ **Cause:** `from_source(<local path>)` stores the path it was registered from. **Fix:** register again from `<runtime>`:
```console
$ cd ~/projects/lab-runtime && uv run python flows/hello.py
│ hello/hello │ applied │
$ uv run prefect deployment inspect hello/hello
                'directory': '/home/thovicheka/projects/lab-runtime'
```
**Result:** ✅

**All three, after 4.3 was merged** (registered by the human from `<runtime>`):
```console
$ uv run prefect deployment ls
┃ Name                          ┃ ID                           ┃ Work Pool     ┃
│ hello/hello                   │ 09384bc5-cc1c-4521-9a22-e48… │ lab           │
│ hello-gpu/hello-gpu           │ 6c12d07c-3dc5-496d-be46-143… │ lab           │
│ train-mnist/train-mnist       │ 70c0c3d9-134c-4b7f-8c1e-12d… │ lab           │
```
**Result:** ✅
</details>

### 8. Run a free flow
```bash
uv run prefect deployment run hello/hello --watch
```
*What it does:* creates a run of `hello`; the worker picks it up within a few seconds and runs it on the server. `--watch` follows it until it ends. Free: no Modal, no GPU. Use it after any change to check the queue still works.

<details><summary>Example from this build</summary>

```console
$ uv run prefect deployment run hello/hello --watch
Created flow run 'mutant-trogon'.
└── URL: http://lab:4200/runs/flow-run/bffd5c93-...
● 16:40:27.839 prefect.flow-run.Pending * mutant-trogon
●         .883 prefect.worker.submitted-flow-run * lab-worker
●      :29.071 prefect.flow-run.pull-step.executed
●      :30.491 prefect.flow-run.Running * mutant-trogon
●         .556 prefect.flow-run.Completed * mutant-trogon
Flow run finished successfully in 'Completed'.
$ uv run prefect flow-run logs bffd5c93-...
... Executing deployment step: set_working_directory
... Hello from lab (ubuntu-4gb-sin-2, Python 3.12.3)
... Finished in state Completed()
```
**Result:** ✅ done ~4 s after creation. The worker peaked at 157 MB while running it.
</details>

### 9. Run a paid flow through the approval gate
Start a run *(on the server)*, or press **Run** on the deployment in the UI:
```bash
uv run prefect deployment run hello-gpu/hello-gpu
```
*What it does:* the run starts, estimates its cost, sends this on Telegram, then **pauses**. Nothing is spent yet:
```
⏸️ Awaiting approval, ~$0.01: hello-gpu on T4
At most $0.05 if it hits its 5 min timeout.
http://lab:4200/flow-runs/flow-run/<id>
Resume → tick approve → Submit. No answer in 24 h = not run.
```
Then *(on the laptop or phone, over Tailscale)*: open the link → **Resume** → tick **approve** → **Submit**. In the new Prefect UI, **Resume** is in the run's **⋮** menu (top right); **Switch to V1 UI** shows it as a button instead. The run continues to Modal and Telegram says ▶️ Started, then ✅ Finished (or ❌ Failed). To say no, press Resume and submit **without** ticking approve: the run ends **Cancelled** and Telegram says 🚫 Declined.

**Cost:** `hello-gpu` ~$0.01, at most $0.05. `train-mnist` with 3000 steps ~$0.02, at most $0.30 (its 30 min timeout). T4 at $0.000164/s; check Modal's current price.

> **If you see** no Telegram message, **it means** the flow couldn't read the bot token. Check `ls -l ~/projects/lab-runtime/.env` (step 4). The run still pauses; find it under **Runs** in the UI.
>
> **If you see** no **Resume** button on a paused run, **it means** you're on the new UI, which hides it. Open the **⋮** menu, or use **Switch to V1 UI**.
>
> **If you see** the run go **Failed** right after approval with `ModuleNotFoundError: No module named 'jobs'`, **it means** the Modal container didn't get the `jobs/` folder. Check that `jobs/` is a package next to `flows/` in `<runtime>`.
>
> **If you see** a traceback ending in `prefect.exceptions.CancelledRun: Declined in the UI; nothing ran on Modal` in a declined run's logs, **it means** nothing: Prefect logs the Cancelled state the flow returns as an exception. The run is Cancelled and nothing ran on Modal.

<details><summary>Example from this build</summary>

Three `hello-gpu` runs, read back from the server (state history and logs, UTC) and checked on Telegram by the human.

**Decline: `supportive-vulture`** (2026-10-15). Resumed **without** ticking approve:
```console
04:09:29 Scheduled
04:09:39 Running
04:09:40 Paused      ⏸️ Awaiting approval, ~$0.01: hello-gpu on T4 | At most $0.05 if it hits its 5 min timeout. | http://lab:4200/flow-runs/flow-run/b0065954-...
04:25:20 Running     Resuming flow run execution!
04:25:22 Declined
04:25:22 Cancelled   Declined in the UI; nothing ran on Modal
answer stored by the UI (paused-1-response): {"approve":false,"note":""}
```
Telegram: `⏸️ Awaiting approval`, then `🚫 Declined: hello-gpu. Nothing ran on Modal; $0 spent.` No Modal task on the run's timeline. **Result:** ✅ declined, $0.

**Approve: `psychedelic-velociraptor`** (2026-10-15). Resumed **with** approve ticked:
```console
$ uv run prefect flow-run logs e673c7d7-...
04:31:48 Beginning flow run 'psychedelic-velociraptor' for flow 'hello-gpu'
04:31:59 ⏸️ Awaiting approval, ~$0.01: hello-gpu on T4 | At most $0.05 if it hits its 5 min timeout. | http://lab:4200/flow-runs/flow-run/e673c7d7-... | Resume → tick approve → Submit. No answer in 24 h = not run.
04:31:59 Pausing flow, execution will continue when this flow run is resumed.
04:34:49 Resuming flow run execution!
04:34:49 Approved
04:35:04       gpu: Tesla T4
04:35:04     torch: 2.14.1+cu130
04:35:04      cuda: 13.0
04:35:04    matmul: 4096x4096
04:35:04        ms: 32.11
04:35:04    tflops: 4.28
04:35:05 Finished in state Completed()
```
State history: `04:31:35 Scheduled · 04:31:45 Pending · 04:31:48 Running · 04:31:59 Paused · 04:34:39 Running · 04:35:04 Completed`. Telegram: `▶️ Started: hello-gpu (T4)`, then `✅ Finished: hello-gpu in 0m 14s, ~$0.00 on T4` / `Tesla T4: 4.28 TFLOPS`. **Result:** ✅ Modal was called only after approval; ~15 s on a T4, ~$0.00 of free credit.

**Older paused run: `sophisticated-elk`** (2026-10-14). Resumed without approve as well, so it ended `CANCELLED` (`Declined in the UI; nothing ran on Modal`), $0.

> **Lesson from this build:** the first attempt at an approved run was really a decline: the UI stored `{"approve":false}`. The new UI hides **Resume** in the ⋮ menu, so the form is easy to submit without the box ticked. Read the stored answer (`paused-1-response`) when a run is Cancelled and you expected it to run.

Both declined runs also logged a `CancelledRun` traceback after the Cancelled state; it's harmless (see the note above).
</details>

### 10. Run with parameters, later, or on a schedule
Parameters, with `--param` (repeat it for each one):
```bash
uv run prefect deployment run train-mnist/train-mnist --param run_name=flow-1 --param steps=3000
```
Start later, with `--start-in` (or `--start-at` for a clock time):
```bash
uv run prefect deployment run train-mnist/train-mnist --param run_name=night-1 --start-in "in 2 hours"
uv run prefect deployment run train-mnist/train-mnist --param run_name=night-1 --start-at "at 23:00"
```
Every night, with a schedule on the deployment:
```bash
uv run prefect deployment schedule create train-mnist/train-mnist --cron "0 23 * * *" --timezone Asia/Phnom_Penh
uv run prefect deployment schedule ls train-mnist/train-mnist
```
*What it does:* a later or scheduled run waits as **Scheduled**, then starts on time. **A paid flow still pauses for approval when it starts**, so a 23:00 run waits until you approve it (up to 24 h). Schedule paid flows for a time you'll be around, or approve in the morning.

`train-mnist` parameters: `run_name` (required; the same name resumes from its R2 checkpoint, a new name starts fresh), `steps` (default 3000), `ckpt_every` (default 500). In the UI: **Deployments → train-mnist → Run → Custom run**.

> **If you see** the scheduled run stay **Late**, **it means** the worker isn't running. Check step 6.

`--start-in`, `--start-at`, and schedules weren't tried in this build; the flags are from Prefect 3.8.8's CLI.

### 11. Update the services after each merge
```bash
cd ~/projects/lab-runtime && git pull && uv sync && sudo systemctl restart prefect-server prefect-worker
```
*What it does:* brings `<runtime>` to the latest `main`, matches its `.venv` to `uv.lock`, and restarts both services. If a merge only changed flow code (no new packages), `git pull` alone is enough: deployments read the code at each run.

Then, only for a **new** flow, register it from `<runtime>` (step 7).

> **If you see** `git pull` say `Not possible to fast-forward`, **it means** someone committed in `<runtime>`. Stop and look before resetting anything; it should only ever follow `main`.

<details><summary>Example from this build</summary>

After 4.3 was merged (flows only, no new packages):
```console
$ cd ~/projects/lab-runtime && git pull
...
$ git log --oneline -1
7a610fb Merge pull request #18 from thovicheka/task/4.3-flows
```
**Result:** ✅ no `uv sync` or restart needed.
</details>

---

## How the approval gate works

The gate is in `flows/approval.py`. Every flow that calls a paid Modal function calls `ask_approval()` first:

| What happens | State | Telegram | Modal |
|---|---|---|---|
| Run starts, sends the estimate, waits | **Paused** | ⏸️ Awaiting approval, ~$X | not called |
| You tick **approve** and Resume | Running → **Completed** / **Failed** | ▶️ Started → ✅ Finished / ❌ Failed | called once |
| You Resume **without** ticking approve | **Cancelled** | 🚫 Declined | not called |
| No answer in 24 h | **Failed** | ⌛ Not approved within 24 h | not called |

- `approve` is unticked by default, so pressing Resume without looking declines. The **note** field is optional and shows in the Telegram reply.
- **Paid steps never retry**: the Modal task, the flow, and the Modal function all have `retries=0`. A failed training run is re-run by hand with the same `run_name`; it resumes from its R2 checkpoint and asks for approval again.
- **Telegram sends retry** twice, 10 s apart. If Telegram is still down, the flow logs a warning and carries on: the run still pauses and waits.
- Each flow states its expected and worst-case seconds next to its code (`EXPECTED_SECONDS` / `MAX_SECONDS`). `MAX_SECONDS` must match the `timeout=` of the Modal function in `jobs/`, by hand.
- Tested without spending money: `tests/test_flows.py` runs 11 tests on a throwaway Prefect server with Modal and Telegram faked (any real Modal call fails the test).

**To add a paid flow:** copy `flows/hello_gpu.py`, change the import, the estimate, and the `.remote()` call, then register it from `<runtime>` after the merge.

## Limits

- **Paused runs hold worker slots.** A paused run keeps its process alive (~90 MB) and uses one of the worker's 2 slots (`--limit 2`) for up to 24 h. Two runs waiting for approval block every other flow, including `hello`. Answer or cancel paused runs; if this gets in the way, raise `--limit` in `deploy/prefect-worker.service` or switch the gate to `suspend_flow_run` ([design §5](04-job-queue-design.md#5-how-a-paid-gpu-flow-waits-for-approval)).
- **The gate is enforced by the flow, not by Modal.** Anything with shell access on the server can resume a run through the Prefect API, or call Modal directly. For Claude Code, `.claude/settings.json` denies the resume and run-deployment commands (`prefect`, `uv run prefect`, and `.venv/bin/prefect` forms) and globs for the Python and REST names (`resume_flow_run`, `run_deployment`, `/flow_runs/*/resume`). Side effect: an agent's command that only *mentions* those phrases (in an `echo` or a commit message) is blocked too. Which credentials each agent gets is task 5.1.
- **The UI has no login.** Anyone on your tailnet can open it and press Resume. Fine while the tailnet is only your devices; Prefect's `PREFECT_SERVER_API_AUTH_STRING` (basic auth) is an option later.
- **Modal's spending limit is the hard stop.** With a **$0** limit, as in this build, a job that gets past the gate still can't spend more than the monthly free credit. Keep a limit set however the gate changes.

## Verify it worked
```bash
systemctl is-active prefect-server prefect-worker
curl -s http://127.0.0.1:4200/api/health
uv run prefect deployment ls
uv run prefect flow-run ls --limit 5
```
Expected: `active` twice, `true`, the three deployments from step 7 on pool `lab`, and your recent runs with their states (`COMPLETED` for `hello` and an approved `hello-gpu`, `CANCELLED` for a declined one). Set `COLUMNS=200` if the table is truncated.

<details><summary>Example from this build</summary>

2026-10-15, after the approved run:
```console
$ systemctl is-active prefect-server prefect-worker
active
active
$ curl -s http://127.0.0.1:4200/api/health
true
$ COLUMNS=200 uv run prefect flow-run ls --limit 6
│ e673c7d7-... │ hello-gpu │ psychedelic-velociraptor │ COMPLETED │ 2 minutes ago  │
│ 1dc4dad0-... │ hello     │ energetic-dormouse       │ COMPLETED │ 1 minute ago   │
│ b0065954-... │ hello-gpu │ supportive-vulture       │ CANCELLED │ 11 minutes ago │
│ ac67ec1d-... │ hello-gpu │ sophisticated-elk        │ CANCELLED │ 11 hours ago   │
│ e3fc86d3-... │ hello     │ slick-swallow            │ COMPLETED │ 11 hours ago   │
│ bffd5c93-... │ hello     │ mutant-trogon            │ COMPLETED │ 11 hours ago   │
```
(`COLUMNS=200` stops the CLI from truncating the columns.) The deployments are listed in step 7. **Result:** ✅ the services, the queue, the free flow, and the gate's approve and decline paths all work on the real server. The 24 h timeout is covered by `tests/test_flows.py` only.
</details>
