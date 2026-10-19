"""Training template as a Prefect flow: ask for approval, then run jobs/train_template.py's
`train` on a Modal T4. Same R2 checkpoints and W&B run as `modal run jobs/train_template.py`.

States: Scheduled → Running → Paused (⏸️ on Telegram, with cost and link) → you Resume in the UI:
  - approve switch on: Running → ▶️ Started → ✅ Finished (Completed) or ❌ Failed (Failed)
  - approve switch off: 🚫 Declined (Cancelled); nothing runs on Modal
  - no answer in 24 h: ⌛ (Failed); nothing runs on Modal
A failed run is never retried automatically. Run it again with the same run_name to resume
from its last R2 checkpoint (it asks for approval again).

Register (on the server, from ~/projects/lab-runtime after the merge, with prefect-server running):
    uv run python -m flows.train
Run: UI → Deployments → train-mnist/train-mnist → Run (set run_name), or
    uv run prefect deployment run train-mnist/train-mnist --param run_name=flow-1

Cost: measured 2026-10-14, 2000 steps trained in 23-27 s on a T4. The estimate allows 90 s
for container start, data download and W&B, plus 15 ms per step: 3000 steps ≈ 135 s ≈ $0.02.
The function's 30 min timeout caps one run at ~$0.30.
"""

from pathlib import Path

import modal
from prefect import flow, task
from prefect.cache_policies import NO_CACHE
from prefect.states import Cancelled

from flows.approval import ask_approval
from jobs.train_template import GPU, PROJECT, app, train
from lab.notify import notify_job

REPO = Path(__file__).resolve().parents[1]
STARTUP_SECONDS = 90  # container start, MNIST download, W&B init
SECONDS_PER_STEP = 0.015  # 2000 steps in 23-27 s on a T4, rounded up
MAX_SECONDS = 30 * 60  # timeout= in jobs/train_template.py: Modal stops the function there


def expected_seconds(steps: int) -> float:
    return STARTUP_SECONDS + steps * SECONDS_PER_STEP


# Paid: never retried by Prefect (Modal's retries=0 too). The job resumes from its checkpoint,
# so a human re-runs it after a failure, with a new approval.
@task(retries=0, cache_policy=NO_CACHE)
def run_on_modal(run_name: str, steps: int, ckpt_every: int) -> dict:
    with notify_job(f"train {PROJECT} {run_name}", gpu=GPU) as job:
        with modal.enable_output(), app.run():  # same as `modal run`, from Python
            result = train.remote(run_name=run_name, steps=steps, ckpt_every=ckpt_every)
        job.note = (
            f"steps {result['resumed_from']}→{result['resumed_from'] + result['steps_this_run']}"
            f", best test loss {result['best_test_loss']}\n{result['checkpoints']}"
            + (f"\n{result['wandb']}" if result["wandb"] else "")
        )
    return result


@flow(name="train-mnist", retries=0, log_prints=True)
def train_mnist(run_name: str, steps: int = 3000, ckpt_every: int = 500):
    job = f"train {PROJECT} {run_name} ({steps} steps)"
    if not ask_approval(
        job, gpu=GPU, expected_seconds=expected_seconds(steps), max_seconds=MAX_SECONDS
    ):
        return Cancelled(message="Declined in the UI; nothing ran on Modal")
    result = run_on_modal(run_name, steps, ckpt_every)
    for key, value in result.items():
        print(f"{key:>15}: {value}")
    return result


if __name__ == "__main__":
    # Code is read from this checkout when each run starts; nothing is uploaded anywhere.
    train_mnist.from_source(source=str(REPO), entrypoint="flows/train.py:train_mnist").deploy(
        name="train-mnist", work_pool_name="lab"
    )
