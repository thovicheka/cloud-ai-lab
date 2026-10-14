"""Hello-GPU: prove Modal hands us a GPU, runs PyTorch on it, and stops by itself.

Run (on the server, from the repo root):
    modal run jobs/hello_gpu.py

Cost (Modal prices checked 2026-10-13; check modal.com/pricing before running):
    T4 = $0.000164/s (~$0.59/h). Expect ~1-2 min of GPU time on the first run
    (container start + torch import + matmul), so ~$0.01-0.02. Building the image
    the first time adds a few minutes of CPU time, under $0.01. Total: < $0.05,
    covered by the Starter plan's free monthly credit.
"""

import modal

GPU = "T4"  # cheapest Modal GPU
TORCH_VERSION = "2.14.1"
NUMPY_VERSION = "2.5.3"  # torch warns "Failed to initialize NumPy" without it

app = modal.App("hello-gpu")
image = modal.Image.debian_slim(python_version="3.12").uv_pip_install(
    f"torch=={TORCH_VERSION}", f"numpy=={NUMPY_VERSION}"
)


# timeout: a hard stop, so a hung job can never bill for more than 5 minutes.
@app.function(image=image, gpu=GPU, timeout=300)
def hello(n: int = 4096) -> dict:
    import subprocess
    import time

    import torch

    print(subprocess.run(["nvidia-smi"], capture_output=True, text=True, check=True).stdout)

    if not torch.cuda.is_available():
        raise RuntimeError("torch can't see a GPU")

    a = torch.randn(n, n, device="cuda")
    b = torch.randn(n, n, device="cuda")
    a @ b  # warm-up: the first call pays for CUDA kernel loading
    torch.cuda.synchronize()

    start = time.perf_counter()
    a @ b
    torch.cuda.synchronize()  # GPU calls are async; wait before stopping the clock
    seconds = time.perf_counter() - start

    # Plain Python types only: the result is unpickled on the server, which has no torch.
    # torch.__version__ is a TorchVersion, not a str; returning it fails with
    # "DeserializationError: ... the 'torch' module is not available in the local environment".
    return {
        "gpu": str(torch.cuda.get_device_name(0)),
        "torch": str(torch.__version__),
        "cuda": str(torch.version.cuda),
        "matmul": f"{n}x{n}",
        "ms": round(seconds * 1000, 2),
        "tflops": round(2 * n**3 / seconds / 1e12, 2),
    }


@app.local_entrypoint()
def main():
    from lab.notify import notify_job  # here, not at the top: containers don't need it

    with notify_job("hello-gpu", gpu=GPU) as job:
        result = hello.remote()
        job.note = f"{result['gpu']}: {result['tflops']} TFLOPS"
    for key, value in result.items():
        print(f"{key:>9}: {value}")
