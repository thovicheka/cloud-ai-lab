# Stage 3 — Experiment tracking (Weights & Biases)

**What you'll have working by the end:** every training run shows up on wandb.ai with its config, loss and accuracy charts, sample predictions, and the R2 path of its checkpoints. A run that crashes and resumes stays **one** W&B run with continuous charts.

**Status:** ✅ Stage 3 complete (tasks 3.1–3.2; this doc is task 3.3).

**How to read this guide:** instructions use placeholders like `<wandb-api-key>`; replace them with your own values. After key steps, an **Example from this build** block shows the real commands and output from the author's setup:

| Placeholder | In this build |
|---|---|
| `<wandb-api-key>` | kept private (`WANDB_API_KEY=***`) |
| `<wandb-entity>` | `vicheese-cloud-ai-lab` (the W&B account/team the runs go to) |
| `<run-name>` | `wandb-1` |

**Which machine:** steps 1–2 happen on wandb.ai in a browser. Everything else runs **on the server**, from the repo root `~/projects/cloud-ai-lab`.

Why W&B: see [decisions.md](decisions.md#experiment-tracking-weights--biases-over-self-hosted-mlflow).

## Prerequisites
- [Stage 2](02-gpu-compute.md): Modal set up, the `r2` secret, and `jobs/train_template.py` working.
- Optional: [Stage 6](06-notifications.md), so the Finished message carries the W&B link.

---

## Steps

### 1. Create a W&B account *(browser)*
Sign up at wandb.ai. The free tier is enough for this lab.

*What it does:* gives you a place for runs. Projects are created automatically the first time a job logs to them; this lab uses one project, `cloud-ai-lab`.

### 2. Copy your API key *(browser)*
Open wandb.ai/authorize and copy the key.

*What it does:* the key lets programs log runs as you. Treat it like a password: it goes only into `.env` (step 3) and the Modal secret (step 4).

### 3. Add the key to `.env` *(on the server)*
```bash
nano .env
```
Fill in this line (it's already in `.env.example` with a fake value):
```bash
WANDB_API_KEY=<wandb-api-key>
```
*What it does:* keeps the key with the lab's other secrets, git-ignored and readable only by you. Training doesn't read it from here (step 4 does that). It's here so step 4 has one source to copy from.

### 4. Store the key as a Modal secret *(on the server)*
```bash
grep '^WANDB_API_KEY=' .env > ~/wandb.env && modal secret create wandb --from-dotenv ~/wandb.env; rm ~/wandb.env
```
*What it does:* uploads only the W&B line as the Modal secret `wandb` and deletes the temporary file. It's the same pattern as the `r2` secret in [Stage 2, step 6](02-gpu-compute.md): keys stay out of shell history, and other keys stay out of Modal. The training job gets the key as an environment variable through `secrets=[..., modal.Secret.from_name("wandb")]`.

> **Skipping W&B?** Still create a Modal secret `wandb` containing only `WANDB_MODE=disabled`, or training jobs won't start:
> ```bash
> modal secret create wandb WANDB_MODE=disabled
> ```
> The template asks Modal for the `wandb` secret by name. If the secret doesn't exist, Modal stops the job before training begins. With this placeholder secret, training runs normally and prints `warning: WANDB_API_KEY not set; W&B logging is off for this run`. (Not tested in this build, because the real secret existed. The template's no-key path is covered by `tests/test_tracking.py`.)

<details><summary>Example from this build</summary>

```console
$ uv run modal secret list
┃ Name  ┃ Created at           ┃ Created by   ┃ Last used at         ┃
│ wandb │ 2026-10-14 07:15 UTC │ <workspace>  │ -                    │
│ r2    │ 2026-10-14 04:45 UTC │ <workspace>  │ 2026-10-14 05:07 UTC │
```
**Result:** ✅ both secrets exist.
</details>

### 5. Run the template with a crash, then resume *(on the server; costs money)*
```bash
modal run jobs/train_template.py --run-name <run-name> --crash-at-step 1100   # dies after saving step 1000
modal run jobs/train_template.py --run-name <run-name>                        # resumes from step 1000
```
*What it does:* trains the MNIST template, logging to W&B as it goes. The first run crashes on purpose at step 1100 and the second picks up from the step-1000 checkpoint. It's the same test as [Stage 2](02-gpu-compute.md), now with W&B. Both runs print the same `W&B: https://wandb.ai/...` line, and the second says `Resuming run <run-name>`.

**Cost:** T4 at $0.000164/s (modal.com/pricing, 2026-10-13). About $0.01–0.02 per run. The first run after adding `wandb` also rebuilds the image (under 20 s in this build).

> **If you see** `Error: No such option '--run'. Did you mean '--run-name'?`, use the full flag `--run-name`. The command stopped before contacting Modal, so nothing was billed.
>
> **If you see** `warning: WANDB_API_KEY not set; W&B logging is off for this run`, the `wandb` secret has no `WANDB_API_KEY`. Redo step 4 with `--force` to overwrite it. Training still runs and checkpoints still go to R2; only W&B is off.

<details><summary>Example from this build</summary>

First run, crashing at step 1100 (image build and download progress trimmed):
```console
$ modal run jobs/train_template.py --run-name wandb-1 --crash-at-step 1100
✓ Initialized. View run at https://modal.com/apps/...
Building image im-...
=> Step 2: RUN /.uv/uv pip install ... boto3==1.43.112 numpy==2.5.3 torch==2.14.1 torchvision==0.29.1 wandb==0.30.0
...
Built image im-... in 16.91s
...
no checkpoint at mnist/checkpoints/wandb-1/latest.pt; starting from step 0
wandb: [wandb.login()] Loaded credentials for https://api.wandb.ai from WANDB_API_KEY.
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
**Result:** ✅ The crash is the point of the test, so the traceback is expected. W&B got 20 train points (steps 50–1000) and 2 × 16 sample images. Steps 1050 and 1100 were held back, because they came after the last checkpoint (see [Known limits](#known-limits)).

Before resuming, R2 holds exactly two checkpoints:
```console
$ rclone ls r2:cloud-ai-lab/mnist/checkpoints/wandb-1/
  5074261 best.pt
  5074261 latest.pt
```

Second run, resuming (progress trimmed):
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
✓ App completed. ...
```
**Result:** ✅ Same W&B run id (`hy7wqqht`) in both runs. The resume started at step 1000. Final test loss 0.0240, accuracy 99.29%, 26.8 s of training, about $0.01–0.02 (estimate).
</details>

### 6. Add W&B to your own job *(in the code)*
`jobs/train_template.py` already does all of this. For a new training job, the pieces are:
```python
WANDB_VERSION = "0.30.0"
image = (...).uv_pip_install(..., f"wandb=={WANDB_VERSION}").add_local_python_source("lab")

@app.function(image=image, secrets=[modal.Secret.from_name("r2"), modal.Secret.from_name("wandb")], ...)
def train(run_name: str, ...):
    from lab import tracking

    # after restoring the checkpoint (wandb_id is None for a new run)
    run = tracking.start_run(run_name, {**config, "checkpoints": ckpt_dir}, run_id=wandb_id)
    wandb_id = tracking.run_id(run, wandb_id)   # save this in every checkpoint
    try:
        ...
        run.log({"test/loss": test_loss, "test/acc": test_acc}, step=step)
        torch.save({..., "wandb_id": wandb_id}, path)
    except BaseException:
        run.finish(exit_code=1)   # marks the W&B run failed; a resume reopens it
        raise
    run.finish()
```
*What it does:* `start_run` starts a run in the `cloud-ai-lab` project named after `--run-name`. Given the id saved in the checkpoint, it continues that run (`resume="allow"`). Without a key it returns a disabled run that accepts every call and does nothing. `run_id()` returns the id to save; a disabled run's id is random, so it keeps the previous one.

**What the template logs:**

| What | Where on wandb.ai | When |
|---|---|---|
| Config: steps, ckpt_every, batch_size, lr, seed, project, gpu, **checkpoints** (R2 folder) | run config | at start |
| `train/loss`, `train/acc` | charts | every 50 steps (sent at the next checkpoint) |
| `test/loss`, `test/acc`, `best_test_loss` | charts | every checkpoint (500 steps) |
| `test/samples`: 16 test digits captioned `pred N / true M` | media panel | every checkpoint |
| `best_test_loss`, `checkpoints` | run summary | at the end |

The local entrypoint adds the W&B link to the Telegram ✅ Finished message ([Stage 6](06-notifications.md)).

> **Adapting:** for audio projects, log `wandb.Audio(array, sample_rate=...)` the same way as the images. Keep the `if not run.disabled:` guard the template uses around media, so no audio is built when W&B is off.

## Verify it worked
Open the `W&B:` link that the runs printed (or wandb.ai → project `cloud-ai-lab`). Expected:
- **one** run named `<run-name>`, not two;
- `train/loss` and `test/loss` charts covering the whole run, with no gap or doubled points around the resume;
- `test/samples` images with `pred N / true M` captions;
- the config's `checkpoints` value pointing at `r2:cloud-ai-lab/mnist/checkpoints/<run-name>/`.

<details><summary>Example from this build</summary>

Checked by the human on wandb.ai and in Telegram after step 5 (2026-10-14):
- wandb.ai: run `wandb-1` has continuous charts 0–3000. `test/samples` shows digit images with predicted/true captions. The config shows the checkpoint path.
- Telegram: ▶️ Started, ❌ Failed, ▶️ Started, ✅ Finished, and the Finished message has the W&B link.

**Result:** ✅ 3.2's "done when" (a run shows charts on wandb.ai) is met.
</details>

---

## Known limits
- **Train charts update every 500 steps, not every 50.** Train points are held until the next checkpoint and logged just before it's saved. W&B then never has steps past the last checkpoint, so a resumed run logs the redone steps once, not twice. The cost: on wandb.ai, the live view lags by up to one checkpoint interval, and points after the last checkpoint of a crashed run are never logged.
- **Untested: skipping W&B with the `WANDB_MODE=disabled` secret on Modal.** The no-key path itself is tested offline.
- **The tests use W&B offline mode.** They check run names, config, and that a resumed run keeps its id, without contacting wandb.ai. Resuming against the real server was first checked in step 5.
- **The W&B client is pinned** (`wandb==0.30.0` in the job image and as a dev dependency). Update both together.

## What's in the repo

| File | What it is |
|---|---|
| `lab/tracking.py` | `start_run()` (start or resume, off without a key), `run_id()`, `run_url()` |
| `jobs/train_template.py` | the template, logging to W&B (config, metrics, samples, checkpoint path) |
| `tests/test_tracking.py` | 4 offline tests: no key, new run, resume keeps the id, id survives the checkpoint round trip. `uv run pytest -q` runs all 37 |
| `.env.example` | `WANDB_API_KEY` with a fake value |

> **If you see** `wandb.errors.errors.CommError: user is not logged in` when running the tests, something is keeping wandb's per-process setup between tests. `tests/test_tracking.py` resets it after each test with `wandb.teardown()`. Keep that fixture if you add tests.
