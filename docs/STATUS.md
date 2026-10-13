# Status

Live progress for agent work. The agent updates this after every step and pushes it (see "Working unattended" in [`CLAUDE.md`](../CLAUDE.md)). Task definitions live in [`ROADMAP.md`](ROADMAP.md).

## Summary

*(Written when all given tasks are done or blocked: what finished, what's blocked, and what the human must do, in order.)*

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
- The default `--run-name` is required on purpose: rerunning with the same name resumes, and a new name starts fresh. A finished run rerun with its name does nothing and returns its result.

**5. GPU run and resume test:** not done. Needs 2.1, the `r2` secret, and the human.
</details>
