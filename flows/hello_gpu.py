"""hello-gpu as a Prefect flow: ask for approval, then run jobs/hello_gpu.py's function on a Modal T4.

States: Scheduled → Running → Paused (⏸️ on Telegram, with cost and link) → you Resume in the UI:
  - approve ticked: Running → ▶️ Started → ✅ Finished (Completed) or ❌ Failed (Failed)
  - approve unticked: 🚫 Declined (Cancelled); nothing runs on Modal
  - no answer in 24 h: ⌛ (Failed); nothing runs on Modal

Register (on the server, from ~/projects/lab-runtime after the merge, with prefect-server running):
    uv run python -m flows.hello_gpu
Run: UI → Deployments → hello-gpu/hello-gpu → Run, or
    uv run prefect deployment run hello-gpu/hello-gpu

Cost: the real run on 2026-10-14 took 9 s; the estimate allows 60 s for a cold start
(~$0.01 on T4). The function's 5 min timeout caps it at ~$0.05.
"""

from pathlib import Path

import modal
from prefect import flow, task
from prefect.cache_policies import NO_CACHE
from prefect.states import Cancelled

from flows.approval import ask_approval
from jobs.hello_gpu import GPU, app, hello
from lab.notify import notify_job

REPO = Path(__file__).resolve().parents[1]
EXPECTED_SECONDS = 60  # 9 s measured warm; container start and image pull on a cold run
MAX_SECONDS = 300  # timeout= in jobs/hello_gpu.py: Modal stops the function there


# Paid: never retried by Prefect (Modal's retries=0 too). A human decides whether to pay again.
@task(retries=0, cache_policy=NO_CACHE)
def run_on_modal() -> dict:
    with notify_job("hello-gpu", gpu=GPU) as job:
        with modal.enable_output(), app.run():  # same as `modal run`, from Python
            result = hello.remote()
        job.note = f"{result['gpu']}: {result['tflops']} TFLOPS"
    return result


@flow(name="hello-gpu", retries=0, log_prints=True)
def hello_gpu():
    if not ask_approval(
        "hello-gpu", gpu=GPU, expected_seconds=EXPECTED_SECONDS, max_seconds=MAX_SECONDS
    ):
        return Cancelled(message="Declined in the UI; nothing ran on Modal")
    result = run_on_modal()
    for key, value in result.items():
        print(f"{key:>9}: {value}")
    return result


if __name__ == "__main__":
    # Code is read from this checkout when each run starts; nothing is uploaded anywhere.
    hello_gpu.from_source(source=str(REPO), entrypoint="flows/hello_gpu.py:hello_gpu").deploy(
        name="hello-gpu", work_pool_name="lab"
    )
