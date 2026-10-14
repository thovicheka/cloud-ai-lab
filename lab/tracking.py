"""Weights & Biases for training jobs: one W&B run per training run, resumable, optional.

The key comes from WANDB_API_KEY: from `.env` on the server, or from the Modal
secret `wandb` inside a job (`secrets=[modal.Secret.from_name("wandb")]`).
Without it, training still runs; W&B calls do nothing and a warning is printed.

Resuming: keep `run_id(run)` in the checkpoint and pass it back to `start_run`,
so a restarted job continues the same W&B run instead of starting a new one:

    run = start_run(run_name, config, run_id=state.get("wandb_id"))
    ...
    torch.save({..., "wandb_id": run_id(run, state.get("wandb_id"))}, path)
"""

import os

PROJECT = "cloud-ai-lab"


def start_run(name: str, config: dict, *, run_id: str | None = None, dir: str = "/tmp/wandb"):
    """Start (or resume, if `run_id` exists in W&B) the run `name` in the cloud-ai-lab project."""
    import wandb

    if not os.environ.get("WANDB_API_KEY"):
        print("warning: WANDB_API_KEY not set; W&B logging is off for this run")
        return wandb.init(mode="disabled", name=name, config=config)

    os.makedirs(dir, exist_ok=True)
    # resume="allow": continue run_id if W&B has it, else start a new run with that id
    return wandb.init(
        project=PROJECT, name=name, id=run_id, resume="allow", config=config, dir=dir
    )


def run_id(run, previous: str | None = None) -> str | None:
    """The id to store in a checkpoint. A disabled run's id is random, so keep `previous`."""
    return previous if run.disabled else run.id


def run_url(run) -> str | None:
    """The run's page on wandb.ai, or None when W&B is off or offline."""
    return None if run.disabled else run.url
