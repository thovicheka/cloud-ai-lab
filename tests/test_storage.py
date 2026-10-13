"""lab/storage.py against moto's in-memory S3: no network, no real keys."""

import pytest

from lab import storage


def test_r2_key_layout():
    assert storage.r2_key("mnist", "checkpoints", "run-1", "latest.pt") == (
        "mnist/checkpoints/run-1/latest.pt"
    )
    assert storage.r2_key("p", "runs", "/a/b/") == "p/runs/a/b"


@pytest.mark.parametrize(
    "args", [("p", "models", "x"), ("", "runs", "x"), ("p", "runs", ""), ("p", "runs", "../x")]
)
def test_r2_key_rejects_bad_paths(args):
    with pytest.raises(ValueError):
        storage.r2_key(*args)


def test_upload_download_round_trip(r2, tmp_path):
    src = tmp_path / "in.bin"
    src.write_bytes(bytes(range(256)) * 100)
    key = storage.r2_key("p", "runs", "r1", "in.bin")

    assert storage.upload(src, key) == "r2:test-bucket/p/runs/r1/in.bin"
    out = storage.download(key, tmp_path / "nested" / "out.bin")

    assert out.read_bytes() == src.read_bytes()


def test_upload_overwrites(r2, tmp_path):
    f = tmp_path / "f.txt"
    key = "p/runs/f.txt"
    f.write_text("one")
    storage.upload(f, key)
    f.write_text("two")
    storage.upload(f, key)

    assert storage.download(key, tmp_path / "g.txt").read_text() == "two"
    assert storage.list_keys("p/") == [key]


def test_list_keys_prefix_and_pagination(r2, tmp_path):
    f = tmp_path / "f"
    f.write_text("x")
    for i in range(1005):  # more than one page of 1000
        storage.upload(f, f"p/runs/{i:04d}")
    storage.upload(f, "other/runs/x")

    keys = storage.list_keys("p/runs/")
    assert len(keys) == 1005
    assert keys[0] == "p/runs/0000" and keys[-1] == "p/runs/1004"


def test_exists(r2, tmp_path):
    f = tmp_path / "f"
    f.write_text("x")
    storage.upload(f, "p/runs/a.txt")

    assert storage.exists("p/runs/a.txt")
    assert not storage.exists("p/runs/a")  # a prefix is not a file


def test_missing_credentials_name_the_variable(monkeypatch):
    monkeypatch.delenv("R2_ENDPOINT_URL", raising=False)
    storage.client.cache_clear()
    with pytest.raises(KeyError, match="R2_ENDPOINT_URL"):
        storage.client()
