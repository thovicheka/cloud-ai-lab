"""Smoke test for the Prefect setup: a free flow that runs on `lab` only (no Modal, no GPU).

Register it once (on the server, from the repo root, with prefect-server running):
    uv run python flows/hello.py
Then run it from the UI (Deployments → hello/hello → Run) or:
    uv run prefect deployment run hello/hello
The worker (prefect-worker.service) picks it up; the run shows "Hello from lab" in its logs.
"""

import platform
from pathlib import Path

from prefect import flow, get_run_logger

REPO = Path(__file__).resolve().parents[1]


@flow(name="hello", log_prints=True)
def hello(name: str = "lab") -> str:
    logger = get_run_logger()
    message = f"Hello from {name} ({platform.node()}, Python {platform.python_version()})"
    logger.info(message)
    return message


if __name__ == "__main__":
    # Code is read from this checkout when each run starts; nothing is uploaded anywhere.
    hello.from_source(source=str(REPO), entrypoint="flows/hello.py:hello").deploy(
        name="hello", work_pool_name="lab"
    )
