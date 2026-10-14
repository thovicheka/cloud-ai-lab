"""lab/notify.py with Telegram's API replaced by a fake: nothing is sent."""

import io
import urllib.error

import pytest

from lab import notify as n

TOKEN = "123456:FAKE-TOKEN-must-never-be-printed"  # same as tests/conftest.py


def texts(sent):
    return [m["text"] for m in sent]


def test_notify_sends_to_chat(telegram):
    assert n.notify("hello") is True
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    assert telegram == [{"url": url, "chat_id": "42", "text": "hello"}]


def test_notify_truncates_long_text(telegram):
    n.notify("x" * 5000)
    assert len(telegram[0]["text"]) == 4096


def test_notify_without_config_does_not_raise(monkeypatch, capsys):
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
    monkeypatch.delenv("TELEGRAM_CHAT_ID", raising=False)
    assert n.notify("hello") is False
    assert "not set" in capsys.readouterr().out


@pytest.mark.parametrize(
    "error",
    [
        urllib.error.HTTPError(
            "https://api.telegram.org/bot" + TOKEN, 401, "Unauthorized", {},
            io.BytesIO(b'{"ok":false,"description":"Unauthorized"}'),
        ),
        urllib.error.HTTPError("u", 502, "Bad Gateway", {}, io.BytesIO(b"<html>not json</html>")),
        urllib.error.URLError("Name or service not known"),
        TimeoutError("timed out"),
    ],
)  # fmt: skip
def test_notify_errors_do_not_raise_or_leak_token(telegram, monkeypatch, capsys, error):
    def failing_urlopen(request, timeout):
        raise error

    monkeypatch.setattr(n.urllib.request, "urlopen", failing_urlopen)
    assert n.notify("hello") is False
    out = capsys.readouterr().out
    assert "not sent" in out
    assert TOKEN not in out and "FAKE-TOKEN" not in out


def test_estimate_cost():
    assert n.estimate_cost(3600, "T4") == pytest.approx(0.5904)
    assert n.estimate_cost(100, "H100:8") == pytest.approx(100 * 0.001097 * 8)
    assert n.estimate_cost(100, "H100!") == pytest.approx(100 * 0.001097)
    assert n.estimate_cost(100, None) is None


def test_duration_format():
    assert n._duration(65) == "1m 05s"
    assert n._duration(3 * 3600 + 7 * 60 + 30) == "3h 07m"


def test_job_that_finishes(telegram, monkeypatch):
    clock = iter([0.0, 125.0])
    monkeypatch.setattr(n.time, "monotonic", lambda: next(clock))

    with n.notify_job("train try-1", gpu="T4") as job:
        job.note = "best test loss 0.03"

    assert texts(telegram) == [
        "▶️ Started: train try-1 (T4)",
        "✅ Finished: train try-1 in 2m 05s, ~$0.02 on T4\nbest test loss 0.03",
    ]


def test_job_that_fails_reraises(telegram, monkeypatch):
    clock = iter([0.0, 30.0])
    monkeypatch.setattr(n.time, "monotonic", lambda: next(clock))

    with pytest.raises(RuntimeError, match="boom"):
        with n.notify_job("train try-1", gpu="T4"):
            raise RuntimeError("boom")

    assert texts(telegram) == [
        "▶️ Started: train try-1 (T4)",
        "❌ Failed: train try-1 after 0m 30s, ~$0.00 on T4\nRuntimeError: boom",
    ]


def test_job_stopped_with_ctrl_c(telegram):
    with pytest.raises(KeyboardInterrupt):
        with n.notify_job("cpu job"):
            raise KeyboardInterrupt

    assert texts(telegram)[1].startswith("⏹️ Stopped: cpu job after 0m 00s, CPU only")


def test_job_runs_even_when_telegram_is_down(monkeypatch):
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
    ran = []
    with n.notify_job("job"):
        ran.append(True)
    assert ran == [True]


def test_self_test_sends_all_three_kinds(telegram, monkeypatch):
    monkeypatch.setattr(n.time, "sleep", lambda s: None)
    n._test()
    kinds = [t.split(":")[0] for t in texts(telegram)]
    assert kinds == ["▶️ Started", "✅ Finished", "▶️ Started", "❌ Failed"]


def test_load_env_reads_file_without_overriding(tmp_path, monkeypatch):
    env = tmp_path / ".env"
    env.write_text(
        "# comment\n\nA_KEY=plain\nexport B_KEY = 'quoted value'\nC_KEY=\"x=y\"\nNOT A LINE\n"
    )
    monkeypatch.setenv("C_KEY", "already set")
    for key in ("A_KEY", "B_KEY"):
        monkeypatch.delenv(key, raising=False)

    n.load_env(env)

    assert n.os.environ["A_KEY"] == "plain"
    assert n.os.environ["B_KEY"] == "quoted value"
    assert n.os.environ["C_KEY"] == "already set"


def test_load_env_missing_file_is_fine(tmp_path):
    n.load_env(tmp_path / "nope.env")
