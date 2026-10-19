# Status

Live progress for agent work. The agent updates this after every step and pushes it (see "Working unattended" in [`CLAUDE.md`](../CLAUDE.md)). Task definitions live in [`ROADMAP.md`](ROADMAP.md).

## Summary

**2026-10-19: approval wording fix (branch `task/approval-switch-wording`, from `origin/main` at 8db3aa7).** The Prefect UI shows `approve` as a **switch**, not a checkbox, and "tick approve" in the ⏸️ message led to two accidental declines in the khmer-speaker-anonymization project (`sage-oxpecker`, `impartial-hawk`: stored answer `{"approve":false}`, $0 spent). The ⏸️ message now says "Resume → turn the approve switch ON → Submit"; the docstrings in `flows/approval.py`, `flows/hello_gpu.py`, `flows/train.py` match. `lab.notify.estimate_cost`'s docstring no longer says CPU and memory are "a few % extra": with 4 cores + 16 GiB on a T4 they add about 54%. Text only, no behaviour change; 48 tests ✅. No money spent. **Human must:** review and merge, then `git -C ~/projects/lab-runtime pull` on the server (the workers read the checkout at each run start).

**Run of 2026-10-15 (second): 4.3 recorded and ticked, 4.4 done (branch `task/4.4-document-stage-4`, from `origin/main` at 7a610fb). Stopping here.** The human's test runs all passed. Decline: `supportive-vulture` was resumed without approve → 🚫 Declined, **Cancelled**, no Modal call, $0. Approve: `psychedelic-velociraptor` → ▶️ Started, `✅ Finished: hello-gpu in 0m 14s, ~$0.00 on T4`, Tesla T4 4.28 TFLOPS, **Completed**. The older `sophisticated-elk` is **Cancelled**. All three deployments are on pool `lab`. `docs/04-job-queue.md` now has these runs in step 9, plus where the new UI hides **Resume** (the ⋮ menu, or **Switch to V1 UI**). Status ✅. README row ✅ and status line updated; ROADMAP 4.3 and 4.4 ticked. **Stage 4 is complete** once this is merged. The agent spent no money; it only read the Prefect API (`flow-run ls`, `flow-run logs`, state history). **Human must:** review and merge `task/4.4-document-stage-4`. Nothing else.

**Run of 2026-10-15 (first): 4.3 test run recorded (not passed yet), 4.4 written (branch `task/4.4-document-stage-4`, from `origin/main` at 7a610fb). Stopping here.** The server shows **no approved `hello-gpu` run yet**. `supportive-vulture` was resumed at 04:25 UTC, but the answer the UI stored is `{"approve":false}`. So the flow declined it: **Cancelled**, 🚫 on Telegram, nothing ran on Modal, $0. `sophisticated-elk` (2026-10-14) was the same. The gate's pause and decline paths are proven on the real server; the approved path isn't. So **4.3 and 4.4 stay unticked**. `docs/04-job-queue.md` is written (all 11 steps, the gate, the limits) with real output, except the approved-run example. The README row and status line say Stage 4 is almost done. No money spent; the agent only read the Prefect API. **Human must:** start one more `hello-gpu` run and make sure **approve** is ticked (a checkmark, not just the field) before **Submit** (~$0.01, at most $0.05). If it's still Cancelled, see "If approve was ticked" under 4.3. Then paste the result; the agent records it and ticks 4.3 and 4.4. *(Superseded by the second run above: `supportive-vulture` was the deliberate decline test, and the approved run passed.)*

**Run of 2026-10-14: 4.3 written (branch `task/4.3-flows`, from `origin/main` at cb6d770). Stopping here.** Two Prefect flows wrap the Modal jobs: `hello-gpu` and `train-mnist`. Each estimates the cost, sends `⏸️ Awaiting approval, ~$X` on Telegram with a link to the run, then pauses for up to 24 h. Modal is called only after you tick `approve` in the UI; a decline or a timeout ends the run without touching a GPU. Paid steps are never retried. `.claude/settings.json` now stops agents from resuming paused runs or starting deployment runs. 11 new tests (48 total) ✅ against a throwaway Prefect server, with Modal and Telegram faked. Nothing deployed, no Modal call, no money spent. **Human must:** review and merge, then run the 7 steps under 4.3 (register both flows, run `hello-gpu` once, approve it: ~$0.01, at most $0.05).

**Run of 2026-10-14: runtime worktree for the Prefect services (branch `task/4.2-runtime-worktree`, from `main`). Stopping here.** `~/projects/lab-runtime` is a git worktree of `main` with its own `.venv` (`uv sync` done). Both unit files now run from it; `hello` was re-registered from it and ran **Completed**. Nothing installed, no money spent. **Human must:** merge, then run the 9 reinstall steps under "4.2 follow-up" (`git pull`, `uv sync`, `sudo cp`, `daemon-reload`, `restart`, checks). After every later merge: `cd ~/projects/lab-runtime && git pull && uv sync && sudo systemctl restart prefect-server prefect-worker`. Open: `.env` for `lab-runtime` before 4.3.

**Run of 2026-10-14: 4.1 ticked (self-hosted picked), 4.2 set up (branch `task/4.2-prefect-setup`). Stopping here; waiting for the human.** Prefect 3.8.8 added with `uv`; `deploy/prefect-server.service` (UI at http://lab:4200 over Tailscale) and `deploy/prefect-worker.service` (work pool `lab`) written, not installed. A by-hand dry run on localhost worked: the `hello` flow ran Completed; server ~245 MB, worker ~97 MB idle. **Human must:** run the 9 steps under 4.2 (`sudo cp`, `daemon-reload`, two `enable --now`, checks), then paste the output; the agent then measures memory on the real services.

**Run of 2026-10-14: 4.1 written (branch `task/4.1-prefect-design`). Stopping here; waiting for the human to pick.** `docs/04-job-queue-design.md` compares a self-hosted Prefect server with Prefect Cloud's free Hobby tier (memory, cost, `sudo`, accounts, calling Modal, approval gate) and **recommends self-hosted**. Nothing installed, no account created, no money spent. **Human must:** read the doc and pick A (self-hosted) or B (Cloud Hobby); then review and merge. 4.2 starts after the pick.

**Run of 2026-10-14: 3.2 recorded, 3.3 done (branch `task/3.3-document-stage-3`, from `main` after #12). Stopping here.** The human's crash + resume run with W&B passed: one W&B run (`hy7wqqht`) across both runs, resumed at step 1000, final test loss 0.0240 / acc 99.29%. The human checked wandb.ai and Telegram (details under 3.2). 3.2 and 3.3 ticked in ROADMAP. `docs/03-experiment-tracking.md` written, README row and status line updated. **Stage 3 is complete** once this is merged. No money spent by the agent; the agent only ran `rclone ls` (read-only) and offline tests. **Human must:** review and merge `task/3.3-document-stage-3`. Nothing else.

**Run of 2026-10-14: 3.1 recorded, 3.2 written (branch `task/3.2-wandb-template`). Stopping here.** 3.1 ticked (the `wandb` secret exists). 3.2: `jobs/train_template.py` logs to W&B (project `cloud-ai-lab`, run name = `--run-name`), resumed runs continue the same W&B run, and training still works without a key. 4 new tests (37 total) ✅. Not run on Modal. **Human must:** run the two commands under 3.2 (~$0.05 from free credits), check the W&B page, then review and merge.

**Run of 2026-10-14: doc gaps (branch `task/2.6-doc-gaps`). Done; stopping here.** `.claude/settings.json` now also denies `uv run modal run/deploy/serve`. The Stage 2 doc has the real spend-limit path and `modal token new` output. The Stage 6 doc has the real `--test` result and says ⏹️ Stopped is untested. The README status line says Stages 0, 1, 2, 6 are done and Stage 3 (W&B) is next. **Human must:** review and merge `task/2.6-doc-gaps`. Nothing else.

**Final summary, run of 2026-10-14: record 2.3/2.4/6.1/6.2, then 2.5 and 6.3. All done; stopping here.**

**Branches are stacked; review and merge in this order:** `task/2.2-record-gpu-run` → `task/2.4-record-resume-test` → `task/2.5-document-stage-2` → `task/6.3-document-notifications`.

| Task | State | Branch |
|---|---|---|
| 2.1, 2.2 | done, ticked | `task/2.2-record-gpu-run` |
| 2.3, 2.4, 6.1, 6.2 | done, ticked (resume test passed; real Telegram messages) | `task/2.4-record-resume-test` |
| 2.5 Document Stage 2 | done: `docs/02-gpu-compute.md`, README row, `decisions.md` | `task/2.5-document-stage-2` |
| 6.3 Document Stage 6 | done: `docs/06-notifications.md`, README row | `task/6.3-document-notifications` |

**Stages 2 and 6 are complete** once these are merged. No money was spent by the agent; the paid runs were the human's, on Modal's free credit (limit $0). The agent only read Modal and R2 (`modal app list`, `modal app logs`, `modal secret list`, `rclone ls`).

**Human must:** review and merge the four branches in order. Nothing else.

**Noticed, not done (out of scope):**
- The ⏹️ Stopped message (Ctrl-C during `modal run`) has never been tested on a real job. Try it on the next real run.
- `docs/ROADMAP.md` 2.1 says "set a monthly spending limit" with no amount; this build used $0. Fine as is, but worth a line if others copy the lab.
- ~~`.claude/settings.json` still denies `modal run` but not `uv run modal run`~~: fixed in `task/2.6-doc-gaps`.

**2.5 done (2026-10-14, branch `task/2.5-document-stage-2`, on top of `task/2.4-record-resume-test`).** `docs/02-gpu-compute.md` written from the recorded steps; README Stage 2 row and status line updated; "Stage 2 job design" added to `decisions.md`.

**2.3, 2.4, 6.1, 6.2 done (2026-10-14).** The resume test passed: the crash run saved at steps 500 and 1000 and died at 1100; the second run printed `resumed mnist/checkpoints/try-1/latest.pt at step 1000` and finished at step 3000 (test acc 0.9933). R2 holds exactly `best.pt` and `latest.pt`. Telegram sent Started, Failed, and Finished. All four ticked in ROADMAP. Next: 2.5 and 6.3 (docs).

**2.1 and 2.2 done (2026-10-14).** The human finished 2.1 (Modal account, token, spending limit **$0**: free credits only) and re-ran `hello_gpu.py` after the fix: ✅ Tesla T4, 3.84 TFLOPS, 9 s, ~$0.00. Both ticked in ROADMAP. With a $0 limit, jobs stop when the monthly free credit runs out instead of billing. Next: 2.4's resume test (see 2.4).

**Fix of 2026-10-14, second (branch `task/2.4-fix-ckpt-dir`).** The human's first `modal run jobs/train_template.py --run-name try-1 --crash-at-step 1100` failed at the first save (step 500) with `RuntimeError: Parent directory /tmp/ckpt does not exist.` Cause: `/tmp/ckpt` was only created when a checkpoint was restored, and a fresh run has none. Fixed in the template and in `RunCheckpoints.restore()`, with a new test. **Retries:** the logs show one attempt and no retry; all three jobs now set `retries=0` explicitly (Modal's default). **Human must:** merge this branch, then re-run 2.4's two commands (~$0.05). Details under 2.4.

**Fix of 2026-10-14 (branch `task/2.2-fix-return-types`).** The human's first `modal run jobs/hello_gpu.py` got a Tesla T4 but failed returning the result (`DeserializationError`: `torch` not available locally). Cause: the result held `torch.__version__`, a `TorchVersion` object, not a `str`. Fixed in `hello_gpu.py`; `train_template.py` now casts its results too; `r2_hello.py` was already fine. Images now include `numpy`, and the install command is `uv tool install modal --with python-dotenv`. **Human must:** merge this branch, then re-run `modal run jobs/hello_gpu.py` (< $0.05). Details under 2.2.

**Run of 2026-10-13: tasks 2.2, 2.3, 2.4, 6.2.** All agent work is finished. Each task is blocked only on a human step: Modal account (2.1), the R2 secret, a Telegram bot (6.1), and running the paid jobs. No money was spent and no Modal job was run.

**Branches are stacked; review and merge in this order:** `task/2.2-hello-gpu` → `task/2.3-modal-r2` → `task/2.4-train-template` → `task/6.2-notifier`. Each builds on the one before (shared `pyproject.toml`, `lab/`, this file).

| Task | Agent work | Tested | Blocked on |
|---|---|---|---|
| 2.2 Hello-GPU | `jobs/hello_gpu.py`, uv project | GPU run ❌ (result type), fixed; re-run ✅ Tesla T4 | nothing: done |
| 2.3 R2 from Modal | `lab/storage.py`, `jobs/r2_hello.py`, `.env.example` | 10 tests vs fake S3 ✅; real run ✅ | nothing: done |
| 2.4 Training template | `lab/checkpoints.py`, `jobs/train_template.py` | GPU run ❌ (`/tmp/ckpt` missing), fixed; resume test ✅; 7 tests ✅ | nothing: done |
| 6.2 Notifier | `lab/notify.py`, wired into all jobs | 16 tests vs fake Telegram ✅; real Started / Failed / Finished ✅ | nothing: done |

**What the human does, in order** (details under each task below; run everything on the server from `~/projects/cloud-ai-lab`):
1. **2.1:** sign up at modal.com, **set a monthly spending limit**, then `uv tool install modal --with python-dotenv` and `modal token new`.
2. **R2 + Telegram keys:** `cp .env.example .env && chmod 600 .env`, then fill in the R2 values (same as the rclone `r2` remote) and, after 6.1, the bot token and chat ID.
3. **Modal secret:** `grep '^R2_' .env > ~/r2.env && modal secret create r2 --from-dotenv ~/r2.env; rm ~/r2.env`
4. **Free:** `uv run python -m lab.notify --test` → 4 Telegram messages (needs 6.1).
5. **Paid, about $0.10 total** (T4 at $0.000164/s):
   - `modal run jobs/hello_gpu.py`: < $0.05
   - `modal run jobs/r2_hello.py`: < $0.01
   - `modal run jobs/train_template.py --run-name try-1 --crash-at-step 1100`, then the same without `--crash-at-step`: ~$0.05 for both; the second must print `resumed ... at step 1000`.
6. Review and merge the four branches in order; tick 2.2–2.4 and 6.2 in ROADMAP once the runs pass.

**Noticed, not done (out of scope):**
- The training loop has never executed. Expect possible small fixes after the first GPU run. If you'd rather catch them for ~$0.001, you could approve a CPU-only Modal smoke run (`gpu=None`, a few steps).
- The README's Stage 2 and Stage 6 rows still say "coming"; that's for 2.5 / 6.3.
- `.claude/settings.json` denies `modal run`, but not `uv run modal run`. Add `Bash(uv run modal run:*)` if you want the same guard on that form. (Fixed 2026-10-14 in `task/2.6-doc-gaps`.)

---

<!-- Template for each task:

## <id> — <title>
- **Branch:** `task/<id>-<short-name>`
- **State:** in progress / done / blocked
- **Done:** <what's finished>
- **Next:** <the next step>
- **Human must:** <exact commands, keys, approvals, or costs; "nothing" if none>

-->

## 0.2 — Document Stage 0
- **Branch:** `task/0.2-document-stage-0`
- **State:** done, committed and pushed; waiting for the human's review and merge
- **Done:** `docs/00-agent-setup.md` written (install, PATH fix, tmux, subscription login, wrapped-URL `Unknown scope: user:mcp_` failure, focus-events fix, verify). README Stage 0 row added; 0.1 and 0.2 ticked in ROADMAP.
- **Next:** nothing.
- **Human must:** review and merge.

## 0.3 — Unattended agent rules
- **Branch:** `task/0.3-unattended-rules`
- **State:** done, waiting for the human's review and merge
- **Done:** hard rule 2 replaced (commit and push freely to own branch); "Working unattended" section added to `CLAUDE.md`; this file created; `.claude/settings.json` with `permissions.deny` rules.
- **Next:** nothing.
- **Human must:** review and merge. The new rule 2 takes effect once it's on `main`.

<details><summary>Steps and output from this build</summary>

**1. Check the settings format** in the current docs (code.claude.com/docs/en/settings and /permissions, read 2026-10-13):
- the `"$schema"` URL is `https://json.schemastore.org/claude-code-settings.json`;
- `Bash(x:*)` is still supported and means the same as `Bash(x *)`;
- `Read(./.env)` matches `.env` in the current directory; `Read(**/.env)` matches any `.env` at or under it;
- Read deny rules also cover `cat`, `head`, `tail`, `sed` on that file in Bash, but not scripts (Python, Node) that open it themselves.

**Result:** ✅ the rule list as given is valid syntax.

**2. Write `.claude/settings.json` and validate the JSON**
```console
$ python3 -m json.tool .claude/settings.json >/dev/null && echo "JSON valid"
JSON valid
```
**Result:** ✅

**3. Test that deny rules block commands** (harmless commands chosen so nothing happens even if not blocked):
```console
$ git merge --abort
Permission to use Bash with command git merge --abort has been denied.

$ rm -rf ./does-not-exist-deny-test
Permission to use Bash with command rm -rf ./does-not-exist-deny-test has been denied.
```
**Result:** ✅ both blocked by Claude Code 2.1.296, in the same session that created the file.

**Limits (from the docs):** deny rules match the command as written. They are not a security wall: a bare `git push` while on `main`, `git push origin HEAD:main`, `rm -fr`, `/usr/bin/sudo`, `bash -c "..."`, or a Python script reading `.env` aren't matched. They catch the usual form; the rules in `CLAUDE.md` and branch protection on GitHub cover the rest.
</details>

## 2.2 — Hello-GPU job
- **Branch:** `task/2.2-hello-gpu`
- **State:** done (2026-10-14). The first GPU run failed returning its result; fixed on `task/2.2-fix-return-types` (merged); the re-run passed. Ticked in ROADMAP, with 2.1.
- **Fix branch:** `task/2.2-fix-return-types`: plain Python types in the returned dicts (`hello_gpu.py`, `train_template.py`), `numpy==2.5.3` in the torch images, ROADMAP 2.1 install command now `uv tool install modal --with python-dotenv`.
- **Done:** `uv` project (`pyproject.toml`, `uv.lock`, Python 3.12, `modal` 1.6.1). `jobs/hello_gpu.py`: a T4 function that prints `nvidia-smi`, times a 4096×4096 PyTorch matmul, and returns GPU name, torch/CUDA versions, ms and TFLOPS. 5-minute hard timeout. Cost estimate in the file's docstring.
- **Next:** nothing.
- **Human must:** nothing. The steps below are kept as a record.
  1. ✅ **2.1** (done 2026-10-14; spending limit set to **$0**, free credits only): sign up for Modal, **set a monthly spending limit**, then on the server:
     ```bash
     uv tool install modal --with python-dotenv   # the `modal` command; --from-dotenv needs python-dotenv
     modal token new          # opens a login link; writes ~/.modal.toml
     ```
  2. Run the job: `modal run jobs/hello_gpu.py`
     **Estimated cost:** T4 at $0.000164/s (modal.com/pricing, 2026-10-13). ~1–2 min of GPU time plus a few minutes of CPU for the first image build: **under $0.05**, inside the Starter plan's $30/month free credit.
  3. Check: output shows `gpu: Tesla T4` and the command returns to the prompt by itself.

<details><summary>Steps and output from this build</summary>

**1. Check whether 2.1 is done**
```console
$ which modal; test -f ~/.modal.toml && echo "modal.toml exists" || echo "no modal.toml"
bash: line 1: modal: command not found
no modal.toml
```
**Result:** ❌ 2.1 not done: no `modal` command and no token. The code can still be written; running it waits for the human.

**2. Create the project and add the Modal client library**
```console
$ uv init --bare --python 3.12 --name cloud-ai-lab
Initialized project `cloud-ai-lab`
$ uv add modal
...
$ uv run python -c "import modal; print(modal.__version__)"
1.6.1
$ uv python pin 3.12
Pinned `.python-version` to `3.12`
```
**Result:** ✅ The library only; it needs no account.

**3. Pick the GPU and estimate the cost** (modal.com/pricing, read 2026-10-13)

| GPU | $/s | $/h |
|---|---|---|
| T4 | 0.000164 | 0.59 |
| L4 | 0.000222 | 0.80 |
| A10 | 0.000306 | 1.10 |

**Result:** ✅ T4 is the cheapest. Pinned `torch==2.14.1` (released 2026-09-30).

**4. Check the job loads** (no network, no Modal account needed)
```console
$ uv run python -m py_compile jobs/hello_gpu.py
$ uv run python -c "import runpy; m = runpy.run_path('jobs/hello_gpu.py'); app = m['app']; print('app:', app.name, '| functions:', list(app.registered_functions)); print('entrypoints:', list(app.registered_entrypoints))"
app: hello-gpu | functions: ['hello']
entrypoints: ['main']
```
**Result:** ✅ (Modal warns that `registered_functions` is deprecated in 1.7; only the check uses it, not the job.)

**5. First GPU run** (run by the human on 2026-10-14; output as reported)
```console
$ modal run jobs/hello_gpu.py
...
DeserializationError: Deserialization failed because the 'torch' module is not available in the local environment.
```
The container log also showed torch's warning `Failed to initialize NumPy`.

**Result:** ❌ the job ran on a **Tesla T4**, but the result never reached the server.
- **Error:** `DeserializationError: ... the 'torch' module is not available in the local environment.`
- **Cause:** Modal pickles the return value in the container and unpickles it on the server, inside the `modal` tool's own environment, which has no torch. `torch.__version__` is a `TorchVersion` (a `str` subclass defined in torch), so the pickle refers to the torch module and can't load without it.
- **Fix:** return only plain Python types: `str(torch.__version__)`, and `str()` around the other torch-provided values. Checked the other jobs for the same problem:
  - `train_template.py`: values were already plain (`.item()` gives a Python `float`); added `int()` / `float()` casts so it stays that way when edited.
  - `r2_hello.py`: returns object keys from boto3, already plain `str`. No change.
- **Also:** torch prints `Failed to initialize NumPy` when numpy isn't installed. Added `numpy==2.5.3` (released 2026-09-06; 2.5.4 is only 4 days old) to the `hello_gpu` and `train_template` images. `r2_hello` doesn't use torch, so its image is unchanged.

**6. Reproduce the cause without torch** (a `str` subclass from a module that's missing on the loading side, as on the server)
```console
$ uv run python -I scratchpad/repro.py scratchpad/fakemod
isinstance(v, str): True
str(v): {'torch': '2.14.1+cu128'}
raw TorchVersion: ModuleNotFoundError No module named 'fake_torch_version'
```
**Result:** ✅ a `str` subclass still needs its module to unpickle; `str(v)` doesn't.

**7. Check the fixed jobs load, lint, and the tests still pass**
```console
$ for f in hello_gpu r2_hello train_template; do uv run python -c "import runpy; print('$f loads, app:', runpy.run_path('jobs/$f.py')['app'].name)"; done
hello_gpu loads, app: hello-gpu
r2_hello loads, app: r2-hello
train_template loads, app: train-template
$ uvx ruff@0.14.0 check --select E,F,W,B --line-length 100 lab jobs tests
All checks passed!
$ uv run pytest -q
32 passed in 3.79s
```
**Result:** ✅

**8. `modal secret create --from-dotenv` needs `python-dotenv`** (reported by the human while doing 2.3's secret)
**Result:** ❌ then ✅
- **Cause:** `uv tool install modal` installs the CLI without `python-dotenv`, which `--from-dotenv` imports.
- **Fix:** install the CLI with it, and the ROADMAP 2.1 command now says so:
```console
$ uv tool install modal --with python-dotenv
$ uv tool list --show-with
modal v1.6.1 [with: python-dotenv]
- modal
```

**9. Re-run on the GPU** (run by the human on 2026-10-14, after merging `task/2.2-fix-return-types`; result as reported by the Telegram notifier)
```console
$ modal run jobs/hello_gpu.py
...
```
Telegram:
```text
✅ Finished: hello-gpu in 0m 09s, ~$0.00 on T4
Tesla T4: 3.84 TFLOPS
```
**Result:** ✅ the GPU name came back (Tesla T4), the result reached the server, and the job stopped by itself. This meets 2.2's "done when".
- **Cost:** 9 s at $0.000164/s ≈ **$0.0015**, under the < $0.05 estimate (that allowed for the first image build). Paid from free credits.
- **Speed:** 3.84 TFLOPS on a 4096×4096 FP32 matmul, about half of a T4's ~8 TFLOPS FP32 peak. Plausible for one untuned matmul timed once.
- **Also confirmed:** the Telegram notifier sends a real Finished message (6.1's bot works).

**2.1 confirmed by the human:** Modal account created, `modal token new` succeeded, spending limit set to **$0**: jobs run on the free monthly credit only and stop when it runs out instead of billing.
</details>

## 2.3 — R2 from Modal
- **Branch:** `task/2.3-modal-r2` (built on `task/2.2-hello-gpu`; merge 2.2 first)
- **State:** done (2026-10-14). The human created the `r2` secret and ran the job; the file landed in R2. Ticked in ROADMAP.
- **Done:** `lab/storage.py` (`r2_key`, `upload`, `download`, `list_keys`, `exists`; credentials from env vars; keys laid out as `<project>/<datasets|checkpoints|runs>/...`). `jobs/r2_hello.py`: a CPU-only Modal job that writes `hello/runs/<UTC stamp>/hello.txt` and lists it. 10 tests in `tests/test_storage.py` against an in-memory fake S3 (moto). `.env.example` with the R2 keys.
- **Next:** nothing.
- **Human must:** nothing. The steps below are kept as a record.
  1. ✅ Finish **2.1** (see 2.2).
  2. Create `.env` from `.env.example` and fill in the R2 values (the same endpoint and token as the rclone `r2` remote):
     ```bash
     cp .env.example .env && chmod 600 .env && nano .env
     ```
  3. Store only the `R2_` keys as the Modal secret `r2` (via a temp file, so keys never land in shell history):
     ```bash
     grep '^R2_' .env > ~/r2.env && modal secret create r2 --from-dotenv ~/r2.env; rm ~/r2.env
     ```
  4. Run (from the repo root): `modal run jobs/r2_hello.py`. **Estimated cost:** CPU only, a few seconds: **under $0.01**.
  5. Check: `rclone ls r2:cloud-ai-lab/hello/runs/` lists the new `hello.txt`.

<details><summary>Steps and output from this build</summary>

**1. Add dependencies**
```console
$ uv add boto3
$ uv add --dev pytest "moto[s3]"
$ grep -A1 -E '^name = "(boto3|moto|pytest)"' uv.lock
name = "boto3"
version = "1.43.112"
name = "moto"
version = "5.2.4"
name = "pytest"
version = "9.1.1"
```
**Result:** ✅

**2. Test `lab/storage.py` against moto (fake S3, no network)**
```console
$ uv run pytest -q
...
E   botocore.exceptions.SSLError: SSL validation failed for https://fake-account.r2.cloudflarestorage.com/test-bucket [SSL: SSLV3_ALERT_HANDSHAKE_FAILURE] sslv3 alert handshake failure (_ssl.c:1000)
...
6 passed, 4 errors in 20.83s
```
**Result:** ❌
- **Error:** the tests that touch the bucket tried to reach a real host.
- **Cause:** moto only intercepts AWS URLs by default. An R2-style `endpoint_url` went out to the network (with fake keys, so nothing happened).
- **Fix:** set `MOTO_S3_CUSTOM_ENDPOINTS` to the test endpoint in the fixture.
```console
$ uv run pytest -q
..........                                                               [100%]
10 passed in 3.66s
```
**Result:** ✅ Covers key layout and bad paths, a binary round trip, overwrite, prefix listing past one page (1005 keys), `exists`, and a clear error when a variable is missing.

**3. Check the job loads and finds `lab` locally**
```console
$ uv run python -c "import runpy, importlib.util; m = runpy.run_path('jobs/r2_hello.py'); print('app:', m['app'].name); print('lab found at:', importlib.util.find_spec('lab').origin)"
app: r2-hello
lab found at: /home/thovicheka/projects/cloud-ai-lab/lab/__init__.py
```
**Result:** ✅ `modal run` adds the current directory to `sys.path` (`modal/cli/import_refs.py`), so jobs must be run **from the repo root** for `add_local_python_source("lab")` to find the package.

**4. Choose how the secret is created**
```console
$ uv run modal secret create --help
...
  --from-dotenv PATH  Path to a .env file to load secrets from.
```
**Result:** ✅ `--from-dotenv` loads *every* key in the file, so the human's command feeds it only the `R2_` lines.

**5. Write to real R2 from Modal** (run by the human on 2026-10-14; container log and checks fetched afterwards, read-only)
```console
$ modal run jobs/r2_hello.py
...
$ uv run modal app logs ap-kErl***
 + boto3==1.43.112
...
Built image im-*** in 4.75s
uploaded r2:cloud-ai-lab/hello/runs/20261014T045622Z/hello.txt
Stopping app - local entrypoint completed.
$ rclone ls r2:cloud-ai-lab/hello/runs/
       53 20261014T045622Z/hello.txt
$ uv run modal secret list
│ Name │ Created at           │ ...
│ r2   │ 2026-10-14 04:45 UTC │ ...
```
**Result:** ✅ a Modal container wrote to R2 with the `r2` secret, and the file is visible from the server with rclone.
</details>

## 2.4 — Checkpointed training template
- **Branch:** `task/2.4-train-template` (built on `task/2.3-modal-r2`; merge 2.2 → 2.3 → 2.4)
- **State:** done (2026-10-14). The first GPU run failed at the first save; fixed on `task/2.4-fix-ckpt-dir` (merged); the resume test then passed. Ticked in ROADMAP.
- **Fix branch:** `task/2.4-fix-ckpt-dir`: the template creates `/tmp/ckpt` before restoring or saving; `RunCheckpoints.restore()` now always creates its target folder, so a copied template can't hit this; new test `test_fresh_run_can_save_to_a_missing_folder`; `retries=0` set explicitly on all three jobs.
- **Done:** `lab/checkpoints.py` (`RunCheckpoints`: `latest.pt` + `best.pt` per run, overwritten in place, so only 2 objects ever; `restore()` for resuming). `jobs/train_template.py`: small CNN on MNIST (T4); evaluates and checkpoints every 500 steps; resumes weights, optimizer, step, best loss, RNG and data position from `latest.pt`; `--crash-at-step N` simulates a lost GPU. 6 new tests in `tests/test_checkpoints.py` (16 total).
- **Next:** nothing.
- **Human must:** nothing. The steps below are kept as a record.
  1. ✅ Finish 2.1 and 2.3's secret.
  2. Crash on purpose, then resume (from the repo root):
     ```bash
     modal run jobs/train_template.py --run-name try-1 --crash-at-step 1100   # dies after saving step 1000
     modal run jobs/train_template.py --run-name try-1                        # should print "resumed ... at step 1000"
     rclone ls r2:cloud-ai-lab/mnist/checkpoints/try-1/                       # exactly best.pt and latest.pt
     ```
     Pressing Ctrl-C during the first run works too (it stops the Modal app), but 3000 steps on a T4 finish in well under a minute, so it's hard to time.
     **Estimated cost:** T4 at $0.000164/s; each run ~1–2 min including startup and the first image build: **~$0.05 for both runs**.
  3. Check: the second run prints `resumed mnist/checkpoints/try-1/latest.pt at step 1000` and ends with `steps_this_run: 2000`, `resumed_from: 1000`.

<details><summary>Steps and output from this build</summary>

**1. Write `lab/checkpoints.py` and test it (moto, no network)**
```console
$ uv run pytest -q
................                                                         [100%]
16 passed in 4.23s
```
**Result:** ✅ New tests cover: key layout, `improved()` for min and max, a new run restores nothing, resume returns the last save while best moves only on improvement, only 2 objects after 10 saves, runs don't see each other's checkpoints. The R2 fixture moved to `tests/conftest.py` so both test files share it.

**2. Write the template; check it loads and lints**
```console
$ uv run python -c "import runpy; m = runpy.run_path('jobs/train_template.py'); print('app:', m['app'].name)"
app: train-template
$ uvx ruff@0.14.0 check --select E,F,W,B --line-length 100 lab jobs tests
All checks passed!
```
**Result:** ✅

**3. Review the resume path by reading it** (it can't run here)
**Result:** ❌ found a bug before any run
- **Error (would have been):** resume crashes in `torch.set_rng_state`.
- **Cause:** the checkpoint was loaded with `map_location="cuda"`, which moves the saved RNG state to the GPU; `set_rng_state` only accepts a CPU tensor.
- **Fix:** load with `map_location="cpu"`. `load_state_dict` copies weights and optimizer state onto the model's device anyway.

**4. Design notes**
- Batch order depends only on `(seed, epoch, step)`: each epoch's shuffle uses its own seeded generator. A resumed run sees exactly the batches the lost run would have seen next.
- Dropout uses the CUDA RNG, which is saved and restored. Results should match an uninterrupted run apart from cuDNN's usual non-determinism.
- `best.pt` is uploaded before `latest.pt`. A crash between the two then leaves `latest` one save behind (resume redoes ≤500 steps) rather than losing a new best.
- `--run-name` has no default on purpose: rerunning with the same name resumes, and a new name starts fresh. A finished run rerun with its name does nothing and returns its result.

**5. First GPU run** (run by the human on 2026-10-14; container log fetched afterwards with `modal app logs`, download progress lines removed)
```console
$ modal run jobs/train_template.py --run-name try-1 --crash-at-step 1100
...
$ uv run modal app logs ap-IIGT***
...
no checkpoint at mnist/checkpoints/try-1/latest.pt; starting from step 0
Traceback (most recent call last):
  ...
  File "/root/train_template.py", line 141, in train
    torch.save(
  ...
RuntimeError: Parent directory /tmp/ckpt does not exist.
Stopping app - uncaught exception raised locally: RuntimeError('Parent directory /tmp/ckpt does not exist.').
```
**Result:** ❌ the training loop ran (MNIST downloaded, 500 steps trained), then the first `torch.save` failed. Nothing reached R2.
- **Error:** `RuntimeError: Parent directory /tmp/ckpt does not exist.` (`train_template.py` line 141, `torch.save`)
- **Cause:** `/tmp/ckpt` was only created by `storage.download()` during a restore. A fresh run has nothing to restore, so the folder never existed. `torch.save` doesn't create folders.
- **Fix:**
  - `jobs/train_template.py`: `os.makedirs(os.path.dirname(path), exist_ok=True)` right after choosing the path, before any restore or save.
  - `lab/checkpoints.py`: `restore()` creates `local_path`'s folder even when there's no checkpoint, so any job that copies the restore-then-save pattern works on a fresh run.
  - Checked the rest: `storage.download()` already creates parent folders (`mkdir(parents=True)`), and `test_upload_download_round_trip` already downloads into a missing `nested/` folder. `storage.upload()` only reads. `load_data()` lets torchvision create `/tmp/data`. No other changes.

**6. Did Modal retry the failed run?**
```console
$ uv run modal app list
...
  ap-IIGT***   train-template   stopped   0   2026-10-14 04:57 UTC   2026-10-14 04:57 UTC
...
$ uv run modal app logs ap-IIGT*** > train_logs.txt
$ # count attempts: each attempt prints "no checkpoint ..." or "resumed ..." once
'no checkpoint' count: 1 | Traceback count: 1 | 'retr' lines: []
```
**Result:** ✅ one attempt, no retry, billed once.
- **Retries configured:** 0 on all three jobs. None of them set `retries`, and Modal's default is no retries (`retries=None` → no retry policy, `modal/_utils/function_utils.py`).
- **"No more retries left"** isn't a message Modal 1.6.1 prints. It's a code comment in `modal/_functions.py` (line 514), on the path that turns the failure into the local exception. It doesn't appear in this run's logs.
- **Change:** `retries=0` now written out on each `@app.function`, with a comment, so the setting is visible and a copied template doesn't change it silently.
- **What can still retry:** Modal re-runs an input that its own infrastructure lost (e.g. a preempted GPU); that isn't configurable. For the template this isn't silent and doesn't redo much: the retry prints `resumed ... at step N` and loses at most `--ckpt-every` steps. Each attempt is still capped by `timeout`, and the Telegram cost (6.2) is measured on the server's wall clock, so it includes any retry.

**7. Test a fresh run with no folder, and check the test catches the bug**
```console
$ uv run pytest -q
.................................                                        [100%]
33 passed in 4.17s
$ sed -i '/Path(local_path).parent.mkdir/d' lab/checkpoints.py   # temporarily undo the fix
$ uv run pytest -q tests/test_checkpoints.py
E       FileNotFoundError: [Errno 2] No such file or directory: '/tmp/pytest-of-<user>/.../ckpt/latest.pt'
1 failed, 6 passed in 0.89s
$ # fix restored
$ uvx ruff@0.14.0 check --select E,F,W,B --line-length 100 lab jobs tests
All checks passed!
$ uv run python -c "from modal._utils.function_utils import _parse_retries; print(_parse_retries(0))"
backoff_coefficient: 1
initial_delay_ms: 1000
max_delay_ms: 60000
```
**Result:** ✅ The new test fails without the fix and passes with it. `retries=0` is valid; the policy's `retries` field is 0, so it isn't printed. All three jobs still load.

**8. Resume test on the GPU** (run by the human on 2026-10-14, after merging `task/2.4-fix-ckpt-dir`; container logs fetched afterwards with `modal app logs`, download progress and traceback frames removed)

Crash run:
```console
$ modal run jobs/train_template.py --run-name try-1 --crash-at-step 1100
...
no checkpoint at mnist/checkpoints/try-1/latest.pt; starting from step 0
step   500/3000  train loss 0.0476  test loss 0.0499  test acc 0.9834  saved latest + best
step  1000/3000  train loss 0.0118  test loss 0.0373  test acc 0.9876  saved latest + best
Traceback (most recent call last):
RuntimeError: simulated crash at step 1100 (--crash-at-step)
Stopping app - uncaught exception raised locally: RuntimeError('simulated crash at step 1100 (--crash-at-step)').
```
Telegram: ▶️ Started, then ❌ Failed.

**Result:** ✅ (the crash is the point) saved at 500 and 1000, then died at 1100. The `/tmp/ckpt` fix works.

Resume run (same `--run-name`, no crash flag):
```console
$ modal run jobs/train_template.py --run-name try-1
...
resumed mnist/checkpoints/try-1/latest.pt at step 1000 (best test loss 0.0373)
step  1500/3000  train loss 0.0091  test loss 0.0290  test acc 0.9895  saved latest + best
step  2000/3000  train loss 0.0231  test loss 0.0281  test acc 0.9910  saved latest + best
step  2500/3000  train loss 0.0140  test loss 0.0231  test acc 0.9921  saved latest + best
step  3000/3000  train loss 0.0028  test loss 0.0217  test acc 0.9933  saved latest + best
Stopping app - local entrypoint completed.
```
Result (as printed locally, reported by the human): finished at step 3000, `best_test_loss: 0.0217`, `train_seconds: 23.2`. Telegram: ✅ Finished.

**Result:** ✅ it resumed at step 1000 instead of starting over, which is 2.4's "done when". The best loss carried over (0.0373) and kept improving.

R2 afterwards:
```console
$ rclone ls r2:cloud-ai-lab/mnist/checkpoints/try-1/
  5074197 best.pt
  5074197 latest.pt
```
**Result:** ✅ exactly two objects for the run. They're the same size because the last save was also the best one.

**Cost:** both runs ran on free credits (spending limit $0). 2000 steps of training took 23.2 s; with start-up each run took about a minute.
</details>

## 4.4 — Document Stage 4
- **Branch:** `task/4.4-document-stage-4` (from `origin/main` at 7a610fb)
- **State:** done; ticked in ROADMAP. Waiting for review and merge.
- **Done:**
  - `docs/04-job-queue.md` (STYLE.md format) covers: how it fits together; 11 steps (add Prefect, CLI profile, `lab-runtime` worktree, `.env` symlink, install and check both systemd services, register deployments, a free run, a paid run through the gate, parameters / `--start-in` / `--start-at` / schedules, the update routine after merges); a table of the gate's outcomes (approve / decline / 24 h timeout); limits (paused runs hold worker slots, the deny rules and what they can't stop, no UI login, Modal's $0 limit as the hard stop); verify. Every step has an "Example from this build" block.
  - Step 9 has the real decline (`supportive-vulture`) and approve (`psychedelic-velociraptor`) runs, and `sophisticated-elk`. It also says where the new UI keeps **Resume** (⋮ menu; **Switch to V1 UI** shows a button), with a troubleshooting note. Status set to ✅.
  - `--start-in`, `--start-at`, and `deployment schedule create --cron --timezone` are checked against Prefect 3.8.8's CLI source but **not run** (the doc says so). Running them starts runs, and the deny rules block agents from that.
  - README: Stage 4 row ✅; status line says Stages 0–4 and 6 are done and Stage 5 is next.
- **Tested:** read-only checks only: `COLUMNS=200 uv run prefect flow-run ls`, `uv run prefect flow-run logs <id>`, and the run's state history from the Prefect API.
- **Human must:** review and merge `task/4.4-document-stage-4`.
- **Noticed, not done (out of scope):**
  - Run history in `~/.prefect/prefect.db` grows without limit. The doc doesn't cover a cleanup yet; worth a step once there's real volume.
  - `CLAUDE.md` still says to create branches "from main"; since 4.2's worktree, that has to be `origin/main` (the doc's step 3 says so).
  - The 24 h timeout path (⌛, **Failed**) is only covered by `tests/test_flows.py`, not a real run. That's fine, since a real test means waiting a day.
  - `approve` defaults to unticked, and the new UI hides Resume, so it's easy to submit a decline by mistake (it happened once in this build). Making `approve` a required choice with no default would make that harder; that would be a small 4.3 follow-up.

## 4.3 — Wrap the Modal jobs in Prefect flows
- **Branch:** `task/4.3-flows` (from `origin/main` at cb6d770)
- **State:** done; merged (#18), ticked in ROADMAP (on `task/4.4-document-stage-4`). Pause, decline, and approve all work on the real server.
- **Done:**
  - `flows/approval.py`: the gate. `ask_approval()` sends `⏸️ Awaiting approval, ~$X: <job> on T4`, the worst case at the job's Modal timeout, and the UI link (`prefect.runtime.flow_run.ui_url`, so `http://lab:4200/...` on the worker). Then it calls `pause_flow_run(wait_for_input=Approval, timeout=24 h)`. The `Approval` form has `approve` (unticked by default, so pressing Resume without ticking it declines) and `note`.
  - `flows/hello_gpu.py` (flow `hello-gpu`) and `flows/train.py` (flow `train-mnist`, parameters `run_name`, `steps`, `ckpt_every`). After approval, a task runs the existing Modal function with `app.run()` + `.remote()` inside `notify_job()`, so you get ▶️ Started, then ✅ Finished or ❌ Failed, as with `modal run`. These are ephemeral apps, as proposed in the design doc §4, so no `modal deploy` is needed.
  - States you'll see: Running → **Paused** → Running → **Completed** / **Failed**. Declined → **Cancelled** (🚫 on Telegram). No answer in 24 h → **Failed** (⌛ on Telegram).
  - Retries: Telegram sends retry twice (10 s apart). If they still fail, the flow logs a warning and carries on, so the gate still holds. Paid steps: task `retries=0`, flow `retries=0`, no caching, and Modal's own `retries=0` as before. A failed training run is re-run by hand with the same `run_name`; it resumes from its R2 checkpoint and asks for approval again.
  - Cost estimates: based on real runs (hello-gpu took 9 s; training did 2000 steps in 23–27 s).
    - `hello-gpu`: 60 s → **~$0.01**, at most **$0.05** (5 min timeout).
    - `train-mnist`: 90 s + 15 ms/step. 3000 steps → **~$0.02**, at most **$0.30** (30 min timeout).
  - `.claude/settings.json`: denies the flow-run resume and deployment run commands. Covered forms: bare `prefect`, `uv run prefect`, and the `.venv/bin/prefect` paths. Glob rules also catch the Python API names (`resume_flow_run`, `run_deployment`) and the REST resume / create-run paths.
  - `tests/test_flows.py`: 11 tests on a throwaway Prefect server (`prefect_test_harness`). Modal is faked, and any real `modal.App.run` fails the test. Telegram is faked. The pause is the real one, and the tests resume it through the API as the UI does. The fake Telegram fixture moved from `test_notify.py` to `conftest.py`.
- **Human test runs (2026-10-15; all ✅):**
  - ✅ Deployed: `prefect deployment ls` lists `hello/hello`, `hello-gpu/hello-gpu`, `train-mnist/train-mnist`, all on pool `lab`.
  - ✅ Decline: `supportive-vulture` (hello-gpu). Telegram's `⏸️ Awaiting approval` arrived. Resumed **without** ticking approve → Telegram `🚫 Declined: hello-gpu. Nothing ran on Modal; $0 spent.` State **Cancelled**, no Modal task on the timeline.
  - ✅ Approve: `psychedelic-velociraptor` (hello-gpu). Resumed **with** approve ticked → Telegram `▶️ Started: hello-gpu (T4)`, then `✅ Finished: hello-gpu in 0m 14s, ~$0.00 on T4` / `Tesla T4: 4.28 TFLOPS`. State **Completed**.
  - Older paused run `sophisticated-elk`: **CANCELLED** in `flow-run ls`.
  - UI note: in the new Prefect UI, **Resume** is in the ⋮ menu; **Switch to V1 UI** shows a Resume button.
  - Side note: each decline logs a `CancelledRun` traceback after the Cancelled state. It's harmless: Prefect raises the Cancelled state that the flow returns.

<details><summary>Example from this build: the human's test runs</summary>

**1. Deployments** (human, from `~/projects/lab-runtime`)
```console
$ uv run prefect deployment ls
│ hello/hello                   │ 09384bc5-... │ lab │
│ hello-gpu/hello-gpu           │ 6c12d07c-... │ lab │
│ train-mnist/train-mnist       │ 70c0c3d9-... │ lab │
```
**Result:** ✅

**2. Runs** (agent, read-only)
```console
$ COLUMNS=200 uv run prefect flow-run ls --limit 6
│ e673c7d7-... │ hello-gpu │ psychedelic-velociraptor │ COMPLETED │ 2 minutes ago  │
│ 1dc4dad0-... │ hello     │ energetic-dormouse       │ COMPLETED │ 1 minute ago   │
│ b0065954-... │ hello-gpu │ supportive-vulture       │ CANCELLED │ 11 minutes ago │
│ ac67ec1d-... │ hello-gpu │ sophisticated-elk        │ CANCELLED │ 11 hours ago   │
│ e3fc86d3-... │ hello     │ slick-swallow            │ COMPLETED │ 11 hours ago   │
│ bffd5c93-... │ hello     │ mutant-trogon            │ COMPLETED │ 11 hours ago   │
```
**Result:** ✅

**3. Decline: `supportive-vulture`** (state history, UTC)
```console
04:09:29 Scheduled · 04:09:39 Running · 04:09:40 Paused · 04:25:20 Running · 04:25:22 Cancelled "Declined in the UI; nothing ran on Modal"
paused-1-response  {"approve":false,"note":""}
```
Telegram (human): `⏸️ Awaiting approval`, then `🚫 Declined: hello-gpu. Nothing ran on Modal; $0 spent.` No Modal task on the timeline. **Result:** ✅ $0.

**4. Approve: `psychedelic-velociraptor`** (agent, read-only)
```console
$ uv run prefect flow-run logs e673c7d7-...
04:31:59 ⏸️ Awaiting approval, ~$0.01: hello-gpu on T4 | At most $0.05 if it hits its 5 min timeout. | http://lab:4200/flow-runs/flow-run/e673c7d7-... | ...
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
State history: `04:31:35 Scheduled · 04:31:45 Pending · 04:31:48 Running · 04:31:59 Paused · 04:34:39 Running · 04:35:04 Completed`. Telegram (human): `▶️ Started: hello-gpu (T4)`, then `✅ Finished: hello-gpu in 0m 14s, ~$0.00 on T4` / `Tesla T4: 4.28 TFLOPS`. **Result:** ✅ Modal called only after approval; ~$0.00 of free credit.

**5. Earlier attempt.** The run of 2026-10-15 (first) recorded `supportive-vulture` as a failed approve. The human has since confirmed it was the decline test. So nothing was wrong with the gate; only the approve path hadn't been run yet.
</details>

- **Human must:** nothing. Steps 1–7 below are done; kept for reference.

1. Go to the runtime checkout:
```bash
cd ~/projects/lab-runtime
```

2. Get the merged flows (no new packages, so no `uv sync` or restart needed):
```bash
git pull
```

3. Register `hello-gpu` with the work pool `lab` (expected: `│ hello-gpu/hello-gpu │ applied │`):
```bash
uv run python -m flows.hello_gpu
```

4. Register `train-mnist` (expected: `│ train-mnist/train-mnist │ applied │`):
```bash
uv run python -m flows.train
```

5. Check both are there:
```bash
uv run prefect deployment ls
```

6. Start one `hello-gpu` run. It only pauses: Telegram should say `⏸️ Awaiting approval, ~$0.01: hello-gpu on T4` with a link. Nothing is spent yet.
```bash
uv run prefect deployment run hello-gpu/hello-gpu
```

7. *(On the laptop or phone, over Tailscale)* open the link from Telegram → **Resume** → tick **approve** → **Submit**. **Cost: ~$0.01, at most $0.05** (T4 at $0.000164/s, 5 min hard timeout; covered by Modal's free credit, limit $0). Expected: ▶️ Started, then `✅ Finished: hello-gpu in ...` and `Tesla T4: ... TFLOPS`; the run shows **Completed**.

> **If you see** the run go **Failed** right after approval with `ModuleNotFoundError: No module named 'jobs'` in its logs, **it means** the Modal container didn't get the `jobs/` folder (checked offline below, but only a real run proves it). Paste the log; nothing more is spent.
>
> **If you see** no Telegram message, **it means** the flow couldn't read the bot token. Check `ls -l ~/projects/lab-runtime/.env` (it should be a symlink to the repo's `.env`). The run still pauses; find it under **Runs** in the UI.

<details><summary>Example from this build</summary>

**1. How Modal will ship the job when a flow imports it.** `modal run jobs/hello_gpu.py` runs the file as a script. A flow imports it as `jobs.hello_gpu`, which Modal treats as a package. Checked offline (no Modal call):
```console
$ uv run python -c "import jobs.hello_gpu as h, jobs.train_template as t; ..."
jobs.hello_gpu FunctionSourceInfoType.PACKAGE /home/thovicheka/projects/cloud-ai-lab/jobs ['jobs']
jobs.train_template FunctionSourceInfoType.PACKAGE /home/thovicheka/projects/cloud-ai-lab/jobs ['jobs']
```
**Result:** ✅ Modal mounts the `jobs/` folder and imports `jobs.<name>` in the container. Not proven until a real run (step 7).

**2. Load each flow the way the worker does** (from the entrypoint path, with the repo not on `sys.path`)
```console
$ .venv/bin/python -I -c "... load_flow_from_entrypoint(ep) ..."
repo on sys.path: False
flows/hello_gpu.py:hello_gpu -> hello-gpu []
flows/train.py:train_mnist -> train-mnist ['run_name', 'steps', 'ckpt_every']
```
**Result:** ✅ Prefect adds the working directory while loading, so `from jobs...` and `from flows...` resolve.

**3. Tests**
```console
$ uv run pytest tests/test_flows.py -v
test_hello_gpu_estimate PASSED
test_train_estimate PASSED
test_paid_steps_never_retry PASSED
test_approval_waits_24_hours PASSED
test_nothing_runs_before_approval_then_approved_run PASSED
test_declined_never_calls_modal PASSED
test_resume_without_ticking_approve_declines PASSED
test_no_answer_times_out_without_modal PASSED
test_failed_gpu_step_is_not_retried PASSED
test_telegram_down_still_pauses_and_retries_messages PASSED
test_train_passes_parameters_after_approval PASSED
11 passed in 27.69s
$ uv run pytest -q
48 passed in 36.49s
```
**Result:** ✅

**4. Can the tests fail?** I temporarily made `hello-gpu` call Modal before asking, then ran the tests again:
```console
7 failed, 4 passed in 83.36s
```
**Result:** ✅ the gate tests catch it. The file was restored afterwards (`git diff` clean).

**5. The tests didn't touch the real server**
```console
$ uv run prefect flow ls          # only the flow from 4.2
│ d1851678-... │ hel… │ 2026-10-14 16:40:23 │
```
**Result:** ✅ no `hello-gpu` or `train-mnist` flow on :4200. The harness also asserts its API URL isn't `:4200`.

**6. Deny rules work in this session** (harmless commands; each would do nothing even if allowed)
```console
$ echo "glob check: prefect flow-run resume"
Permission to use Bash with command echo "glob check: prefect flow-run resume" has been denied.
$ uv run prefect deployment run --help
Permission to use Bash with command uv run prefect deployment run --help has been denied.
$ echo "glob check: from prefect.flow_runs import resume_flow_run"
Permission to use Bash ... has been denied.
```
**Result:** ✅ both the prefix rules and the `*` globs match. Side effect: an agent's shell command that only *mentions* these phrases (e.g. in an `echo` or a commit message) is blocked too.

**7. Lint** (`ruff`, line length 100 like the rest of the repo): new files clean. Two older `SIM117` findings remain in `tests/test_notify.py`; not touched.
</details>

- **Noticed, not done (out of scope):**
  - A paused run keeps its process alive and uses one of the worker's 2 slots (`--limit 2`) for up to 24 h. Two runs waiting for approval would hold back every other flow, including `hello`. Options: raise the limit (each paused run is ~90 MB), or switch to `suspend_flow_run` (design doc §5).
  - The gate can't stop an agent with shell access from running Python that imports a flow's task and calls Modal directly, or from calling the Prefect API under other names. The deny rules cover the obvious forms; Modal's $0 spending limit stays the backstop. 5.1 decides which credentials agents get.
  - `r2_hello` has no flow. You asked for `hello_gpu` and `train_template`; the design doc also lists `r2_hello` (< $0.01). Easy to add the same way.
  - Cost estimates are hard-coded constants next to each flow. `MAX_SECONDS` must be kept in step with `timeout=` in `jobs/*.py` by hand.

## 4.2 follow-up — Runtime worktree for the services
- **Branch:** `task/4.2-runtime-worktree` (from `main` at b71f207)
- **State:** blocked on 🧑 merge + `sudo` reinstall. Agent work done.
- **Why:** the services ran from `~/projects/cloud-ai-lab`, where agents switch branches, so flows ran whatever branch was checked out (open point from 4.2).
- **Done:**
  - `git worktree add ~/projects/lab-runtime main` + `uv sync` there (its own `.venv`, Prefect 3.8.8, 341 MB on disk).
  - `deploy/prefect-server.service` and `deploy/prefect-worker.service`: `WorkingDirectory` and `ExecStart` now use `/home/thovicheka/projects/lab-runtime`. Header comments explain the worktree and the update routine. `systemd-analyze verify` passes.
  - `hello` re-registered from `~/projects/lab-runtime`: its pull step now `cd`s into `lab-runtime`, so flow runs use the runtime code even before the services are reinstalled. One run: **Completed**.
- **Next:** after the human reinstalls: check both services run from `lab-runtime`, then run `hello` once more.
- **Human must:** merge `task/4.2-runtime-worktree`, then run the commands below *(on the server)*, in order. Nothing costs money.

**Update routine after each merge to `main`** (keeps the services on the latest `main`):
```bash
cd ~/projects/lab-runtime && git pull && uv sync && sudo systemctl restart prefect-server prefect-worker
```
Already-registered deployments read code from `lab-runtime` at each run, so a `git pull` is enough; only a *new* flow needs registering, and it must be registered from `~/projects/lab-runtime` (e.g. `cd ~/projects/lab-runtime && uv run python flows/<flow>.py`).

**Rules this adds for agents:**
- `main` is checked out in `lab-runtime`, so `git switch main` in `~/projects/cloud-ai-lab` fails (`'main' is already used by worktree`). Start task branches with `git fetch origin && git switch -c task/<id>-<name> origin/main`.
- Never edit, commit in, or switch branches in `~/projects/lab-runtime`. Only the update routine touches it.

**Reinstall** *(on the server, after merging)*:

1. Go to the runtime checkout:
```bash
cd ~/projects/lab-runtime
```

2. Get the merged unit files:
```bash
git pull
```

3. Make its `.venv` match `uv.lock`:
```bash
uv sync
```

4. Copy the new unit files over the installed ones:
```bash
sudo cp deploy/prefect-server.service deploy/prefect-worker.service /etc/systemd/system/
```

5. Make systemd read them:
```bash
sudo systemctl daemon-reload
```

6. Restart both services on the new paths:
```bash
sudo systemctl restart prefect-server prefect-worker
```

7. Check both run from `lab-runtime` (no `sudo`). Expected: `WorkingDirectory=/home/thovicheka/projects/lab-runtime` twice:
```bash
systemctl show prefect-server prefect-worker -p WorkingDirectory
```

8. Check both are `active (running)` and their `CGroup` lines show `lab-runtime/.venv/bin/prefect`:
```bash
systemctl status prefect-server prefect-worker --no-pager
```

9. Check the API answers (expected: `true`; give the server ~10 s after the restart):
```bash
curl -s http://127.0.0.1:4200/api/health
```

> **If you see** `status=203/EXEC` in step 8, **it means** `~/projects/lab-runtime/.venv/bin/prefect` is missing. Run step 3 again, then step 6.
>
> **If you see** `git pull` say `Not possible to fast-forward`, **it means** someone committed in `lab-runtime`. Stop and ask; don't reset it.

<details><summary>Example from this build</summary>

**1. Create the worktree**
```console
$ git worktree add ~/projects/lab-runtime main
Preparing worktree (checking out 'main')
HEAD is now at b71f207 Merge pull request #15 from thovicheka/task/4.2-prefect-setup
$ git worktree list
/home/thovicheka/projects/cloud-ai-lab  b71f207 [task/4.2-runtime-worktree]
/home/thovicheka/projects/lab-runtime   b71f207 [main]
```
**Result:** ✅

**2. `uv sync` in it**
```console
$ cd ~/projects/lab-runtime && uv sync
...
 + yarl==1.25.1
$ .venv/bin/prefect version | head -1
Version:              3.8.8
$ du -sh .venv
341M	.venv
```
**Result:** ✅

**3. Point the units at it, then check them**
```console
$ sed -i 's#/home/thovicheka/projects/cloud-ai-lab#/home/thovicheka/projects/lab-runtime#g' \
    deploy/prefect-server.service deploy/prefect-worker.service
$ systemd-analyze verify deploy/prefect-server.service deploy/prefect-worker.service
$ echo $?
0
```
**Result:** ✅ (`verify` also checks that the new `ExecStart` binary exists)

**4. The `hello` deployment still pointed at the old checkout**
```console
$ uv run prefect deployment inspect hello/hello
    'pull_steps': [{'prefect.deployments.steps.set_working_directory':
                    {'directory': '/home/thovicheka/projects/cloud-ai-lab'}}],
```
**Result:** ❌ **Cause:** `from_source(<local path>)` stores the path where it was registered. **Fix:** register again from the runtime checkout:
```console
$ cd ~/projects/lab-runtime && uv run python flows/hello.py
│ hello/hello │ applied │
$ uv run prefect deployment inspect hello/hello
                'directory': '/home/thovicheka/projects/lab-runtime'
$ uv run prefect deployment run hello/hello --watch
Created flow run 'slick-swallow'.
... prefect.flow-run.Completed * slick-swallow
Flow run finished successfully in 'Completed'.
$ uv run prefect flow-run logs e3fc86d3-...
... Executing deployment step: set_working_directory
... Hello from lab (ubuntu-4gb-sin-2, Python 3.12.3)
... Finished in state Completed()
```
**Result:** ✅ (the worker was still the old install; only the flow's working directory changed)

**5. `main` is now taken by the worktree**
```console
$ git switch main          # in ~/projects/cloud-ai-lab
fatal: 'main' is already used by worktree at '/home/thovicheka/projects/lab-runtime'
```
**Result:** ✅ expected; agents branch from `origin/main` instead (rules above).
</details>

- **Noticed, not done (out of scope):**
  - `lab-runtime` has no `.env` (it's git-ignored), and `lab/notify.py` reads `.env` from the checkout it runs in. Flows in 4.3 that call `notify()` or R2 will need it there. One option: `ln -s ~/projects/cloud-ai-lab/.env ~/projects/lab-runtime/.env` (one file of secrets, no copy). Your call, before 4.3.
  - `CLAUDE.md` still says to create branches "from main"; the `git switch -c ... origin/main` rule above could go there.
  - This branch and `task/4.2-record-install` both add to the top of this file's Summary, so the second merge will have a small conflict here (keep both paragraphs).
  - 4.4 (`docs/04-job-queue.md`) should include the worktree and the update routine.

## 4.2 — Set up Prefect (self-hosted)
- **Branch:** `task/4.2-prefect-setup` (merged, #15); install recorded on `task/4.2-record-install`
- **State:** done. Both services installed and running; `hello` ran **Completed** through them.
- **Done:**
  - 4.1 ticked; the pick (self-hosted) recorded in `decisions.md`, the design doc, and ROADMAP.
  - `uv add prefect` → 3.8.8 in `pyproject.toml` / `uv.lock`. 37 existing tests still pass.
  - `deploy/prefect-server.service`: `prefect server start` on `0.0.0.0:4200`, SQLite at `~/.prefect/prefect.db`, UI calls `http://lab:4200/api`, analytics off, `MemoryHigh=500M` / `MemoryMax=700M`, restarts on failure.
  - `deploy/prefect-worker.service`: process worker on work pool `lab` (created on first start), at most 2 flow runs at once, `MemoryHigh=700M` / `MemoryMax=900M`, always restarts.
  - `flows/hello.py`: a free smoke-test flow (no Modal) to check that the worker runs flows.
  - CLI profile on `lab` switched to `local` (`PREFECT_API_URL=http://127.0.0.1:4200/api`, `PREFECT_UI_URL=http://lab:4200`), so `prefect` commands talk to the service and never start a throwaway server.
  - Dry run of the exact `ExecStart` commands by hand (localhost only, port 4210, throwaway Prefect home in the scratchpad, now stopped): server healthy in 10 s, worker created pool `lab`, `hello` ran **Completed** twice. Memory: server **~245 MB**, worker **~97 MB** idle / **~186 MB** while running a flow. Details below.
  - 🧑 Human installed both units on `main` (all ✅): both `active (running)`, `/api/health` → `true`, UI opens on the laptop, pool `lab` **Ready**.
  - 🤖 `hello` deployed to pool `lab` and run once through the installed services: **Completed** in ~4 s. Memory on the real services: server **~235 MB**, worker **~79 MB** idle, **157 MB** peak while running `hello`; `free -h` shows **1.7 GiB available**, swap unused. 4.2 ticked in ROADMAP.
- **Next:** 4.3 (wrap the Modal jobs in flows).
- **Human must:** review and merge `task/4.2-record-install`. Nothing else.

<details><summary>Install steps the human ran (kept for reference)</summary>

**Before you start:** stay on this branch (or merge it first). The services run the repo's `.venv`; a plain `uv sync` on a branch without Prefect would remove it from the venv (`uv run` doesn't).

1. Go to the repo:
```bash
cd ~/projects/cloud-ai-lab
```

2. Copy both unit files into systemd's folder:
```bash
sudo cp deploy/prefect-server.service deploy/prefect-worker.service /etc/systemd/system/
```

3. Make systemd read them:
```bash
sudo systemctl daemon-reload
```

4. Start the server now and at every boot:
```bash
sudo systemctl enable --now prefect-server.service
```

5. Start the worker now and at every boot:
```bash
sudo systemctl enable --now prefect-worker.service
```

6. Check that both are `active (running)` (no `sudo` needed):
```bash
systemctl status prefect-server prefect-worker --no-pager
```

7. Check the API answers (expected output: `true`):
```bash
curl -s http://127.0.0.1:4200/api/health
```

8. Check the worker connected (expected: `Worker 'lab-worker' started!`). Your user isn't in the `adm` group, so reading system logs needs `sudo`:
```bash
sudo journalctl -u prefect-worker -n 20 --no-pager
```

9. *(On the laptop)* open **http://lab:4200**. Expected: the Prefect dashboard; **Work Pools** shows `lab` with one worker online.

> **If you see** `status=203/EXEC` in step 6, **it means** `.venv/bin/prefect` is missing (e.g. after a `uv sync` on another branch). Run `uv sync` on this branch, then `sudo systemctl restart prefect-server prefect-worker`.
>
> **If you see** the dashboard load but say it can't reach the API, **it means** the browser can't resolve `lab`. Check that `ping lab` works from the laptop (Tailscale MagicDNS).

</details>

<details><summary>Example from this build</summary>

**1. Add Prefect**
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

**2. Check setting names in this version.** `prefect config view --show-defaults` showed `PREFECT_SERVER_API_HOST='127.0.0.1'` and `PREFECT_SERVER_UI_API_URL='http://127.0.0.1:4200/api'`. With that default, the UI in the laptop's browser would call the laptop itself, so the unit sets it to `http://lab:4200/api`. **Result:** ✅

**3. Dry run of the server's `ExecStart`** (localhost, port 4210, throwaway `PREFECT_HOME`, in tmux)
```console
$ PREFECT_HOME=<scratch>/prefect-home PREFECT_SERVER_API_HOST=127.0.0.1 PREFECT_SERVER_API_PORT=4210 \
    PREFECT_SERVER_ANALYTICS_ENABLED=false .venv/bin/prefect server start
...
Check out the dashboard at http://127.0.0.1:4210
$ curl -s http://127.0.0.1:4210/api/health      # answered after 10 s
true
```
**Result:** ✅

**4. Dry run of the worker's `ExecStart`**
```console
$ PREFECT_API_URL=http://127.0.0.1:4210/api .venv/bin/prefect worker start --pool lab --type process \
    --name lab-worker --limit 2 --install-policy never
Worker 'lab-worker' started!
$ prefect work-pool ls
│ lab  │ process │ 7618b472-... │ None │
```
**Result:** ✅ the pool was created on first start.

**5. Register and run `hello`**
```console
$ uv run python flows/hello.py
│ hello/hello │ applied │
$ uv run prefect deployment run hello/hello
Created flow run 'legendary-bloodhound'.
# worker log:
... Executing deployment step: set_working_directory
... Hello from lab (ubuntu-4gb-sin-2, Python 3.12.3)
... Finished in state Completed()
```
**Result:** ✅ (run twice more for memory; both Completed)

**6. Memory** (summed RSS of each process and its children, sampled every 0.1 s)
```console
$ free -m          # before starting anything
Mem:   3814 total   1706 used   2107 available
server idle:                 peak tree RSS 248 MB, max processes 1
worker idle:                 peak tree RSS 97 MB, max processes 1
worker while running hello:  peak tree RSS 186 MB, max processes 2
python with prefect + modal imported: max RSS 95 MB
```
**Result:** ✅ ~0.35 GB idle for both, under the design estimate (0.4–0.8 GB). The `MemoryHigh`/`MemoryMax` limits leave ~2× headroom over this.

First attempt at step 6 ❌: a `pgrep -f` sampler printed `pgrep: only one pattern can be provided` because the pattern matched both the tmux `bash -c` wrapper and the Python process. Fix: a small Python sampler that walks `/proc` from one PID.

**7. Check the unit files**
```console
$ systemd-analyze verify deploy/prefect-server.service deploy/prefect-worker.service
$ echo $?
0
```
**Result:** ✅

**8. Point the CLI at the service**
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
**Result:** ✅ the profile switched despite the connection error.
</details>

<details><summary>Example from this build: install on the real server</summary>

**1–3. Copy the units, reload, enable** *(human, on `main` after #15)*
```console
$ sudo cp deploy/prefect-server.service deploy/prefect-worker.service /etc/systemd/system/
$ sudo systemctl daemon-reload
$ sudo systemctl enable --now prefect-server.service
Created symlink ... → /etc/systemd/system/prefect-server.service.
$ sudo systemctl enable --now prefect-worker.service
Created symlink ... → /etc/systemd/system/prefect-worker.service.
```
**Result:** ✅ both files in `/etc/systemd/system/`.

**4. Status and logs** *(human)*
```console
$ systemctl status prefect-server prefect-worker --no-pager
● prefect-server.service ... Active: active (running)   Memory: 229.7M (max: 700.0M)
● prefect-worker.service ... Active: active (running)   Memory: 79.1M (max: 900.0M)
$ sudo journalctl -u prefect-worker -n 20 --no-pager
... Worker 'lab-worker' started!
```
**Result:** ✅

**5. API and UI** *(human)*
```console
$ curl -s http://127.0.0.1:4200/api/health
true
```
On the laptop, http://lab:4200 opens; **Work Pools → lab**: Status **Ready**, Type **Process**, Last Polled less than a minute ago. **Result:** ✅

**6. Memory, idle** *(agent, ~7 min after start)*
```console
$ free -h
               total        used        free      shared  buff/cache   available
Mem:           3.7Gi       1.9Gi       197Mi       4.8Mi       1.9Gi       1.8Gi
Swap:          4.0Gi       512Ki       4.0Gi
$ systemctl status prefect-server prefect-worker --no-pager | grep Memory
     Memory: 234.7M (high: 500.0M max: 700.0M available: 265.2M peak: 235.2M)
     Memory: 79.1M (high: 700.0M max: 900.0M available: 620.8M peak: 79.6M)
```
**Result:** ✅ ~314 MB for both, close to the dry run (~345 MB).

**7. Deploy `hello` to pool `lab` and run it once** *(agent, CPU only, no Modal)*
```console
$ uv run python flows/hello.py
│ hello/hello │ applied │
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
**Result:** ✅ the installed worker picked it up within ~2 s; done ~4 s after creation.

**8. Memory, after the run**
```console
$ systemctl status prefect-server prefect-worker --no-pager | grep Memory
     Memory: 236.6M (high: 500.0M max: 700.0M available: 263.3M peak: 237.1M)
     Memory: 84.8M (high: 700.0M max: 900.0M available: 615.1M peak: 157.4M)
$ free -h
Mem:           3.7Gi       2.0Gi       178Mi       4.8Mi       1.9Gi       1.7Gi
Swap:          4.0Gi       512Ki       4.0Gi
```
**Result:** ✅ worker peaked at 157 MB with one flow run (dry run: ~186 MB), well under `MemoryHigh=700M`. 1.7 GiB still available.
</details>

- **Noticed, not done (out of scope):**
  - The services run from the working checkout that agents also switch branches in, so flows run whatever branch is checked out. A separate checkout of `main` (e.g. `~/projects/cloud-ai-lab-main`) for the services would isolate them; worth deciding before 4.3.
  - The UI has no login. Anyone on your tailnet can open it and press Resume. Fine while the tailnet is only your devices; Prefect's `PREFECT_SERVER_API_AUTH_STRING` (basic auth) is an option later.
  - Run history in SQLite grows without limit; 4.4 could document a cleanup.

## 4.1 — Job queue design
- **Branch:** `task/4.1-prefect-design` (merged); pick recorded on `task/4.2-prefect-setup`
- **State:** done, ticked. 🧑 picked **A, self-hosted** (2026-10-14); recorded in `decisions.md` and the design doc.
- **Done:** `docs/04-job-queue-design.md`: self-hosted Prefect server vs Prefect Cloud Hobby, side-by-side table, memory on this box (2.15 GB available now; A adds ~0.4–0.8 GB, B ~0.15–0.3 GB, **estimates**, not measured), how flows call Modal (flow on `lab`, ephemeral `app.run()` + `.remote()`), and the approval gate (`pause_flow_run` → Paused → Resume in the UI, 24 h timeout, Telegram message with cost). Recommendation: **self-hosted**. Prefect 3.8.8 (2026-10-06) is current.
- **Next:** 4.2 (service files, `uv add prefect`, `decisions.md` entry) once the human picks.
- **Human must:** nothing.
- **Noticed, not done (out of scope):**
  - The approval gate can be bypassed by anything with shell on `lab` (Prefect API `resume_flow_run`); 4.3 should add a deny rule for Prefect's resume command and 5.1 should decide agent credentials. Modal's $0 limit stays the backstop.
  - Memory figures are estimates; 4.2 should measure RSS after a day and a week and record it.

## 3.3 — Document Stage 3
- **Branch:** `task/3.3-document-stage-3` (from `main` after #12; also carries the 3.2 run record)
- **State:** done, waiting for the human's review and merge
- **Done:** `docs/03-experiment-tracking.md` (STYLE.md shape: goal, placeholders, prerequisites, 6 steps, verify, known limits, files). It covers the account, the API key, `.env`, the `wandb` Modal secret (with the "Skipping W&B?" note: create `wandb` with only `WANDB_MODE=disabled`, or training jobs won't start), the crash + resume run, adding W&B to a new job, and what the template logs. Real output comes from 3.1's `modal secret list` and 3.2's runs. README Stage 3 row → the doc; README status line: Stages 0–3 and 6 done, next Stage 4. 3.2 and 3.3 ticked in ROADMAP.
- **Not verified:** the "Skipping W&B?" path on Modal (the real secret exists). Modal's exact missing-secret error comes from its server, so the doc describes it without quoting it.
- **Next:** nothing.
- **Human must:** review and merge.

<details><summary>Steps and output from this build</summary>

**1. Branch from `main` after #12**
```console
$ git fetch -q origin && git log --oneline HEAD..origin/main   # on task/3.2-wandb-template
4761cc6 Merge pull request #12 from thovicheka/task/3.2-wandb-template
$ git switch -c task/3.3-document-stage-3 origin/main
Switched to a new branch 'task/3.3-document-stage-3'
```
**Result:** ✅ `task/3.2-wandb-template` was already fully merged (no commits missing from `main`), so the new branch starts from `main` and needs no rebase or merge.

**2. Check doc claims against the repo**
```console
$ uv run pytest -q
37 passed in 6.57s
$ uv run pytest -q --co tests/test_tracking.py
4 tests collected in 0.00s
$ sed -n '10,15p' pyproject.toml
[dependency-groups]
dev = [
    "moto[s3]>=5.2.4",
    "pytest>=9.1.1",
    "wandb==0.30.0",
]
```
**Result:** ✅ test counts and the `wandb` pin match the doc. Config keys, `LOG_EVERY = 50`, `N_SAMPLES = 16`, and the Telegram note were read from `jobs/train_template.py`.
</details>

## 3.2 — Log the template to W&B
- **Branch:** `task/3.2-wandb-template` (from `main` after #11; also carries the 3.1 record). Merged as #12. The run below is recorded on `task/3.3-document-stage-3`.
- **State:** done (2026-10-14). The human's crash + resume run passed and the human checked wandb.ai and Telegram. Ticked in ROADMAP.
- **Done:**
  - `lab/tracking.py`: `start_run(name, config, run_id=None)` starts or resumes (`resume="allow"`) a run in project `cloud-ai-lab`. No `WANDB_API_KEY` → prints `warning: WANDB_API_KEY not set; W&B logging is off for this run` and returns a disabled run that accepts every call. `run_id()` returns the id to store (a disabled run's id is random, so the checkpoint's is kept). `run_url()`.
  - `jobs/train_template.py`: uses the `wandb` secret; image adds `wandb==0.30.0` (released 2026-09-09). Logs config (+ project, GPU, R2 checkpoint folder), `train/loss` and `train/acc` every 50 steps, and `test/loss`, `test/acc`, `best_test_loss`, and 16 test images captioned `pred N / true M` at each checkpoint. Summary gets `best_test_loss` and `checkpoints`. The W&B run id is saved in the checkpoint as `wandb_id`; old checkpoints without it still load. On a crash the W&B run is closed as failed. The result and the Telegram Finished message include the W&B URL.
  - Train points are held until the next checkpoint and logged just before it's saved. W&B then never has steps past the last checkpoint, so a resumed run logs the redone steps (1001–1100 in the crash test) once, not twice.
  - `tests/test_tracking.py`: 4 tests (W&B offline, nothing sent). `.env.example`: `WANDB_API_KEY`. `wandb` added as a dev dependency (tests only).
- **Not tested:** the training loop with W&B (no torch here; CLAUDE.md forbids local training) and resuming against the real W&B server (offline mode keeps the id but doesn't upload). The first Modal run is their first real test.
- **Next:** nothing.
- **Human must:** nothing. The steps below are kept as a record.
  1. ✅ Run the crash/resume test with a new run name (from the repo root, on the server):
     ```bash
     modal run jobs/train_template.py --run-name wandb-1 --crash-at-step 1100
     modal run jobs/train_template.py --run-name wandb-1
     ```
     **Estimated cost:** T4 at $0.000164/s (modal.com/pricing, 2026-10-13). Each run ~1–2 min including start-up; the first one also rebuilds the image for `wandb` (a few minutes of CPU, < $0.01). **~$0.05 for both**, from the free credit (spend limit $0).
  2. Check:
     - Both runs print the same `W&B: https://wandb.ai/.../runs/<id>` line; the second also prints `resumed ... at step 1000`.
     - On wandb.ai, project `cloud-ai-lab` has **one** run `wandb-1`: `train/loss` and `test/loss` charts from step 50 to 3000 with no gap or double points around 1000–1100; `test/samples` images with captions; config shows `checkpoints: r2:cloud-ai-lab/mnist/checkpoints/wandb-1/`.
     - Telegram's Finished message ends with the W&B URL.
  3. If it passes, tick 3.2 in ROADMAP (or ask the agent to record it).

<details><summary>Steps and output from this build</summary>

**1. Pick and add the W&B client**
```console
$ curl -s https://pypi.org/pypi/wandb/json | ...   # newest releases
('2026-09-09T00:16:20', '0.30.0')
('2026-08-26T23:42:52', '0.29.0')
$ uv add --dev "wandb==0.30.0"
 + wandb==0.30.0
```
**Result:** ✅ 0.30.0 is the newest and over a month old.

**2. Check how wandb 0.30.0 behaves with W&B off and offline** (no key, nothing sent)
```console
disabled: NoopRun disabled attr True id ic4ki5a4 url None name n
offline: id abc123 name n project p disabled False url None cfg {'a': 1}
```
**Result:** ✅ A disabled run accepts `log`, `summary`, `config.update`, and `finish`, but its id is random, so it must not be saved in the checkpoint (hence `run_id()`). An offline run keeps the id it's given.

**3. First test run**
```console
$ uv run pytest -q tests/test_tracking.py
...
wandb.errors.errors.CommError: user is not logged in
3 failed, 1 passed in 6.04s
$ uv run pytest -q tests/test_tracking.py -k "not no_key"
3 passed, 1 deselected in 1.88s
```
**Result:** ❌
- **Error:** `CommError: user is not logged in` in the offline tests, but only after the no-key test ran.
- **Cause:** wandb keeps one setup per process that caches the environment from its first `init`. The no-key test's environment (no key, no `WANDB_MODE`) stuck for the later tests. Each one works on its own. A Modal job starts one run per process, so jobs aren't affected.
- **Fix:** an autouse fixture that calls `wandb.teardown()` after each test.
```console
$ uv run pytest -q
.....................................                                    [100%]
37 passed in 6.79s
$ uvx ruff@0.14.0 check --select E,F,W,B --line-length 100 lab jobs tests
All checks passed!
$ uv run python -c "import runpy; m = runpy.run_path('jobs/train_template.py'); print('app:', m['app'].name)"
app: train-template
```
**Result:** ✅

**4. Check the resume tests catch a broken resume** (temporarily pass `id=None` instead of `run_id`)
```console
$ uv run pytest -q tests/test_tracking.py
FAILED tests/test_tracking.py::test_resume_reuses_the_saved_id - AssertionErr...
FAILED tests/test_tracking.py::test_wandb_id_survives_the_checkpoint_round_trip
2 failed, 2 passed in 2.36s
$ # fix restored
$ uv run pytest -q
37 passed in 6.45s
```
**Result:** ✅

**5. Run on Modal with W&B** (run by the human, 2026-10-14; output trimmed)

The first attempt used a short flag:
```console
$ modal run jobs/train_template.py --run wandb-1 --crash-at-step 1100
Error: No such option '--run'. Did you mean '--run-name'?
```
**Result:** ❌
- **Error:** `No such option '--run'`.
- **Cause:** typo. The flag is `--run-name`.
- **Fix:** the full flag. The CLI rejected the command before contacting Modal, so nothing was billed.

Crash run:
```console
$ modal run jobs/train_template.py --run-name wandb-1 --crash-at-step 1100
Building image im-...
=> Step 2: RUN /.uv/uv pip install ... boto3==1.43.112 numpy==2.5.3 torch==2.14.1 torchvision==0.29.1 wandb==0.30.0
...
Built image im-... in 16.91s
...
no checkpoint at mnist/checkpoints/wandb-1/latest.pt; starting from step 0
wandb: Currently logged in as: vicheese (vicheese-cloud-ai-lab) to https://api.wandb.ai. ...
wandb: Syncing run wandb-1
W&B: https://wandb.ai/vicheese-cloud-ai-lab/cloud-ai-lab/runs/hy7wqqht
step   500/3000  train loss 0.0444  test loss 0.0504  test acc 0.9835  saved latest + best
step  1000/3000  train loss 0.0101  test loss 0.0364  test acc 0.9875  saved latest + best
wandb: uploading history steps 0-19, summary, console lines 0-2
...
wandb: Synced 5 W&B file(s), 32 media file(s), 0 artifact file(s) and 0 other file(s)
...
RuntimeError: simulated crash at step 1100 (--crash-at-step)
```
**Result:** ✅ The crash is intended. 20 history steps = train points 50–1000; steps 1050/1100 were held back (after the last checkpoint), as designed.

Checkpoints in R2 between the two runs (read-only check by the agent):
```console
$ rclone ls r2:cloud-ai-lab/mnist/checkpoints/wandb-1/
  5074261 best.pt
  5074261 latest.pt
```
**Result:** ✅ exactly two objects.

Resume run:
```console
$ modal run jobs/train_template.py --run-name wandb-1
resumed mnist/checkpoints/wandb-1/latest.pt at step 1000 (best test loss 0.0364)
wandb: Resuming run wandb-1
W&B: https://wandb.ai/vicheese-cloud-ai-lab/cloud-ai-lab/runs/hy7wqqht
step  1500/3000  train loss 0.0060  test loss 0.0275  test acc 0.9903  saved latest + best
step  2000/3000  train loss 0.0301  test loss 0.0281  test acc 0.9906  saved latest
step  2500/3000  train loss 0.0044  test loss 0.0279  test acc 0.9901  saved latest
step  3000/3000  train loss 0.0014  test loss 0.0240  test acc 0.9929  saved latest + best
...
wandb: Synced 5 W&B file(s), 64 media file(s), 0 artifact file(s) and 0 other file(s)
            run: wandb-1
 steps_this_run: 2000
   resumed_from: 1000
 best_test_loss: 0.024
  train_seconds: 26.8
    checkpoints: r2:cloud-ai-lab/mnist/checkpoints/wandb-1/
          wandb: https://wandb.ai/vicheese-cloud-ai-lab/cloud-ai-lab/runs/hy7wqqht
Stopping app - local entrypoint completed.
```
**Result:** ✅ The same W&B run id `hy7wqqht` in both runs ("Resuming run wandb-1"). Resumed at step 1000; test loss 0.0240, acc 99.29%; 26.8 s of training. Estimated cost ~$0.01–0.02 per run (T4 at $0.000164/s), from free credit.

**6. Checked on wandb.ai and Telegram** (reported by the human, 2026-10-14)
- wandb.ai: run `wandb-1` has continuous charts 0–3000. `test/samples` shows digit images with predicted/true captions. The config shows the checkpoint path.
- Telegram: ▶️ Started, ❌ Failed, ▶️ Started, ✅ Finished; the Finished message has the W&B link.

**Result:** ✅ "done when" (a run shows charts on wandb.ai) met.
</details>

## 3.1 — W&B account
- **Branch:** recorded on `task/3.2-wandb-template` (3.1 is a 🧑 task; no code)
- **State:** done (2026-10-14, by the human). Ticked in ROADMAP.
- **Done:** W&B account; `WANDB_API_KEY` in `.env` on the server; Modal secret `wandb` created.
- **Next:** 3.2.
- **Human must:** nothing.

<details><summary>Steps and output from this build</summary>

**1. Check the Modal secret exists** (read-only; `.env` itself isn't read, per CLAUDE.md)
```console
$ uv run modal secret list
┃ Name  ┃ Created at           ┃ Created by   ┃ Last used at         ┃
│ wandb │ 2026-10-14 07:15 UTC │ <workspace>  │ -                    │
│ r2    │ 2026-10-14 04:45 UTC │ <workspace>  │ 2026-10-14 05:07 UTC │
```
**Result:** ✅ The `.env` key is as reported by the human.
</details>

## 2.6 — Doc gaps (not a ROADMAP task; asked for directly)
- **Branch:** `task/2.6-doc-gaps` (from `main` after #10)
- **State:** done, waiting for the human's review and merge
- **Done:**
  1. `.claude/settings.json`: added `Bash(uv run modal run:*)`, `Bash(uv run modal deploy:*)`, `Bash(uv run modal serve:*)` to `permissions.deny`.
  2. `docs/02-gpu-compute.md`: step 1 now names the real path (Settings → Usage & billing → Usage limit tab → Spend limit, $0, $30/month free credit, card not charged); step 3's example is the real `modal token new` output.
  3. `docs/06-notifications.md`: example block for `--test` with real Telegram (all four messages arrived; token and chat ID masked).
  4. `docs/06-notifications.md`: a "Not tested yet" line for ⏹️ Stopped under the message table (the known-limits section already had one).
  5. README status line: Stages 0, 1, 2, 6 done; next is Stage 3 (W&B).
- **Next:** nothing.
- **Human must:** review and merge.

<details><summary>Steps and output from this build</summary>

**1. Validate the settings file and test the new rule** (with a harmless command, so nothing happens even if it isn't blocked)
```console
$ python3 -m json.tool .claude/settings.json >/dev/null && echo "JSON valid"
JSON valid
$ uv run modal run --help
Permission to use Bash with command uv run modal run --help has been denied.
```
**Result:** ✅ blocked in the same session that added the rule.

**2. Doc values** come from the human (spend-limit path, `modal token new` output, `--test` results on the phone). The `modal token new` login link isn't shown: it's single-use.
**Result:** ✅
</details>

## 2.5 — Document Stage 2
- **Branch:** `task/2.5-document-stage-2` (built on `task/2.4-record-resume-test`; merge that first)
- **State:** done, waiting for the human's review and merge
- **Done:** `docs/02-gpu-compute.md` (STYLE.md shape: goal, placeholders, prerequisites, 8 steps, verify, cost and safety). Every failure from this build is in it with error, cause, and fix: `python-dotenv` missing, `DeserializationError` from `torch.__version__`, the NumPy warning, `/tmp/ckpt` missing. Real output comes from the runs recorded under 2.2–2.4 and from `modal app logs` (read-only). README Stage 2 row → the doc; README status line updated. `decisions.md`: new "Stage 2 job design" section (why local entrypoint on the server, two checkpoints, `retries=0`, no default run name). 2.5 ticked in ROADMAP.
- **Not verified:** the exact name of Modal's billing settings page, so step 1 describes it instead of naming it. `modal token new`'s output wasn't recorded, so step 3 shows the check instead. (Both filled in with the human's real values in `task/2.6-doc-gaps`.)
- **Next:** nothing.
- **Human must:** review and merge. The doc links to `06-notifications.md`, which arrives with 6.3.

## 6.3 — Document Stage 6
- **Branch:** `task/6.3-document-notifications` (built on `task/2.5-document-stage-2`; merge that first)
- **State:** done, waiting for the human's review and merge
- **Done:** `docs/06-notifications.md` (STYLE.md shape: goal, placeholders, prerequisites, 7 steps, verify, known limits). Covers creating the bot, the chat ID, `.env`, a one-message test, the four-message self-test, wiring `notify_job` into a job, and troubleshooting for each `notify:` warning. Every claim checked against `lab/notify.py`. Real output: the unconfigured self-test (6.2 step 4) and the Telegram messages from real jobs (2.2, 2.4). README Stage 6 row → the doc. 6.3 ticked in ROADMAP.
- **Not recorded in this build:** BotFather's and @userinfobot's replies and a configured `--test` run, so those steps have no example block. (The `--test` run was added in `task/2.6-doc-gaps`.)
- **Next:** nothing.
- **Human must:** review and merge.

## 6.2 — Notifier
- **Branch:** `task/6.2-notifier` (built on `task/2.4-train-template`; merge 2.2 → 2.3 → 2.4 → 6.2)
- **State:** done (2026-10-14). 6.1 done by the human (bot token and chat ID in `.env`); real jobs sent Started, Failed, and Finished. 6.1 and 6.2 ticked in ROADMAP.
- **Done:** `lab/notify.py`: `notify(text)` sends to Telegram, and the `notify_job(name, gpu=...)` context manager sends ▶️ Started / ✅ Finished / ❌ Failed / ⏹️ Stopped with duration and estimated GPU cost. It never raises: unconfigured or unreachable Telegram prints a warning and the job carries on. Errors never print the token. Standard library only. All three jobs (`hello_gpu`, `r2_hello`, `train_template`) wrap their remote call with it in the local entrypoint, which runs on the server, so Modal needs no Telegram secret. 16 new tests (32 total). Telegram keys added to `.env.example`.
- **Next:** nothing.
- **Human must:** nothing. The steps below are kept as a record.
  1. ✅ Finish **6.1**: create a bot with @BotFather (`/newbot`), then send your bot any message (bots can't message you first). Get your chat ID from @userinfobot. Add both to `.env` (keys in `.env.example`).
  2. Free test, no GPU or Modal (runs a fake job that finishes and one that fails):
     ```bash
     uv run python -m lab.notify --test
     ```
     **Cost:** $0. **Expected:** four Telegram messages: Started, Finished, Started, Failed.
  3. Optional real-job check (after 2.1 + 2.3): `modal run jobs/train_template.py --run-name notify-1 --crash-at-step 600`, then the same command without the flag. Expect Started → Failed, then Started → Finished. **Estimated cost: ~$0.05.**

<details><summary>Steps and output from this build</summary>

**1. Check whether 6.1 is done**
```console
$ test -f .env && echo ".env exists" || echo "no .env"
no .env
```
**Result:** ❌ No bot token yet. The notifier was written and tested with Telegram's API faked.

**2. Tests (fake Telegram, nothing sent)**
```console
$ uv run pytest -q
................................                                         [100%]
32 passed in 3.95s
```
**Result:** ✅ Covers: the request sent, truncation to 4096 chars, no config, HTTP 401 / non-JSON 502 / DNS failure / timeout (none raise, none print the token), cost and duration formatting, finished / failed (re-raises) / Ctrl-C messages, the job still runs when Telegram is down, the `--test` self-test sends all three kinds, `.env` parsing.

**3. First version used `python-dotenv`**
**Result:** ❌ (caught by reading, before any run)
- **Error (would have been):** `ModuleNotFoundError: No module named 'dotenv'` on every `modal run`.
- **Cause:** ROADMAP 2.1 installs the CLI with `uv tool install modal`, which runs the local entrypoint in the tool's own environment, without the project's packages.
- **Fix:** removed `python-dotenv`; a 15-line standard-library `.env` reader instead. Checked under bare system Python:
```console
$ python3 -I -c "import sys; sys.path.insert(0, '.'); from lab.notify import notify_job; print('lab.notify imports under bare system python', sys.version.split()[0])"
lab.notify imports under bare system python 3.12.3
```
**Result:** ✅

**4. Self-test with no Telegram config** (real run; shows the graceful fallback)
```console
$ uv run python -m lab.notify --test
notify: TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID not set; not sent: ▶️ Started: notify test: a job that finishes (T4)
notify: TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID not set; not sent: ✅ Finished: notify test: a job that finishes in 0m 01s, ~$0.00 on T4
this is the note line
notify: TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID not set; not sent: ▶️ Started: notify test: a job that fails (T4)
notify: TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID not set; not sent: ❌ Failed: notify test: a job that fails after 0m 01s, ~$0.00 on T4
RuntimeError: simulated failure (this is expected)
$ echo $?
0
```
**Result:** ✅ The job flow completes, and the messages print instead of being sent.

**5. Real messages from real jobs** (reported by the human, 2026-10-14)
- `hello_gpu` re-run: `✅ Finished: hello-gpu in 0m 09s, ~$0.00 on T4` / `Tesla T4: 3.84 TFLOPS`
- `train_template --crash-at-step 1100`: ▶️ Started, then ❌ Failed
- `train_template` resume: ✅ Finished

**Result:** ✅ all three kinds of message arrived from real Modal jobs, which is 6.2's "done when".

**6. Known limits**
- Duration is measured on the server and includes container start-up, so the cost slightly overestimates GPU time. CPU and memory charges (a few %) aren't counted.
- Untested until a real run: whether `modal run` delivers Ctrl-C to the entrypoint as `KeyboardInterrupt` (→ ⏹️ Stopped), or cancels it some other way (then no stop message).
- With `modal run --detach`, if the server-side client exits, the job keeps going but no Finished message arrives. Stage 4 (Prefect) is the place to fix that.
</details>
