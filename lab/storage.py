"""Upload, download, and list files in Cloudflare R2 (S3-compatible) with boto3.

Credentials come from environment variables: from `.env` on the server, or from
the Modal secret `r2` inside a job (`secrets=[modal.Secret.from_name("r2")]`).

    R2_ENDPOINT_URL        https://<account-id>.r2.cloudflarestorage.com
    R2_ACCESS_KEY_ID
    R2_SECRET_ACCESS_KEY
    R2_BUCKET              optional, defaults to cloud-ai-lab

Keys follow the CLAUDE.md layout: <project>/<datasets|checkpoints|runs>/...
Build them with `r2_key()` so every job lays files out the same way.
"""

import os
from functools import cache
from pathlib import Path

import boto3

DEFAULT_BUCKET = "cloud-ai-lab"
KINDS = ("datasets", "checkpoints", "runs")


def r2_key(project: str, kind: str, *parts: str) -> str:
    """Build an object key, e.g. r2_key("mnist", "checkpoints", "run-1", "latest.pt")."""
    if kind not in KINDS:
        raise ValueError(f"kind must be one of {KINDS}, got {kind!r}")
    segments = [s.strip("/") for s in (project, kind, *parts)]
    if any(not s or ".." in s.split("/") for s in segments):
        raise ValueError(f"empty or '..' path segment in {segments}")
    return "/".join(segments)


def bucket() -> str:
    return os.environ.get("R2_BUCKET", DEFAULT_BUCKET)


@cache
def client():
    """A boto3 S3 client pointed at R2. Raises KeyError naming any missing variable."""
    return boto3.client(
        "s3",
        endpoint_url=os.environ["R2_ENDPOINT_URL"],
        aws_access_key_id=os.environ["R2_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["R2_SECRET_ACCESS_KEY"],
        region_name="auto",  # R2 ignores regions; boto3 just needs one
    )


def upload(local_path: str | Path, key: str) -> str:
    """Upload a file. Overwrites `key` if it exists. Returns the rclone-style path."""
    client().upload_file(str(local_path), bucket(), key)
    return f"r2:{bucket()}/{key}"


def download(key: str, local_path: str | Path) -> Path:
    """Download `key` to `local_path`, creating parent folders."""
    local_path = Path(local_path)
    local_path.parent.mkdir(parents=True, exist_ok=True)
    client().download_file(bucket(), key, str(local_path))
    return local_path


def list_keys(prefix: str = "") -> list[str]:
    """All keys under `prefix`, sorted. Follows pagination (1000 keys per page)."""
    pages = client().get_paginator("list_objects_v2").paginate(Bucket=bucket(), Prefix=prefix)
    return sorted(obj["Key"] for page in pages for obj in page.get("Contents", []))


def exists(key: str) -> bool:
    return key in list_keys(key)
