# Stage 2 — GPU compute (Modal)

**What you'll have working by the end:** from the server, one command rents a GPU on Modal, runs a training job that checkpoints to R2, and stops by itself. If the GPU is lost mid-run, running the same command again resumes from the last checkpoint.

**Status:** ✅ Stage 2 complete (tasks 2.1–2.4; this doc is task 2.5).

**How to read this guide:** instructions use placeholders like `<run-name>`; replace them with your own values. After key steps, an **Example from this build** block shows the real commands and output from the author's setup:

| Placeholder | In this build |
|---|---|
| `<username>` (server user) | `thovicheka` |
| `<bucket-name>` | `cloud-ai-lab` |
| `<project>` (R2 folder for a training project) | `mnist` |
| `<run-name>` | `try-1` |
| GPU | `T4` |
| Modal app and image IDs, R2 keys, emails | kept private (`ap-***`, `im-***`) |

**Which machine:** every command runs **on the server**, from the repo root `~/projects/cloud-ai-lab`. The only exceptions are the Modal website (step 1) and the login link (step 3), which you open in your laptop's browser.

## Prerequisites
- [Stage 1](01-server-setup.md) done: the server, `uv`, and the `rclone` remote `r2` pointing at your bucket (Part E).
- This repo cloned at `~/projects/cloud-ai-lab` on the server.
- A GitHub account to sign up to Modal with.
- Optional, for job messages on your phone: a Telegram bot ([Stage 6](06-notifications.md)). Jobs run fine without it.

Why Modal (and not RunPod or Vast.ai) for batch jobs: see [decisions.md](decisions.md#gpu-compute-modal--runpod-over-vastai).

---

## Steps

### 1. Create a Modal account and set a spending limit *(laptop browser)*
1. Sign up at [modal.com](https://modal.com) with GitHub.
2. In the Modal dashboard, open **Settings → Usage & billing → Usage limit** tab, and set **Spend limit**.

*What it does:* the Starter plan includes a free monthly credit ($30/month in October 2026; check modal.com/pricing). A spend limit of **$0** means jobs run only on that credit and stop when it runs out; your card is never charged.

> **Adapting:** set a higher limit once you train for real. A T4 costs $0.000164/s (~$0.59/h; modal.com/pricing, 2026-10-13).

<details><summary>Example from this build</summary>

Settings → Usage & billing → **Usage limit** tab → **Spend limit: $0**. Jobs use only the $30/month free credit; the card is not charged.

**Result:** ✅
</details>

### 2. Install the Modal CLI *(on the server)*
```bash
uv tool install modal --with python-dotenv
```
*What it does:* installs the `modal` command into its own environment under `~/.local/bin`. `python-dotenv` is needed by `modal secret create --from-dotenv` (step 6).

> **If you see** an error about `dotenv` when running `modal secret create --from-dotenv`, the CLI was installed without it. Re-run the command above; it adds the package to the existing install.

<details><summary>Example from this build</summary>

```console
$ uv tool install modal --with python-dotenv
$ uv tool list --show-with
modal v1.6.1 [with: python-dotenv]
- modal
```
**Result:** ✅ The first install was a plain `uv tool install modal`, which failed later at step 6. **Cause:** `--from-dotenv` imports `python-dotenv`, which the CLI doesn't install by default. **Fix:** the command above.
</details>

### 3. Log the CLI in *(on the server, link opened on the laptop)*
```bash
modal token new
```
*What it does:* prints a login link. Open it on your laptop and approve. The token is saved to `~/.modal.toml` on the server (a secret; never commit or share it).

> **If** a browser tries to open on the server or nothing happens, that's expected on a headless machine. Copy the printed link to your laptop.

<details><summary>Example from this build</summary>

```console
$ modal token new
...
Web authentication finished successfully!
Token is connected to the thovicheka38 workspace.
Verifying token against https://api.modal.com
Token verified successfully!
Token written to /home/thovicheka/.modal.toml in profile thovicheka38.
```
**Result:** ✅ (the login link, shown before `...`, is single-use and left out).
</details>

### 4. Run the hello-GPU job *(on the server)*
```bash
modal run jobs/hello_gpu.py
```
*What it does:* builds a container image with PyTorch (a few minutes the first time, then cached), rents a T4, prints `nvidia-smi`, times a 4096×4096 matrix multiply, prints the result, and stops. The function has a 5-minute timeout, so a hung job can't bill for long. **Cost:** under $0.05 the first time; about $0.002 after that.

Two things to know about every Modal job here:
- **The `@app.function` part runs on Modal; the `@app.local_entrypoint()` part runs on the server**, inside the CLI's own environment, which has no PyTorch. So a function must **return plain Python values** (`str`, `int`, `float`, lists, dicts), never torch objects.
- **Install `numpy` next to `torch` in the image**, or torch prints a `Failed to initialize NumPy` warning.

> **If you see** `DeserializationError: Deserialization failed because the 'torch' module is not available in the local environment`, the function returned a torch object. A common one is `torch.__version__`, which looks like a string but is a `TorchVersion`. Wrap such values in `str()` / `float()` / `int()`.

<details><summary>Example from this build</summary>

First run (container log, from `modal app logs ap-***`):
```console
$ modal run jobs/hello_gpu.py
...
Built image im-*** in 13.32s
UserWarning: Failed to initialize NumPy: No module named 'numpy' ...
+-----------------------------------------------------------------------------------------+
| NVIDIA-SMI 610.57.04              KMD Version: 610.57.04     CUDA UMD Version: 13.3     |
...
|   0  Tesla T4                       On  |   00000000:00:1C.0 Off |                    0 |
| N/A   35C    P8             14W /   70W |       3MiB /  15360MiB |      0%      Default |
...
DeserializationError: Deserialization failed because the 'torch' module is not available in the local environment.
```
**Result:** ❌ the job ran on a Tesla T4, but its result never reached the server.
- **Error:** `DeserializationError ... 'torch' module is not available in the local environment`
- **Cause:** the returned dict held `torch.__version__`, a `TorchVersion` object. Modal pickles the result in the container and unpickles it on the server, which has no torch.
- **Fix:** `str(torch.__version__)` (and `str()` around the other torch values). Also added `numpy` to the image for the warning.

Re-run after the fix:
```console
$ modal run jobs/hello_gpu.py
...
|   0  Tesla T4                       On  |   00000000:E7:00.0 Off |                    0 |
...
Stopping app - local entrypoint completed.
```
Telegram (Stage 6):
```text
✅ Finished: hello-gpu in 0m 09s, ~$0.00 on T4
Tesla T4: 3.84 TFLOPS
```
**Result:** ✅ GPU name returned, no NumPy warning, and the job stopped by itself. 9 s ≈ $0.0015.
</details>

### 5. Put the R2 keys in `.env` *(on the server)*
```bash
cp .env.example .env && chmod 600 .env
nano .env    # fill in the R2_ lines: same endpoint and token as the rclone r2 remote
```
*What it does:* `.env` is git-ignored and readable only by you. `lab/storage.py` reads the `R2_` keys from it (on the server) or from a Modal secret (in a job).

| Key | Value |
|---|---|
| `R2_ENDPOINT_URL` | `https://<account-id>.r2.cloudflarestorage.com` |
| `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY` | the R2 API token from Stage 1 (E1c) |
| `R2_BUCKET` | `<bucket-name>` |

### 6. Store the R2 keys as a Modal secret *(on the server)*
```bash
grep '^R2_' .env > ~/r2.env && modal secret create r2 --from-dotenv ~/r2.env; rm ~/r2.env
```
*What it does:* copies only the `R2_` lines into a temporary file, uploads them as the Modal secret `r2`, and deletes the file. Jobs get the keys as environment variables with `secrets=[modal.Secret.from_name("r2")]`. Going through a file keeps keys out of your shell history; filtering to `R2_` keeps other keys (like Telegram's) out of Modal.

> **If you see** an error about `dotenv`, see step 2.

<details><summary>Example from this build</summary>

```console
$ modal secret list
│ Name │ Created at           │ ...
│ r2   │ 2026-10-14 04:45 UTC │ ...
```
**Result:** ✅ (after reinstalling the CLI with `python-dotenv`, step 2).
</details>

### 7. Write to R2 from Modal *(on the server)*
```bash
modal run jobs/r2_hello.py
```
*What it does:* a CPU-only job (no GPU) that writes `hello/runs/<UTC time>/hello.txt` to your bucket and lists it. **Cost:** a few seconds of CPU, under $0.01.

> **If** a job can't find the `lab` package (an import error naming `lab`), run the command from the repo root. `modal run` looks for `lab` in the current folder.

<details><summary>Example from this build</summary>

```console
$ modal run jobs/r2_hello.py
...
Built image im-*** in 4.75s
uploaded r2:cloud-ai-lab/hello/runs/20261014T045622Z/hello.txt
Stopping app - local entrypoint completed.
$ rclone ls r2:cloud-ai-lab/hello/runs/
       53 20261014T045622Z/hello.txt
```
**Result:** ✅ written from Modal, visible from the server.
</details>

### 8. Train with checkpoints, crash, and resume *(on the server)*
`jobs/train_template.py` trains a small CNN on MNIST on a T4. Every 500 steps (`--ckpt-every`) it evaluates on the test set and saves to R2:

```text
r2:<bucket-name>/<project>/checkpoints/<run-name>/latest.pt   every save
r2:<bucket-name>/<project>/checkpoints/<run-name>/best.pt     when test loss improves
```

Both files are overwritten in place, so a run never stores more than two. Started again with the same `--run-name`, the job resumes from `latest.pt`: weights, optimizer, step, best loss, random state, and position in the data.

Crash on purpose, as if the GPU were lost:
```bash
modal run jobs/train_template.py --run-name <run-name> --crash-at-step 1100
```
*What it does:* trains, saves at steps 500 and 1000, then raises an error at step 1100.

Run the same command without the crash flag:
```bash
modal run jobs/train_template.py --run-name <run-name>
```
*What it does:* finds `latest.pt`, prints `resumed ... at step 1000`, and trains on to step 3000. **Cost:** each run is about a minute on a T4 including start-up: ~$0.05 for both.

> **If you see** `RuntimeError: Parent directory /tmp/ckpt does not exist.` at the first save, the job is from before the fix. The checkpoint folder must be created before `torch.save`: `os.makedirs(os.path.dirname(path), exist_ok=True)`. `RunCheckpoints.restore()` now also creates it.
>
> **If** the second run prints `no checkpoint at ...; starting from step 0`, the `--run-name` differs from the first run's, or the first run crashed before its first save (step 500).
>
> **If** it prints `warning: config changed since the checkpoint`, you changed a setting like `--ckpt-every` between runs. It still resumes; the warning shows old → new.

> **Adapting:** to train your own model, copy the file and change `PROJECT`, `load_data()`, and `make_net()`. For a bigger GPU, change `GPU = "T4"` (e.g. `"L4"`, `"A100-40GB"`), and raise `timeout` for long runs.

<details><summary>Example from this build</summary>

First attempt (container log):
```console
$ modal run jobs/train_template.py --run-name try-1 --crash-at-step 1100
...
no checkpoint at mnist/checkpoints/try-1/latest.pt; starting from step 0
...
  File "/root/train_template.py", line 141, in train
    torch.save(
...
RuntimeError: Parent directory /tmp/ckpt does not exist.
```
**Result:** ❌
- **Error:** `RuntimeError: Parent directory /tmp/ckpt does not exist.` at the first save (step 500).
- **Cause:** `/tmp/ckpt` was only created when a checkpoint was downloaded. A fresh run has nothing to download, so the folder never existed, and `torch.save` doesn't create folders.
- **Fix:** create the folder before restoring or saving. Nothing had reached R2, so the same run name was reused.

Crash run after the fix:
```console
$ modal run jobs/train_template.py --run-name try-1 --crash-at-step 1100
...
no checkpoint at mnist/checkpoints/try-1/latest.pt; starting from step 0
step   500/3000  train loss 0.0476  test loss 0.0499  test acc 0.9834  saved latest + best
step  1000/3000  train loss 0.0118  test loss 0.0373  test acc 0.9876  saved latest + best
RuntimeError: simulated crash at step 1100 (--crash-at-step)
Stopping app - uncaught exception raised locally: RuntimeError('simulated crash at step 1100 (--crash-at-step)').
```
**Result:** ✅ saved twice, then crashed as asked.

Resume:
```console
$ modal run jobs/train_template.py --run-name try-1
...
resumed mnist/checkpoints/try-1/latest.pt at step 1000 (best test loss 0.0373)
step  1500/3000  train loss 0.0091  test loss 0.0290  test acc 0.9895  saved latest + best
step  2000/3000  train loss 0.0231  test loss 0.0281  test acc 0.9910  saved latest + best
step  2500/3000  train loss 0.0140  test loss 0.0231  test acc 0.9921  saved latest + best
step  3000/3000  train loss 0.0028  test loss 0.0217  test acc 0.9933  saved latest + best
...
 best_test_loss: 0.0217
  train_seconds: 23.2
```
**Result:** ✅ resumed at step 1000 instead of starting over; 2000 steps in 23 s.
</details>

## Verify it worked
```bash
rclone ls r2:<bucket-name>/<project>/checkpoints/<run-name>/
```
Expected: exactly two files, `best.pt` and `latest.pt`.

<details><summary>Example from this build</summary>

```console
$ rclone ls r2:cloud-ai-lab/mnist/checkpoints/try-1/
  5074197 best.pt
  5074197 latest.pt
```
**Result:** ✅ (same size because the last save was also the best).
</details>

---

## Cost and safety

- **Spend limit:** set in step 1. With **$0**, nothing is ever billed beyond the free credit ($30/month in October 2026).
- **Timeouts:** every job has one (`timeout=` on `@app.function`): 5 min for hello-GPU, 2 min for R2, 30 min for training. A hung job is killed at the limit.
- **Retries:** every job sets `retries=0`, so a failed job runs once and bills once. To retry, run the command again; the training job resumes. Modal itself may still re-run a job its own infrastructure lost (for example a GPU taken away mid-run); that can't be turned off, and the training job then prints `resumed ... at step N`.
- **Agents never run `modal run`.** They write the code and the command; a human runs it ([CLAUDE.md](../CLAUDE.md), rule 4).
- **Check what ran:** `modal app list` shows recent runs; `modal app logs <app-id>` shows a finished run's output. Both are free.

| Job | Hardware | Typical time | Typical cost |
|---|---|---|---|
| `hello_gpu.py` | T4 | ~10 s (first run: + image build) | ~$0.002 |
| `r2_hello.py` | CPU | a few seconds | < $0.01 |
| `train_template.py` (3000 steps) | T4 | ~1 min with start-up | ~$0.01–0.02 |

Prices: modal.com/pricing, 2026-10-13. Check before relying on them.

## What's in the repo

| File | What it is |
|---|---|
| `jobs/hello_gpu.py` | Step 4: prove the GPU works |
| `jobs/r2_hello.py` | Step 7: prove a job can write to R2 |
| `jobs/train_template.py` | Step 8: the template to copy for real training |
| `lab/storage.py` | Upload / download / list in R2; builds keys as `<project>/<datasets\|checkpoints\|runs>/...` |
| `lab/checkpoints.py` | `RunCheckpoints`: `latest.pt` + `best.pt` per run, `restore()` to resume |
| `lab/notify.py` | Telegram messages for each job ([Stage 6](06-notifications.md)) |
| `tests/` | Offline tests with fake R2 and fake Telegram: `uv run pytest -q` |
