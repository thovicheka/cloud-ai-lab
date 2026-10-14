# Stage 4 design — Prefect: self-hosted server or Prefect Cloud?

**What this decides:** where the Prefect server lives for the job queue (task 4.1). Both options run the same flow code on `lab` and call the same Modal jobs; they differ in what runs on the 4 GB box, who holds the run history, and what needs an account or `sudo`. **🧑 Pick one**; task 4.2 sets it up.

**Picked (🧑, 2026-10-14): A, self-hosted Prefect server**, as recommended (details in [Recommendation](#6-recommendation)). Nothing was installed and no account was created for this doc.

Facts checked on 2026-10-14 against prefect.io/pricing, docs.prefect.io, and PyPI (latest `prefect` is **3.8.8**, released 2026-10-06, Python 3.10–3.14). Prices and limits change; check them again before deciding.

## Contents
1. [The two options](#1-the-two-options)
2. [Side by side](#2-side-by-side)
3. [Memory on this box](#3-memory-on-this-box)
4. [How flows call Modal](#4-how-flows-call-modal)
5. [How a paid GPU flow waits for approval](#5-how-a-paid-gpu-flow-waits-for-approval)
6. [Recommendation](#6-recommendation)
7. [What happens after you pick](#7-what-happens-after-you-pick)

---

## 1. The two options

Prefect has two parts: a **server** (API, database of runs, web UI, scheduler) and a **runner** (the process that actually executes flow code). The runner always lives where the code and `.env` are: on `lab`. The question is only where the server lives.

**A. Self-hosted Prefect server (open source, Apache 2.0)**
- `prefect server start` on `lab`: one Python process with the API, UI, and background services, storing runs in SQLite at `~/.prefect/prefect.db`. No Postgres or Redis needed for one user on one box.
- UI at `http://lab:4200`, reachable from any of your Tailscale devices.
- Plus the runner: a second long-lived process (`flow.serve(...)`) that picks up runs.

**B. Prefect Cloud, free "Hobby" tier**
- Prefect hosts the server and UI at `app.prefect.cloud`.
- On `lab`: only the runner, logged in with a Prefect Cloud API key.
- Hobby limits (prefect.io/pricing, 2026-10-14): **2 users, 1 workspace, 5 deployments, 7-day run retention, 5 automations, 625 API calls/min**, 500 min/month of Prefect's own serverless compute. Not included: custom work pools, webhooks, service accounts. Next tier up: Starter, $100/month.

## 2. Side by side

| | A. Self-hosted server | B. Prefect Cloud Hobby |
|---|---|---|
| **Memory on `lab`** | server + runner: **~400–800 MB** (estimate, see §3) | runner only: **~150–300 MB** (estimate) |
| **Cost** | $0 (runs on the server you already pay for) | $0 on Hobby; $100/month if the limits bind |
| **Needs `sudo`** | Install 2 systemd services (server, runner) | Install 1 systemd service (runner) |
| **Needs an account** | No | Yes: Prefect Cloud account + API key on `lab` |
| **Firewall / network** | No change: `ufw` already allows all traffic on `tailscale0`, so port 4200 is reachable over Tailscale and blocked from the internet | No change: the runner only makes outgoing HTTPS calls |
| **UI from phone** | Phone needs the Tailscale app | Any browser, anywhere (Prefect login) |
| **Run history** | Kept forever on `lab` (clean up by hand if it grows) | 7 days, then gone |
| **Deployments** | Unlimited | 5 (hello-gpu, r2-hello, and training flows count toward it) |
| **Where run data lives** | On `lab` only | Flow names, parameters, and logs on Prefect's servers |
| **Upkeep** | You upgrade Prefect and run DB migrations; if `lab` is down, so is the UI | Prefect runs the server; you upgrade only the client |
| **Approval gate** (§5) | `pause_flow_run` + Resume button: works | Same: works |
| **Calling Modal** (§4) | Flow on `lab` calls Modal: works | Same; plus the Cloud-only Modal push pool, which doesn't fit our design |
| **Switching later** | Point `PREFECT_API_URL` at Cloud; flow code is unchanged | Point it at the self-hosted server; unchanged |

## 3. Memory on this box

**Now** (2026-10-14, nothing Prefect running): 3.8 GB RAM, 1.66 GB used, **2.15 GB available**, 4 GB swap unused. The biggest users are the PyCharm remote IDE backend (~1.2 GB, only while the IDE is connected) and Claude Code (~0.4 GB).

**Estimates, not measured** (installing to measure was out of scope; Prefect publishes no RAM figure):
- Prefect server (FastAPI + UI + background services + SQLite): roughly **250–500 MB** resident.
- Runner (`flow.serve`): roughly **150–300 MB**, a bit more while a flow imports `modal` and waits on a GPU job. The heavy work (PyTorch, data) stays on Modal; the runner only waits on the network.

So option A adds ~0.4–0.8 GB and option B ~0.15–0.3 GB. Both fit inside the 2.15 GB available, with swap as a buffer. The tight moment for A is IDE connected + Claude Code + Prefect + a flow running at once: about 3 GB of 3.8 GB.

Guards for either option:
- Task 4.2 measures real usage (`ps -o rss`) after a day and after a week, and records it.
- Set `MemoryMax=` in each systemd unit, so a leak gets the Prefect service restarted instead of the box swapping. (Prefect fixed one such leak in its in-memory messaging, PR #19136; use a current release.)
- Ubuntu 24.04's SQLite is 3.45.1 (checked in both the system Python and the `uv` Python 3.12), well above Prefect's minimum.

## 4. How flows call Modal

The Stage 2 design stays: **the orchestration runs on `lab`, the GPU function runs on Modal** (see [decisions.md › Stage 2 job design](decisions.md#stage-2-job-design)). `.env`, Telegram, and the approval wait stay on the server; Modal only holds the `r2` and `wandb` secrets.

A Prefect task replaces `modal run`'s local entrypoint and calls the same Modal function from Python:

```python
# flows/train.py (sketch for task 4.3, not written yet)
import modal
from prefect import flow, task

from jobs.train_template import app, train, GPU, PROJECT
from lab.notify import notify_job


@task(retries=0)  # paid step: a failure stops; a human decides to re-run (it resumes)
def run_on_modal(run_name: str, steps: int) -> dict:
    with notify_job(f"train {PROJECT} {run_name}", gpu=GPU):
        with modal.enable_output(), app.run():  # same as `modal run`, from Python
            return train.remote(run_name=run_name, steps=steps)
```

Two ways to reach the Modal function; both work with either Prefect option:

| | Ephemeral app: `with app.run(): train.remote(...)` | Deployed app: `modal.Function.from_name("train-template", "train").remote(...)` |
|---|---|---|
| Setup | None; same as today's `modal run` | 🧑 `modal deploy jobs/train_template.py` after each change (agents are denied `modal deploy`) |
| Start-up | Builds/looks up the image each run (cached after the first) | Slightly faster |
| Code that runs | The code on `lab` at that moment | The last deployed version |

**Proposed: ephemeral apps.** No extra deploy step, and the code that runs is the code in the branch you checked out.

**Retries:** Modal functions keep `retries=0`. Prefect task retries are for free steps only (e.g. a Telegram call); paid tasks get `retries=0`, because the training job resumes from its checkpoint and a human decides whether to pay for another try.

**Not proposed: Prefect Cloud's Modal push work pool** (`--type modal:push`). It's Cloud-only and runs the *whole flow* inside a Modal container, pulling code from GitHub `main`. That moves the approval wait, Telegram, and `.env` onto Modal, contrary to the Stage 2 design, and Hobby's "no custom work pools" may exclude it anyway.

## 5. How a paid GPU flow waits for approval

Prefect has a built-in state for this: **Paused**. The flow estimates the cost, sends a Telegram message, then calls `pause_flow_run` and blocks until you press **Resume** in the UI (or the timeout passes):

```python
from prefect import flow
from prefect.flow_runs import pause_flow_run
from prefect.input import RunInput
from prefect.runtime import flow_run

from lab.notify import notify, estimate_cost


class Approval(RunInput):
    approve: bool  # the Resume form shows this as a checkbox
    note: str = ""


@flow(name="train")
def train_flow(run_name: str, steps: int = 3000):
    est = estimate_cost(seconds=120, gpu="T4")  # task 4.3 replaces this with a real per-job estimate
    notify(f"⏸️ Awaiting approval: train {run_name}, ~${est:.2f} on T4\n<prefect-ui>/runs/flow-run/{flow_run.id}")
    answer = pause_flow_run(wait_for_input=Approval, timeout=24 * 3600)  # default is 1 h
    if not answer.approve:
        notify(f"🚫 Declined: train {run_name}")
        return
    return run_on_modal(run_name, steps)
```

How it plays out:
- **Queued → Paused:** the flow starts (scheduled, triggered by you, or later by an agent), sends `⏸️ Awaiting approval` with the cost and a link, then pauses. Nothing has been spent.
- **You approve:** open the link → **Resume** → tick `approve` → submit. The flow continues to Modal. `▶️ Started`, then `✅ Finished` or `❌ Failed`, as today.
- **You decline:** untick `approve`; the flow ends without calling Modal.
- **You do nothing:** after 24 h the run becomes **Failed** (timeout) and Telegram says so; no GPU is touched.

**`pause_flow_run` vs `suspend_flow_run`:** pause keeps the flow process alive on `lab` while waiting (a few MB; free, since it's our own box; default timeout 1 h). Suspend exits the process and re-runs the flow from the start on resume (no default timeout; needs a deployment). **Proposed: pause**, for simplicity: only a few runs wait at once here. Revisit if many runs queue up.

The same Paused / Resume flow works on both options. The difference is reach: on A the link is `http://lab:4200/...` and needs Tailscale on the device; on B it's `app.prefect.cloud/...` and works from any browser after a Prefect login.

**Limits of the gate (for task 5.1):** the gate is enforced by the flow, not by Modal. Anything with shell access on `lab` can call `resume_flow_run` through the Prefect API, or run `modal run` directly (Claude Code's `.claude/settings.json` already denies `modal run`). The hard backstop stays Modal's **$0 spending limit**. 4.3 should add a deny rule for Prefect's resume command; 5.1 decides which credentials agents get.

## 6. Recommendation

**Self-hosted Prefect server (option A).**

1. **It fits.** ~0.4–0.8 GB estimated against 2.15 GB available, with a `MemoryMax` guard and swap. Real numbers come from 4.2.
2. **No new account, no new key, no data leaves the box.** Fits the lab's "secrets stay on the server" rule with nothing to add to `.env`.
3. **No artificial limits.** Hobby's 5 deployments would bind as soon as a few projects have their own training flows, and 7-day retention drops history you might compare against later (W&B and Telegram keep their own record either way).
4. **Cloud's main extra, the Modal push pool, doesn't fit our design** (§4).
5. **No firewall or Tailscale change:** port 4200 is already reachable over Tailscale only.
6. **Low lock-in:** flow code is identical on both; moving to Cloud later is a `PREFECT_API_URL` change and a login.

**Costs of this choice:** you upgrade Prefect yourself; the UI is down if `lab` is down (so are the jobs, so little is lost); approving from the phone needs the Tailscale app.

**Pick Cloud Hobby instead if:** you want to approve from a phone without Tailscale, or 4.2's measurement shows the server staying above ~800 MB.

## 7. What happens after you pick

Task 4.2 (agent, then you):
- 🤖 add `prefect` with `uv`, write `deploy/prefect-server.service` (A only) and `deploy/prefect-runner.service` with `MemoryMax=`, add `PREFECT_*` settings to `.env.example` (B: `PREFECT_API_KEY=pnu_***`), and record the choice in `decisions.md`.
- 🧑 A: `sudo cp`, `systemctl enable --now` for the two services (exact commands come with 4.2). B: create the Prefect Cloud account, `prefect cloud login`, then the same `sudo` steps for the one runner service.

Task 4.3 then writes the flows above for `hello_gpu`, `r2_hello`, and `train_template`.

<details><summary>Example from this build</summary>

How the numbers in this doc were gathered (all read-only; nothing installed):

**1. Memory now**
```console
$ free -m
               total        used        free      shared  buff/cache   available
Mem:            3814        1661         429           4        2008        2153
Swap:           4095           0        4095
$ ps -eo rss,comm --sort=-rss | head -4
  RSS COMMAND
1188024 remote-dev-serv
406112 claude
85284 jetbrainsd
```
**Result:** ✅ 2.15 GB available; the IDE backend (`remote-dev-serv`) is the largest user.

**2. Latest Prefect release**
```console
$ curl -s https://pypi.org/pypi/prefect/json | python3 -c "..."   # version, requires_python, upload time
3.8.8 <3.15,>=3.10
2026-10-06T16:57:05
```
**Result:** ✅ Prefect 3.8.8 supports the lab's Python 3.12.

**3. SQLite version** (Prefect's default database)
```console
$ uv run python -c "import sqlite3,sys;print(sys.version.split()[0], 'sqlite', sqlite3.sqlite_version)"
3.12.3 sqlite 3.45.1
```
**Result:** ✅

**4. Firewall: is port 4200 reachable over Tailscale without a change?** From `docs/01-server-setup.md`, the rules set in Stage 1:
```console
$ sudo ufw status
Anywhere on tailscale0      ALLOW       Anywhere
Anywhere (v6) on tailscale0 ALLOW       Anywhere (v6)
```
**Result:** ✅ all ports are open on `tailscale0` and closed to the internet, so no `ufw` change is needed.

**5. Running services:** `systemctl list-units --type=service --state=running` shows no Prefect, Postgres, or Docker. **Result:** ✅ nothing to conflict with.

**6. Prefect facts** (read 2026-10-14):
- prefect.io/pricing: Hobby limits as in §1.
- docs.prefect.io `prefect.flow_runs`: `pause_flow_run(wait_for_input=None, timeout=3600, poll_interval=10, key=None)` fails the run if not resumed in time; `suspend_flow_run(..., timeout=None)` waits indefinitely by default.
- docs.prefect.io work pools: the Modal push pool appears only under Prefect Cloud; its guide pulls flow code from GitHub.
- No official RAM figure for `prefect server start` was found, hence the estimates in §3.

**Result:** ✅
</details>
