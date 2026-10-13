"""Telegram notifications for jobs: started / finished / failed, with duration and cost.

Reads TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID from the environment or the repo's
`.env`. Call it from a job's local entrypoint (it runs on the server, where `.env`
lives), so Modal containers never need the Telegram secret:

    with notify_job("train mnist try-1", gpu="T4") as job:
        result = train.remote(...)
        job.note = f"best test loss {result['best_test_loss']}"

A notification never breaks a job: if Telegram isn't configured or is down,
it prints a warning and the job carries on.

Send a test message, or test all three job messages without any GPU:
    uv run python -m lab.notify "hello from the lab"
    uv run python -m lab.notify --test
"""

import json
import os
import sys
import time
import urllib.error
import urllib.request
from contextlib import contextmanager
from pathlib import Path

# Modal per-second GPU prices (modal.com/pricing, 2026-10-13). Check before relying on them.
GPU_PRICE_PER_SECOND = {
    "T4": 0.000164,
    "L4": 0.000222,
    "A10": 0.000306,
    "L40S": 0.000542,
    "A100-40GB": 0.000583,
    "A100-80GB": 0.000694,
    "RTX-PRO-6000": 0.000842,
    "H100": 0.001097,
    "H200": 0.001261,
    "B200": 0.001736,
    "B300": 0.001972,
}
MAX_LENGTH = 4096  # Telegram's limit per message

ENV_FILE = Path(__file__).resolve().parents[1] / ".env"


def load_env(path: Path = ENV_FILE) -> None:
    """Read KEY=VALUE lines from `.env` into os.environ, never overriding what's set.

    Standard library only, so this works under any Python that runs `modal`,
    including `uv tool install modal`, which has no project packages.
    """
    if not path.is_file():
        return
    for line in path.read_text().splitlines():
        line = line.strip().removeprefix("export ")
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = (part.strip() for part in line.split("=", 1))
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
            value = value[1:-1]
        os.environ.setdefault(key, value)


load_env()


def notify(text: str) -> bool:
    """Send `text` to the lab's Telegram chat. Returns False (never raises) on failure."""
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        print("notify: TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID not set; not sent:", text)
        return False

    body = json.dumps({"chat_id": chat_id, "text": text[:MAX_LENGTH]}).encode()
    request = urllib.request.Request(
        f"https://api.telegram.org/bot{token}/sendMessage",
        data=body,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=10):
            return True
    except urllib.error.HTTPError as e:
        # Only the status and Telegram's description: the request URL contains the token.
        try:
            detail = json.loads(e.read()).get("description", "")
        except (ValueError, AttributeError, OSError):
            detail = ""
        print(f"notify: Telegram returned HTTP {e.code} {detail}; not sent")
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        print(f"notify: couldn't reach Telegram ({type(e).__name__}); not sent")
    return False


def estimate_cost(seconds: float, gpu: str | None) -> float | None:
    """GPU cost of `seconds` on `gpu` (CPU and memory, a few % extra, are left out)."""
    if gpu is None:
        return None
    return seconds * GPU_PRICE_PER_SECOND[gpu.split(":")[0].rstrip("!+")] * _gpu_count(gpu)


def _gpu_count(gpu: str) -> int:
    return int(gpu.split(":")[1]) if ":" in gpu else 1


def _duration(seconds: float) -> str:
    minutes, secs = divmod(round(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours}h {minutes:02d}m" if hours else f"{minutes}m {secs:02d}s"


def _summary(seconds: float, gpu: str | None) -> str:
    cost = estimate_cost(seconds, gpu)
    price = f"~${cost:.2f} on {gpu}" if cost is not None else "CPU only, < $0.01"
    return f"{_duration(seconds)}, {price}"


class _Job:
    note = ""  # set inside the `with` block; added to the finish message


@contextmanager
def notify_job(name: str, *, gpu: str | None = None):
    """Notify when the block starts, finishes, fails, or is stopped (Ctrl-C).

    Duration is wall-clock time on the server, including container start-up, so
    the cost is a slight overestimate of what Modal bills.
    """
    job = _Job()
    notify(f"▶️ Started: {name}" + (f" ({gpu})" if gpu else ""))
    start = time.monotonic()
    try:
        yield job
    except KeyboardInterrupt:
        notify(f"⏹️ Stopped: {name} after {_summary(time.monotonic() - start, gpu)}")
        raise
    except BaseException as e:
        error = f"{type(e).__name__}: {e}"[:500]
        notify(f"❌ Failed: {name} after {_summary(time.monotonic() - start, gpu)}\n{error}")
        raise
    notify(
        f"✅ Finished: {name} in {_summary(time.monotonic() - start, gpu)}"
        + (f"\n{job.note}" if job.note else "")
    )


def _test() -> None:
    """Send the three job messages with no GPU and no Modal: a job that finishes, one that fails."""
    with notify_job("notify test: a job that finishes", gpu="T4") as job:
        time.sleep(1)
        job.note = "this is the note line"
    try:
        with notify_job("notify test: a job that fails", gpu="T4"):
            time.sleep(1)
            raise RuntimeError("simulated failure (this is expected)")
    except RuntimeError:
        pass


if __name__ == "__main__":
    if sys.argv[1:] == ["--test"]:
        _test()
    elif len(sys.argv) == 2:
        sys.exit(0 if notify(sys.argv[1]) else 1)
    else:
        sys.exit(__doc__)
