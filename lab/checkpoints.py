"""Best + latest checkpoint for one training run, kept in R2.

Each run has exactly two objects, overwritten in place, so storage never grows:
    <project>/checkpoints/<run>/latest.pt   the most recent save (resume from this)
    <project>/checkpoints/<run>/best.pt     the save with the best metric so far

Framework-agnostic: it moves files; the training code decides what goes in them.
Store the best metric inside the checkpoint so it survives a restart:

    ckpts = RunCheckpoints("mnist", run_name, mode="min")
    if ckpts.restore(path):              # resume
        state = torch.load(path); best = state["best"]
    ...
    is_best = ckpts.improved(val_loss, best)
    if is_best:
        best = val_loss
    torch.save({..., "best": best}, path)
    ckpts.save(path, is_best=is_best)
"""

from pathlib import Path

from lab import storage


class RunCheckpoints:
    def __init__(self, project: str, run: str, *, mode: str = "min"):
        if mode not in ("min", "max"):
            raise ValueError(f"mode must be 'min' or 'max', got {mode!r}")
        self.mode = mode
        self.latest_key = storage.r2_key(project, "checkpoints", run, "latest.pt")
        self.best_key = storage.r2_key(project, "checkpoints", run, "best.pt")

    def improved(self, metric: float, best: float | None) -> bool:
        """True if `metric` beats `best` (None means nothing saved yet)."""
        if best is None:
            return True
        return metric < best if self.mode == "min" else metric > best

    def restore(self, local_path: str | Path) -> Path | None:
        """Download latest.pt to `local_path`; None if this run has no checkpoint yet."""
        if not storage.exists(self.latest_key):
            return None
        return storage.download(self.latest_key, local_path)

    def save(self, local_path: str | Path, *, is_best: bool) -> None:
        """Upload `local_path` as latest.pt, and also as best.pt if `is_best`."""
        # best first: a crash between the two uploads then leaves latest one save
        # behind (resume redoes a few steps) rather than best missing a new record.
        if is_best:
            storage.upload(local_path, self.best_key)
        storage.upload(local_path, self.latest_key)
