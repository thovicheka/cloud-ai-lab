"""lab/tracking.py with W&B offline (nothing sent) and the checkpoint round trip via moto."""

import json

import pytest

from lab import tracking
from lab.checkpoints import RunCheckpoints


@pytest.fixture(autouse=True)
def fresh_wandb():
    """wandb keeps a process-wide setup that caches the environment from its first init.
    A Modal job starts one run per process; tests start many, so reset it after each."""
    yield
    import wandb

    wandb.teardown()


@pytest.fixture
def wandb_offline(monkeypatch, tmp_path):
    """W&B with a fake key in offline mode: runs are written to tmp_path, never uploaded."""
    monkeypatch.setenv("WANDB_API_KEY", "x" * 40)
    monkeypatch.setenv("WANDB_MODE", "offline")
    monkeypatch.setenv("WANDB_SILENT", "true")
    monkeypatch.setenv("WANDB_DIR", str(tmp_path))
    monkeypatch.setenv("WANDB_CONFIG_DIR", str(tmp_path / "config"))
    return tmp_path / "wandb"


def test_no_key_turns_wandb_off_with_a_warning(monkeypatch, tmp_path, capsys):
    monkeypatch.delenv("WANDB_API_KEY", raising=False)
    monkeypatch.setenv("WANDB_DIR", str(tmp_path))
    run = tracking.start_run("try-1", {"lr": 0.001})

    assert run.disabled
    assert "WANDB_API_KEY not set" in capsys.readouterr().out
    run.log({"train/loss": 1.0}, step=50)  # training code keeps calling W&B; nothing happens
    run.summary["best_test_loss"] = 0.5
    assert tracking.run_url(run) is None
    # a disabled run's id is random: keep the one from the checkpoint (or None)
    assert tracking.run_id(run, "abc123") == "abc123"
    assert tracking.run_id(run) is None
    run.finish(exit_code=1)


def test_new_run_uses_project_name_and_config(wandb_offline):
    run = tracking.start_run("try-1", {"lr": 0.001, "checkpoints": "r2:b/p/checkpoints/try-1/"},
                             dir=str(wandb_offline))  # fmt: skip
    try:
        assert not run.disabled
        assert run.project == tracking.PROJECT == "cloud-ai-lab"
        assert run.name == "try-1"
        assert run.config["lr"] == 0.001
        assert run.config["checkpoints"] == "r2:b/p/checkpoints/try-1/"
        assert tracking.run_id(run) == run.id
        run.log({"train/loss": 1.0}, step=50)
    finally:
        run.finish()


def test_resume_reuses_the_saved_id(wandb_offline):
    first = tracking.start_run("try-1", {"lr": 0.001}, dir=str(wandb_offline))
    saved = tracking.run_id(first)
    first.finish(exit_code=1)  # the lost run

    second = tracking.start_run("try-1", {"lr": 0.001}, run_id=saved, dir=str(wandb_offline))
    try:
        assert second.id == saved
    finally:
        second.finish()


def test_wandb_id_survives_the_checkpoint_round_trip(r2, wandb_offline, tmp_path):
    # the template's flow: save the W&B id in the checkpoint, lose the job, restore, resume
    first = tracking.start_run("try-1", {}, dir=str(wandb_offline))
    path = tmp_path / "ckpt" / "latest.pt"
    RunCheckpoints("mnist", "try-1").restore(path)
    path.write_text(json.dumps({"step": 1000, "wandb_id": tracking.run_id(first)}))
    RunCheckpoints("mnist", "try-1").save(path, is_best=True)
    first.finish(exit_code=1)

    restored = RunCheckpoints("mnist", "try-1").restore(tmp_path / "new-job" / "latest.pt")
    state = json.loads(restored.read_text())
    second = tracking.start_run("try-1", {}, run_id=state.get("wandb_id"), dir=str(wandb_offline))
    try:
        assert second.id == first.id
    finally:
        second.finish()
