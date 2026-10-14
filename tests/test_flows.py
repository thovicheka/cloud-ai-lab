"""flows/ against a throwaway Prefect server, with Modal and Telegram replaced by fakes.

The approval gate is the real one: each flow really pauses, and the test resumes it
through the Prefect API the way the UI's Resume button does. Nothing reaches Modal,
Telegram, or the lab's own Prefect server on :4200.
"""

import contextlib
import contextvars
import threading
import time
import urllib.error

import modal
import pytest
from prefect.client.orchestration import get_client
from prefect.client.schemas.filters import FlowRunFilter, FlowRunFilterId
from prefect.flow_runs import resume_flow_run
from prefect.settings import PREFECT_API_URL
from prefect.testing.utilities import prefect_test_harness

from flows import approval
from flows import hello_gpu as hello_flow
from flows import train as train_flow
from lab import notify


@pytest.fixture(scope="session", autouse=True)
def prefect_server():
    with prefect_test_harness():
        assert ":4200" not in PREFECT_API_URL.value()  # never the lab's real server
        yield


@pytest.fixture(autouse=True)
def fast_gate(monkeypatch):
    monkeypatch.setattr(approval, "POLL_INTERVAL", 1)
    monkeypatch.setattr(approval.send, "retry_delay_seconds", [0, 0])


@pytest.fixture(autouse=True)
def no_real_modal(monkeypatch):
    """Any real Modal app start fails the test, even if a fake below is missed."""

    def refuse(*args, **kwargs):
        raise AssertionError("a test tried to start a real Modal app")

    monkeypatch.setattr(modal.App, "run", refuse)
    monkeypatch.setattr(modal, "enable_output", contextlib.nullcontext)


class FakeFunction:
    def __init__(self, result=None, error=None):
        self.calls, self.result, self.error = [], result, error

    def remote(self, **kwargs):
        self.calls.append(kwargs)
        if self.error:
            raise self.error
        return self.result


class FakeApp:
    def run(self):
        return contextlib.nullcontext()


HELLO_RESULT = {
    "gpu": "Tesla T4",
    "torch": "2.14.1",
    "cuda": "12.8",
    "matmul": "4096x4096",
    "ms": 35.8,
    "tflops": 3.84,
}
TRAIN_RESULT = {
    "run": "flow-1",
    "steps_this_run": 3000,
    "resumed_from": 0,
    "best_test_loss": 0.0217,
    "train_seconds": 35.0,
    "checkpoints": "r2:cloud-ai-lab/mnist/checkpoints/flow-1/",
    "wandb": None,
}


@pytest.fixture
def fake_hello(monkeypatch):
    fn = FakeFunction(HELLO_RESULT)
    monkeypatch.setattr(hello_flow, "app", FakeApp())
    monkeypatch.setattr(hello_flow, "hello", fn)
    return fn


@pytest.fixture
def fake_train(monkeypatch):
    fn = FakeFunction(TRAIN_RESULT)
    monkeypatch.setattr(train_flow, "app", FakeApp())
    monkeypatch.setattr(train_flow, "train", fn)
    return fn


def texts(sent):
    return [m["text"] for m in sent]


class Started:
    """A flow started in a thread, as the worker would; it blocks while Paused."""

    def __init__(self, flow, **params):
        self.state = None
        ctx = contextvars.copy_context()
        self.thread = threading.Thread(target=ctx.run, args=(self._run, flow, params), daemon=True)
        self.thread.start()

    def _run(self, flow, params):
        self.state = flow(**params, return_state=True)

    def wait_paused(self, timeout=30):
        deadline = time.monotonic() + timeout
        with get_client(sync_client=True) as client:
            while time.monotonic() < deadline:
                for run in client.read_flow_runs():  # earlier tests' runs have all finished
                    if run.state and run.state.is_paused():
                        self.flow_run_id = run.id
                        return run
                time.sleep(0.2)
        raise AssertionError("flow never paused")

    def resume(self, **answer):
        resume_flow_run(self.flow_run_id, run_input=answer)
        return self.finish()

    def finish(self, timeout=30):
        self.thread.join(timeout)
        assert not self.thread.is_alive(), "flow still running"
        return self.state


def final_state_name(flow_run_id):
    with get_client(sync_client=True) as client:
        (run,) = client.read_flow_runs(
            flow_run_filter=FlowRunFilter(id=FlowRunFilterId(any_=[flow_run_id]))
        )
        return run.state.name


# --- cost estimates and the approval message -------------------------------------------------


def test_hello_gpu_estimate():
    msg = approval.approval_message("hello-gpu", "T4", 60, 300, "http://lab:4200/runs/flow-run/x")
    assert msg.startswith("⏸️ Awaiting approval, ~$0.01: hello-gpu on T4\n")
    assert "At most $0.05 if it hits its 5 min timeout." in msg
    assert "http://lab:4200/runs/flow-run/x" in msg
    assert "No answer in 24 h = not run." in msg


def test_train_estimate():
    assert train_flow.expected_seconds(3000) == 135
    msg = approval.approval_message("train", "T4", train_flow.expected_seconds(3000), 1800, "link")
    assert msg.startswith("⏸️ Awaiting approval, ~$0.02: train on T4\n")
    assert "At most $0.30 if it hits its 30 min timeout." in msg


# --- retries: only free steps --------------------------------------------------------------


def test_paid_steps_never_retry():
    for paid in (hello_flow.run_on_modal, train_flow.run_on_modal):
        assert paid.retries == 0
    for flow in (hello_flow.hello_gpu, train_flow.train_mnist):
        assert flow.retries == 0
    assert approval.send.retries == 2  # Telegram is free to retry


def test_approval_waits_24_hours():
    assert approval.APPROVAL_TIMEOUT == 24 * 3600


# --- the gate, end to end ---------------------------------------------------------------


def test_nothing_runs_before_approval_then_approved_run(telegram, fake_hello):
    run = Started(hello_flow.hello_gpu)
    paused = run.wait_paused()

    assert fake_hello.calls == []  # paused, and Modal not called
    (ask,) = texts(telegram)
    assert ask.startswith("⏸️ Awaiting approval, ~$0.01: hello-gpu on T4")
    assert str(paused.id) in ask  # link to this flow run in the UI

    state = run.resume(approve=True, note="go")
    assert state.is_completed()
    assert fake_hello.calls == [{}]
    _, started, finished = texts(telegram)
    assert started == "▶️ Started: hello-gpu (T4)"
    assert finished.startswith("✅ Finished: hello-gpu in ")
    assert finished.endswith("Tesla T4: 3.84 TFLOPS")


def test_declined_never_calls_modal(telegram, fake_hello):
    run = Started(hello_flow.hello_gpu)
    run.wait_paused()
    state = run.resume(approve=False, note="not today")

    assert state.is_cancelled()
    assert fake_hello.calls == []
    assert (
        texts(telegram)[-1] == "🚫 Declined: hello-gpu (not today). Nothing ran on Modal; $0 spent."
    )


def test_resume_without_ticking_approve_declines(telegram, fake_hello):
    run = Started(hello_flow.hello_gpu)
    run.wait_paused()
    state = run.resume()  # Resume pressed, form left as is

    assert state.is_cancelled()
    assert fake_hello.calls == []


def test_no_answer_times_out_without_modal(telegram, fake_hello, monkeypatch):
    monkeypatch.setattr(approval, "APPROVAL_TIMEOUT", 2)
    run = Started(hello_flow.hello_gpu)
    run.wait_paused()
    state = run.finish()

    assert state.is_failed()
    assert fake_hello.calls == []
    assert texts(telegram)[-1].startswith("⌛ Not approved within")
    assert "Nothing ran on Modal; $0 spent." in texts(telegram)[-1]


def test_failed_gpu_step_is_not_retried(telegram, fake_hello):
    fake_hello.error = RuntimeError("CUDA out of memory")
    run = Started(hello_flow.hello_gpu)
    run.wait_paused()
    state = run.resume(approve=True)

    assert state.is_failed()
    assert final_state_name(run.flow_run_id) == "Failed"
    assert len(fake_hello.calls) == 1  # one paid attempt only
    assert texts(telegram)[-1].startswith("❌ Failed: hello-gpu after ")
    assert "RuntimeError: CUDA out of memory" in texts(telegram)[-1]


def test_telegram_down_still_pauses_and_retries_messages(monkeypatch, fake_hello):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "123456:FAKE")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "42")
    attempts = []

    def down(request, timeout):
        attempts.append(request)
        raise urllib.error.URLError("no network")

    monkeypatch.setattr(notify.urllib.request, "urlopen", down)
    run = Started(hello_flow.hello_gpu)
    run.wait_paused()  # the gate holds even when the message can't be sent
    assert len(attempts) == 3  # first try + 2 retries
    state = run.resume(approve=False)
    assert state.is_cancelled()
    assert fake_hello.calls == []


def test_train_passes_parameters_after_approval(telegram, fake_train):
    run = Started(train_flow.train_mnist, run_name="flow-1", steps=3000, ckpt_every=500)
    run.wait_paused()
    assert fake_train.calls == []
    assert texts(telegram)[0].startswith(
        "⏸️ Awaiting approval, ~$0.02: train mnist flow-1 (3000 steps) on T4"
    )

    state = run.resume(approve=True)
    assert state.is_completed()
    assert fake_train.calls == [{"run_name": "flow-1", "steps": 3000, "ckpt_every": 500}]
    assert texts(telegram)[1] == "▶️ Started: train mnist flow-1 (T4)"
    assert "steps 0→3000, best test loss 0.0217" in texts(telegram)[2]
