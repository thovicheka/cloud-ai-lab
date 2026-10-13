# Status

Live progress for agent work. The agent updates this after every step and pushes it (see "Working unattended" in [`CLAUDE.md`](../CLAUDE.md)). Task definitions live in [`ROADMAP.md`](ROADMAP.md).

## Summary

**Run of 2026-10-13: tasks 2.2, 2.3, 2.4, 6.2.** All agent work is finished. Each task is blocked only on a human step: Modal account (2.1), the R2 secret, a Telegram bot (6.1), and running the paid jobs. No money was spent and no Modal job was run.

**Branches are stacked; review and merge in this order:** `task/2.2-hello-gpu` → `task/2.3-modal-r2` → `task/2.4-train-template` → `task/6.2-notifier`. Each builds on the one before (shared `pyproject.toml`, `lab/`, this file).

| Task | Agent work | Tested | Blocked on |
|---|---|---|---|
| 2.2 Hello-GPU | `jobs/hello_gpu.py`, uv project | loads ✅ | 2.1, a GPU run |
| 2.3 R2 from Modal | `lab/storage.py`, `jobs/r2_hello.py`, `.env.example` | 10 tests vs fake S3 ✅ | 2.1, `r2` secret, a CPU run |
| 2.4 Training template | `lab/checkpoints.py`, `jobs/train_template.py` | checkpoint logic: 6 tests ✅; training loop: not run (no local training) | 2.1, `r2` secret, 2 GPU runs |
| 6.2 Notifier | `lab/notify.py`, wired into all jobs | 16 tests vs fake Telegram ✅; self-test unconfigured ✅ | 6.1 |

**What the human does, in order** (details under each task below; run everything on the server from `~/projects/cloud-ai-lab`):
1. **2.1:** sign up at modal.com, **set a monthly spending limit**, then `uv tool install modal` and `modal token new`.
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
- `.claude/settings.json` denies `modal run`, but not `uv run modal run`. Add `Bash(uv run modal run:*)` if you want the same guard on that form.

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
- **State:** blocked: code written and checked locally; can't run until 2.1 is done
- **Done:** `uv` project (`pyproject.toml`, `uv.lock`, Python 3.12, `modal` 1.6.1). `jobs/hello_gpu.py`: a T4 function that prints `nvidia-smi`, times a 4096×4096 PyTorch matmul, and returns GPU name, torch/CUDA versions, ms and TFLOPS. 5-minute hard timeout. Cost estimate in the file's docstring.
- **Next:** the human runs it (below).
- **Human must:**
  1. Finish **2.1**: sign up for Modal, **set a monthly spending limit**, then on the server:
     ```bash
     uv tool install modal    # the `modal` command; not installed yet
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

**5. Run on a GPU:** not done. Needs 2.1 and the human (`modal run` costs money).
</details>

## 2.3 — R2 from Modal
- **Branch:** `task/2.3-modal-r2` (built on `task/2.2-hello-gpu`; merge 2.2 first)
- **State:** blocked: code written and tested offline; the real run needs 2.1 and the Modal secret
- **Done:** `lab/storage.py` (`r2_key`, `upload`, `download`, `list_keys`, `exists`; credentials from env vars; keys laid out as `<project>/<datasets|checkpoints|runs>/...`). `jobs/r2_hello.py`: a CPU-only Modal job that writes `hello/runs/<UTC stamp>/hello.txt` and lists it. 10 tests in `tests/test_storage.py` against an in-memory fake S3 (moto). `.env.example` with the R2 keys.
- **Next:** the human adds the secret and runs the job (below).
- **Human must:**
  1. Finish **2.1** (see 2.2).
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

**5. Write to real R2 from Modal:** not done. Needs 2.1, the secret, and the human.
</details>

## 2.4 — Checkpointed training template
- **Branch:** `task/2.4-train-template` (built on `task/2.3-modal-r2`; merge 2.2 → 2.3 → 2.4)
- **State:** blocked: code written, checkpoint logic tested offline; the GPU run needs 2.1 + the `r2` secret (2.3)
- **Done:** `lab/checkpoints.py` (`RunCheckpoints`: `latest.pt` + `best.pt` per run, overwritten in place, so only 2 objects ever; `restore()` for resuming). `jobs/train_template.py`: small CNN on MNIST (T4); evaluates and checkpoints every 500 steps; resumes weights, optimizer, step, best loss, RNG and data position from `latest.pt`; `--crash-at-step N` simulates a lost GPU. 6 new tests in `tests/test_checkpoints.py` (16 total).
- **Not tested:** the training loop itself. CLAUDE.md forbids local training and torch isn't installed here, so the first Modal run is its first real test.
- **Next:** the human runs the resume test (below).
- **Human must:**
  1. Finish 2.1 and 2.3's secret.
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

**5. GPU run and resume test:** not done. Needs 2.1, the `r2` secret, and the human.
</details>

## 6.2 — Notifier
- **Branch:** `task/6.2-notifier` (built on `task/2.4-train-template`; merge 2.2 → 2.3 → 2.4 → 6.2)
- **State:** blocked: code written and tested with a fake Telegram API; real messages need 6.1
- **Done:** `lab/notify.py`: `notify(text)` sends to Telegram, and the `notify_job(name, gpu=...)` context manager sends ▶️ Started / ✅ Finished / ❌ Failed / ⏹️ Stopped with duration and estimated GPU cost. It never raises: unconfigured or unreachable Telegram prints a warning and the job carries on. Errors never print the token. Standard library only. All three jobs (`hello_gpu`, `r2_hello`, `train_template`) wrap their remote call with it in the local entrypoint, which runs on the server, so Modal needs no Telegram secret. 16 new tests (32 total). Telegram keys added to `.env.example`.
- **Next:** the human sets up the bot (6.1) and runs the free self-test.
- **Human must:**
  1. Finish **6.1**: create a bot with @BotFather (`/newbot`), then send your bot any message (bots can't message you first). Get your chat ID from @userinfobot. Add both to `.env` (keys in `.env.example`).
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

**5. Known limits**
- Duration is measured on the server and includes container start-up, so the cost slightly overestimates GPU time. CPU and memory charges (a few %) aren't counted.
- Untested until a real run: whether `modal run` delivers Ctrl-C to the entrypoint as `KeyboardInterrupt` (→ ⏹️ Stopped), or cancels it some other way (then no stop message).
- With `modal run --detach`, if the server-side client exits, the job keeps going but no Finished message arrives. Stage 4 (Prefect) is the place to fix that.
</details>
