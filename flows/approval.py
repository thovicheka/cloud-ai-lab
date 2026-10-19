"""Approval gate for paid flows: estimate the cost, ask on Telegram, pause until a human answers.

Every flow that calls a paid Modal function does this first:

    if not ask_approval("hello-gpu", gpu="T4", expected_seconds=60, max_seconds=300):
        return Cancelled(message="Declined in the UI; nothing ran on Modal")
    run_on_modal(...)   # a task with retries=0

ask_approval() sends "⏸️ Awaiting approval, ~$X" with a link to the flow run, then pauses the
run (state Paused). In the UI: open the link → Resume → turn the `approve` switch on → Submit.
Left off means declined. No answer in 24 h → the run fails (FlowPauseTimeout); nothing ran on Modal.

The gate is enforced by the flow, not by Modal: anything with access to the Prefect API can
resume a run. Agents are denied the resume commands in .claude/settings.json; Modal's $0
spending limit stays the hard backstop (docs/04-job-queue-design.md §5).
"""

from prefect import get_run_logger, task
from prefect.exceptions import FlowPauseTimeout
from prefect.flow_runs import pause_flow_run
from prefect.input import RunInput
from prefect.runtime import flow_run

from lab.notify import estimate_cost, notify

APPROVAL_TIMEOUT = 24 * 3600  # seconds; then the run fails without touching a GPU
POLL_INTERVAL = 10  # seconds between checks for a Resume while paused


class Approval(RunInput):
    approve: bool = False  # a switch, off by default: a Resume without turning it on declines
    note: str = ""


@task(retries=2, retry_delay_seconds=10)
def send(text: str) -> None:
    """Send a Telegram message. Free, so it's retried; raises if it still isn't sent."""
    if not notify(text):
        raise RuntimeError("Telegram message not sent (see the notify: line above)")


def tell(text: str) -> None:
    """send() that never fails the flow: Telegram being down mustn't stop or start a job."""
    try:
        send(text)
    except Exception as e:  # noqa: BLE001 -- already retried; the UI still shows the run state
        get_run_logger().warning(f"notification not sent: {e}")


def approval_message(
    job: str, gpu: str, expected_seconds: float, max_seconds: float, link: str
) -> str:
    expected = estimate_cost(expected_seconds, gpu)
    worst = estimate_cost(max_seconds, gpu)
    return (
        f"⏸️ Awaiting approval, ~${expected:.2f}: {job} on {gpu}\n"
        f"At most ${worst:.2f} if it hits its {max_seconds / 60:g} min timeout.\n"
        f"{link}\n"
        f"Resume → turn the approve switch ON → Submit. No answer in {APPROVAL_TIMEOUT / 3600:g} h = not run."
    )


def ask_approval(job: str, *, gpu: str, expected_seconds: float, max_seconds: float) -> bool:
    """Ask on Telegram and pause until a human answers in the UI. True only if approved.

    Raises FlowPauseTimeout (the run fails) after APPROVAL_TIMEOUT with no answer.
    """
    logger = get_run_logger()
    link = flow_run.ui_url or f"flow run {flow_run.id}"
    hours = APPROVAL_TIMEOUT / 3600
    message = approval_message(job, gpu, expected_seconds, max_seconds, link)
    tell(message)
    logger.info(message.replace("\n", " | "))
    try:
        answer = pause_flow_run(
            wait_for_input=Approval, timeout=APPROVAL_TIMEOUT, poll_interval=POLL_INTERVAL
        )
    except FlowPauseTimeout:
        tell(f"⌛ Not approved within {hours:g} h: {job}. Nothing ran on Modal; $0 spent.")
        logger.error(f"No approval within {hours:g} h; not run")
        raise
    note = f" ({answer.note})" if answer.note else ""
    if not answer.approve:
        tell(f"🚫 Declined: {job}{note}. Nothing ran on Modal; $0 spent.")
        logger.info(f"Declined{note}")
        return False
    logger.info(f"Approved{note}")
    return True
