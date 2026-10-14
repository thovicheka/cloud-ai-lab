"""R2 from Modal: write a small file to R2 from inside a Modal container, then list it.

Needs the Modal secret `r2` (see lab/storage.py for its keys).

Run (on the server, from the repo root):
    modal run jobs/r2_hello.py

Cost: CPU only, a few seconds: well under $0.01 (modal.com/pricing, 2026-10-13).
Writes to r2:cloud-ai-lab/hello/runs/<UTC timestamp>/hello.txt
"""

import modal

BOTO3_VERSION = "1.43.112"

app = modal.App("r2-hello")
image = (
    modal.Image.debian_slim(python_version="3.12")
    .uv_pip_install(f"boto3=={BOTO3_VERSION}")
    .add_local_python_source("lab")
)


# retries=0 (Modal's default, made explicit): a failure is never re-run on its own.
@app.function(image=image, secrets=[modal.Secret.from_name("r2")], timeout=120, retries=0)
def write_hello() -> list[str]:
    import socket
    import tempfile
    from datetime import datetime, timezone

    from lab import storage

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    key = storage.r2_key("hello", "runs", stamp, "hello.txt")

    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
        f.write(f"hello from Modal container {socket.gethostname()} at {stamp}\n")
    print("uploaded", storage.upload(f.name, key))

    return storage.list_keys(storage.r2_key("hello", "runs", stamp))


@app.local_entrypoint()
def main():
    from lab.notify import notify_job  # here, not at the top: containers don't need it

    with notify_job("r2-hello") as job:
        keys = write_hello.remote()
        job.note = "\n".join(keys)
    for key in keys:
        print("in R2:", key)
