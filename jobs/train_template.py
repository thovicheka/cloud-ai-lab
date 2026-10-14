"""Checkpointed training template: a small CNN on MNIST that survives losing its GPU.

Every --ckpt-every steps it evaluates on the test set and saves to R2:
    r2:cloud-ai-lab/mnist/checkpoints/<run-name>/latest.pt   (always)
    r2:cloud-ai-lab/mnist/checkpoints/<run-name>/best.pt     (when test loss improves)
Started again with the same --run-name, it resumes from latest.pt: weights,
optimizer, step, best loss, RNG, and the exact position in the shuffled data.

Metrics go to Weights & Biases (project cloud-ai-lab, run name = --run-name): config,
train loss/accuracy every 50 steps, test loss/accuracy and 16 sample images with
predictions at each checkpoint, and the R2 checkpoint folder. The W&B run id is
saved in the checkpoint, so a resumed run continues the same W&B run. Without
WANDB_API_KEY in the `wandb` secret, training still runs, with W&B off.

Copy this file for a new project; replace load_data(), Net, and PROJECT.

Run (on the server, from the repo root; needs the Modal secrets `r2` and `wandb`):
    modal run jobs/train_template.py --run-name try-1
Test resuming: crash on purpose, then run the same command again:
    modal run jobs/train_template.py --run-name try-2 --crash-at-step 1100
    modal run jobs/train_template.py --run-name try-2      # resumes from step 1000

Cost (modal.com/pricing, 2026-10-13): T4 at $0.000164/s (~$0.59/h). The default
3000 steps take ~1-2 min of GPU time including startup: ~$0.01-0.02 per run.
"""

import modal

PROJECT = "mnist"
GPU = "T4"
TORCH_VERSION = "2.14.1"
TORCHVISION_VERSION = "0.29.1"
BOTO3_VERSION = "1.43.112"
NUMPY_VERSION = "2.5.3"  # torch warns "Failed to initialize NumPy" without it
WANDB_VERSION = "0.30.0"
LOG_EVERY = 50  # steps between train-loss points in W&B
N_SAMPLES = 16  # test images logged with their predictions at each checkpoint

app = modal.App("train-template")
image = (
    modal.Image.debian_slim(python_version="3.12")
    .uv_pip_install(
        f"torch=={TORCH_VERSION}",
        f"torchvision=={TORCHVISION_VERSION}",
        f"numpy=={NUMPY_VERSION}",
        f"boto3=={BOTO3_VERSION}",
        f"wandb=={WANDB_VERSION}",
    )
    .add_local_python_source("lab")
)


def load_data(device):
    """MNIST as two in-memory tensors on the GPU (60k train, 10k test); tiny and fast."""
    from torchvision import datasets

    def to_tensors(train):
        ds = datasets.MNIST("/tmp/data", train=train, download=True)
        x = ds.data.float().div(255).sub(0.1307).div(0.3081).unsqueeze(1)  # standard MNIST norm
        return x.to(device), ds.targets.to(device)

    return to_tensors(True), to_tensors(False)


def make_net():
    from torch import nn

    return nn.Sequential(
        nn.Conv2d(1, 32, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
        nn.Conv2d(32, 64, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
        nn.Flatten(), nn.Dropout(0.25), nn.Linear(64 * 7 * 7, 128), nn.ReLU(), nn.Linear(128, 10),
    )  # fmt: skip


# timeout: a hard stop so a hung job can't bill for long. Raise it for real training.
# retries=0 (Modal's default, made explicit): a failed run stops and bills once; run the
# same command again to resume. Modal may still re-run an input lost to its own
# infrastructure (e.g. a preempted GPU); that retry prints "resumed ... at step N".
@app.function(
    image=image,
    gpu=GPU,
    secrets=[modal.Secret.from_name("r2"), modal.Secret.from_name("wandb")],
    timeout=30 * 60,
    retries=0,
)
def train(
    run_name: str,
    steps: int = 3000,
    ckpt_every: int = 500,
    batch_size: int = 128,
    lr: float = 1e-3,
    seed: int = 0,
    crash_at_step: int = 0,
) -> dict:
    import os
    import time

    import torch
    import torch.nn.functional as F
    import wandb

    from lab import storage, tracking
    from lab.checkpoints import RunCheckpoints

    device = "cuda"
    torch.manual_seed(seed)
    (x_train, y_train), (x_test, y_test) = load_data(device)
    model = make_net().to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=lr)
    config = dict(steps=steps, ckpt_every=ckpt_every, batch_size=batch_size, lr=lr, seed=seed)

    ckpts = RunCheckpoints(PROJECT, run_name, mode="min")
    ckpt_dir = f"r2:{storage.bucket()}/{ckpts.latest_key.rsplit('/', 1)[0]}/"
    path = "/tmp/ckpt/latest.pt"
    os.makedirs(os.path.dirname(path), exist_ok=True)  # a fresh run has no /tmp/ckpt yet
    step, best, wandb_id = 0, None, None
    if ckpts.restore(path):
        # cpu: set_rng_state needs CPU tensors; load_state_dict moves the rest to the GPU
        state = torch.load(path, map_location="cpu", weights_only=False)
        model.load_state_dict(state["model"])
        opt.load_state_dict(state["opt"])
        torch.set_rng_state(state["rng"])
        torch.cuda.set_rng_state(state["cuda_rng"])
        step, best = state["step"], state["best"]
        wandb_id = state.get("wandb_id")  # absent in checkpoints from before W&B
        print(f"resumed {ckpts.latest_key} at step {step} (best test loss {best:.4f})")
        if state["config"] != config:
            print(f"warning: config changed since the checkpoint: {state['config']} -> {config}")
    else:
        print(f"no checkpoint at {ckpts.latest_key}; starting from step 0")

    # Same run_id as the lost run -> W&B appends to that run instead of starting a new one.
    wandb_config = {**config, "project": PROJECT, "gpu": GPU, "checkpoints": ckpt_dir}
    run = tracking.start_run(run_name, wandb_config, run_id=wandb_id)
    wandb_id = tracking.run_id(run, wandb_id)
    print(f"W&B: {tracking.run_url(run) or 'off'}")

    # Undo the normalisation once, for the sample images: uint8 pixels, 28x28.
    sample_pixels = (x_test[:N_SAMPLES] * 0.3081 + 0.1307).clamp(0, 1).mul(255).round()
    sample_pixels = sample_pixels.to(torch.uint8).squeeze(1).cpu().numpy()
    sample_labels = y_test[:N_SAMPLES].tolist()

    @torch.no_grad()
    def evaluate():
        model.eval()
        logits = torch.cat([model(x) for x in x_test.split(1000)])
        model.train()
        loss = F.cross_entropy(logits, y_test).item()
        acc = (logits.argmax(1) == y_test).float().mean().item()
        return loss, acc, logits[:N_SAMPLES].argmax(1).tolist()

    # Batch order depends only on (seed, epoch, step), so a resumed run sees exactly
    # the batches the lost run would have seen next.
    per_epoch = len(x_train) // batch_size
    start_step, started = step, time.time()
    # Train points are held back until the next checkpoint, so W&B only ever has steps up to
    # the last save. A resumed run then logs the redone steps once, not twice.
    pending = []
    model.train()
    try:
        while step < steps:
            epoch, i = divmod(step, per_epoch)
            gen = torch.Generator().manual_seed(seed + epoch)
            perm = torch.randperm(len(x_train), generator=gen)
            idx = perm[i * batch_size : (i + 1) * batch_size].to(device)

            logits = model(x_train[idx])
            loss = F.cross_entropy(logits, y_train[idx])
            opt.zero_grad(set_to_none=True)
            loss.backward()
            opt.step()
            step += 1

            if step % LOG_EVERY == 0:
                train_acc = (logits.argmax(1) == y_train[idx]).float().mean().item()
                pending.append((step, {"train/loss": loss.item(), "train/acc": train_acc}))

            if crash_at_step and step == crash_at_step:
                raise RuntimeError(f"simulated crash at step {step} (--crash-at-step)")

            if step % ckpt_every == 0 or step == steps:
                test_loss, test_acc, preds = evaluate()
                is_best = ckpts.improved(test_loss, best)
                if is_best:
                    best = test_loss

                for s, metrics in pending:
                    run.log(metrics, step=s)
                pending.clear()
                metrics = {"test/loss": test_loss, "test/acc": test_acc, "best_test_loss": best}
                if not run.disabled:
                    metrics["test/samples"] = [
                        wandb.Image(img, caption=f"pred {p} / true {t}")
                        for img, p, t in zip(sample_pixels, preds, sample_labels, strict=True)
                    ]
                run.log(metrics, step=step)

                torch.save(
                    {
                        "model": model.state_dict(),
                        "opt": opt.state_dict(),
                        "rng": torch.get_rng_state(),
                        "cuda_rng": torch.cuda.get_rng_state(),
                        "step": step,
                        "best": best,
                        "config": config,
                        "wandb_id": wandb_id,
                    },
                    path,
                )
                ckpts.save(path, is_best=is_best)
                print(
                    f"step {step:>5}/{steps}  train loss {loss.item():.4f}"
                    f"  test loss {test_loss:.4f}  test acc {test_acc:.4f}"
                    f"  saved latest{' + best' if is_best else ''}"
                )
    except BaseException:
        run.finish(exit_code=1)  # marks the W&B run failed; a resume reopens it
        raise

    run.summary["best_test_loss"] = best
    run.summary["checkpoints"] = ckpt_dir
    run.finish()

    # Plain Python types only: the result is unpickled on the server, which has no torch.
    return {
        "run": run_name,
        "steps_this_run": int(step - start_step),
        "resumed_from": int(start_step),
        "best_test_loss": round(float(best), 4) if best is not None else None,
        "train_seconds": round(time.time() - started, 1),
        "checkpoints": ckpt_dir,
        "wandb": tracking.run_url(run),
    }


@app.local_entrypoint()
def main(run_name: str, steps: int = 3000, ckpt_every: int = 500, crash_at_step: int = 0):
    from lab.notify import notify_job  # here, not at the top: containers don't need it

    with notify_job(f"train {PROJECT} {run_name}", gpu=GPU) as job:
        result = train.remote(
            run_name=run_name, steps=steps, ckpt_every=ckpt_every, crash_at_step=crash_at_step
        )
        job.note = (
            f"steps {result['resumed_from']}→{result['resumed_from'] + result['steps_this_run']}"
            f", best test loss {result['best_test_loss']}\n{result['checkpoints']}"
            + (f"\n{result['wandb']}" if result["wandb"] else "")
        )
    for key, value in result.items():
        print(f"{key:>15}: {value}")
