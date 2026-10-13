"""Checkpointed training template: a small CNN on MNIST that survives losing its GPU.

Every --ckpt-every steps it evaluates on the test set and saves to R2:
    r2:cloud-ai-lab/mnist/checkpoints/<run-name>/latest.pt   (always)
    r2:cloud-ai-lab/mnist/checkpoints/<run-name>/best.pt     (when test loss improves)
Started again with the same --run-name, it resumes from latest.pt: weights,
optimizer, step, best loss, RNG, and the exact position in the shuffled data.

Copy this file for a new project; replace load_data(), Net, and PROJECT.

Run (on the server, from the repo root; needs the Modal secret `r2`):
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

app = modal.App("train-template")
image = (
    modal.Image.debian_slim(python_version="3.12")
    .uv_pip_install(
        f"torch=={TORCH_VERSION}", f"torchvision=={TORCHVISION_VERSION}", f"boto3=={BOTO3_VERSION}"
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
@app.function(image=image, gpu=GPU, secrets=[modal.Secret.from_name("r2")], timeout=30 * 60)
def train(
    run_name: str,
    steps: int = 3000,
    ckpt_every: int = 500,
    batch_size: int = 128,
    lr: float = 1e-3,
    seed: int = 0,
    crash_at_step: int = 0,
) -> dict:
    import time

    import torch
    import torch.nn.functional as F

    from lab import storage
    from lab.checkpoints import RunCheckpoints

    device = "cuda"
    torch.manual_seed(seed)
    (x_train, y_train), (x_test, y_test) = load_data(device)
    model = make_net().to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=lr)
    config = dict(steps=steps, ckpt_every=ckpt_every, batch_size=batch_size, lr=lr, seed=seed)

    ckpts = RunCheckpoints(PROJECT, run_name, mode="min")
    path = "/tmp/ckpt/latest.pt"
    step, best = 0, None
    if ckpts.restore(path):
        # cpu: set_rng_state needs CPU tensors; load_state_dict moves the rest to the GPU
        state = torch.load(path, map_location="cpu", weights_only=False)
        model.load_state_dict(state["model"])
        opt.load_state_dict(state["opt"])
        torch.set_rng_state(state["rng"])
        torch.cuda.set_rng_state(state["cuda_rng"])
        step, best = state["step"], state["best"]
        print(f"resumed {ckpts.latest_key} at step {step} (best test loss {best:.4f})")
        if state["config"] != config:
            print(f"warning: config changed since the checkpoint: {state['config']} -> {config}")
    else:
        print(f"no checkpoint at {ckpts.latest_key}; starting from step 0")

    @torch.no_grad()
    def evaluate():
        model.eval()
        logits = torch.cat([model(x) for x in x_test.split(1000)])
        model.train()
        loss = F.cross_entropy(logits, y_test).item()
        acc = (logits.argmax(1) == y_test).float().mean().item()
        return loss, acc

    # Batch order depends only on (seed, epoch, step), so a resumed run sees exactly
    # the batches the lost run would have seen next.
    per_epoch = len(x_train) // batch_size
    start_step, started = step, time.time()
    model.train()
    while step < steps:
        epoch, i = divmod(step, per_epoch)
        perm = torch.randperm(len(x_train), generator=torch.Generator().manual_seed(seed + epoch))
        idx = perm[i * batch_size : (i + 1) * batch_size].to(device)

        loss = F.cross_entropy(model(x_train[idx]), y_train[idx])
        opt.zero_grad(set_to_none=True)
        loss.backward()
        opt.step()
        step += 1

        if crash_at_step and step == crash_at_step:
            raise RuntimeError(f"simulated crash at step {step} (--crash-at-step)")

        if step % ckpt_every == 0 or step == steps:
            test_loss, test_acc = evaluate()
            is_best = ckpts.improved(test_loss, best)
            if is_best:
                best = test_loss
            torch.save(
                {
                    "model": model.state_dict(),
                    "opt": opt.state_dict(),
                    "rng": torch.get_rng_state(),
                    "cuda_rng": torch.cuda.get_rng_state(),
                    "step": step,
                    "best": best,
                    "config": config,
                },
                path,
            )
            ckpts.save(path, is_best=is_best)
            print(
                f"step {step:>5}/{steps}  train loss {loss.item():.4f}  test loss {test_loss:.4f}"
                f"  test acc {test_acc:.4f}  saved latest{' + best' if is_best else ''}"
            )

    return {
        "run": run_name,
        "steps_this_run": step - start_step,
        "resumed_from": start_step,
        "best_test_loss": round(best, 4) if best is not None else None,
        "train_seconds": round(time.time() - started, 1),
        "checkpoints": f"r2:{storage.bucket()}/{ckpts.latest_key.rsplit('/', 1)[0]}/",
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
        )
    for key, value in result.items():
        print(f"{key:>15}: {value}")
