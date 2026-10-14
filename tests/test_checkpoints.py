"""lab/checkpoints.py against moto's in-memory S3."""

import pytest

from lab import storage
from lab.checkpoints import RunCheckpoints


def save(ckpts, tmp_path, content, *, is_best):
    f = tmp_path / "ckpt.pt"
    f.write_text(content)
    ckpts.save(f, is_best=is_best)


def test_keys_follow_layout():
    c = RunCheckpoints("mnist", "run-1")
    assert c.latest_key == "mnist/checkpoints/run-1/latest.pt"
    assert c.best_key == "mnist/checkpoints/run-1/best.pt"


def test_improved_min_and_max():
    lo, hi = RunCheckpoints("p", "r", mode="min"), RunCheckpoints("p", "r", mode="max")
    assert lo.improved(1.0, None) and hi.improved(1.0, None)
    assert lo.improved(0.5, 1.0) and not lo.improved(1.0, 1.0) and not lo.improved(2.0, 1.0)
    assert hi.improved(2.0, 1.0) and not hi.improved(1.0, 1.0) and not hi.improved(0.5, 1.0)
    with pytest.raises(ValueError):
        RunCheckpoints("p", "r", mode="lowest")


def test_restore_returns_none_for_new_run(r2, tmp_path):
    assert RunCheckpoints("p", "new").restore(tmp_path / "x.pt") is None


def test_fresh_run_can_save_to_a_missing_folder(r2, tmp_path):
    # like /tmp/ckpt/latest.pt in a new Modal container: the folder doesn't exist yet
    path = tmp_path / "ckpt" / "latest.pt"
    c = RunCheckpoints("p", "fresh")
    assert c.restore(path) is None
    path.write_text("step 500")  # torch.save fails here if the folder is missing
    c.save(path, is_best=True)
    resumed = RunCheckpoints("p", "fresh").restore(tmp_path / "other" / "x.pt")
    assert resumed.read_text() == "step 500"


def test_resume_gets_latest_and_best_only_moves_on_improvement(r2, tmp_path):
    c = RunCheckpoints("p", "r1")
    save(c, tmp_path, "step 100", is_best=True)
    save(c, tmp_path, "step 200", is_best=False)
    save(c, tmp_path, "step 300", is_best=True)
    save(c, tmp_path, "step 400", is_best=False)

    # a restarted job sees only what's in R2
    restored = RunCheckpoints("p", "r1").restore(tmp_path / "restored" / "latest.pt")
    assert restored.read_text() == "step 400"
    assert storage.download(c.best_key, tmp_path / "best.pt").read_text() == "step 300"


def test_only_two_objects_per_run(r2, tmp_path):
    c = RunCheckpoints("p", "r1")
    for step in range(10):
        save(c, tmp_path, f"step {step}", is_best=step % 3 == 0)

    assert storage.list_keys("p/checkpoints/r1/") == [c.best_key, c.latest_key]


def test_runs_are_independent(r2, tmp_path):
    save(RunCheckpoints("p", "a"), tmp_path, "a", is_best=True)
    assert RunCheckpoints("p", "b").restore(tmp_path / "b.pt") is None
    assert RunCheckpoints("p", "a").restore(tmp_path / "a.pt").read_text() == "a"
