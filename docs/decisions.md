# Decisions

Why each tool was picked, and what it was picked over. Updated as the build goes.

## Always-on server: Hetzner
- **Why a server at all:** an AI chat tab or a laptop terminal only runs while it's open. GPU jobs survive a closed laptop, but the layer that queues, watches, and coordinates them doesn't, unless it lives on a machine that's always on.
- **Why Hetzner:** roughly half the price of DigitalOcean for the same specs.
- **Trade-off:** strict signup checks. New accounts outside Europe may need prepaid credit (it pays your first bills). DigitalOcean, Vultr, or Akamai work as drop-in replacements; every command after server creation is the same.
- **Region:** Singapore, the closest Hetzner region to Southeast Asia. A European region adds noticeable lag to every keystroke in a remote IDE.
- **Size:** 2 vCPU / 4 GB. Agents call model APIs; the "thinking" happens on the provider's servers, so the box mostly waits on the network.

## Secure access: Tailscale
- Private network between your own devices; the server is never exposed to the public internet once the firewall is on.
- Free for personal use and simpler than running a VPN yourself.

## Code: GitHub
- Agents push to branches, never `main`. A human reviews and merges.
- Public repo with secret scanning and push protection on.

## Big-file storage: Cloudflare R2 (over AWS S3, GCS, Backblaze B2)
- **Object storage, not a database:** it stores files (datasets, checkpoints, models), not queryable rows.
- **Zero egress fees** is the deciding factor. Training jobs download the dataset to a GPU on every run. Example: a 50 GB dataset pulled 10 times a month is 500 GB of downloads, roughly $45 on S3 and $0 on R2.
- **S3-compatible:** rclone, `boto3`, and ML data loaders work unchanged, so switching providers later is easy.
- **Cheap storage** (~$0.015/GB/month after 10 GB free). Expected cost for this lab: ~$1–5/month at 100–300 GB.
- **Runner-up: Backblaze B2.** Cheaper storage, free egress up to a monthly limit. R2 wins on simplicity: no limits to track.
- **Rejected: Hetzner Object Storage.** Cheap, but EU-only regions, far from a Singapore server.
- **Cost control:** checkpoints are what grows. Keep only the best and the latest per run.

## GPU compute: Modal + RunPod (over Vast.ai)
- **Modal** for batch jobs: billed per second, starts and stops on its own.
- **RunPod** for interactive sessions when you need a GPU box to poke at.
- **Vast.ai rejected:** cheapest, but instances can be interrupted, which is painful for long training runs.

## Experiment tracking: Weights & Biases (over self-hosted MLflow)
- Hosted, free tier, nothing to run on the small server.
- Logs images and audio per run, which matters for speech and image projects.

## Job queue: Prefect
- Gives jobs explicit states (queued, running, completed, failed), retries, and a UI, without a heavy setup.

## Agents: start with two
- A coordinator and a coding agent first; add more later. An agent is "a job description plus tools," so roles are cheap to add or change.
- Prompts are not enforcement. What an agent can do is decided by which tools and credentials it's given.
- Set a monthly spending limit on any model API key before letting agents loop on their own.

## Notifications: Telegram bot
- Free, works on any phone, easy to build. Serves as a running record of what started, finished, and failed.

## Stage 2 job design
- **The local entrypoint runs on the server, the function on Modal.** Notifications and `.env` stay on the server, so Modal only holds the R2 secret. The catch: the server side has no PyTorch, so functions return plain Python values only.
- **Two checkpoints per run, overwritten in place** (`latest.pt` to resume, `best.pt` to keep). Storage stays flat however long a run trains. `best.pt` is uploaded first: a crash between the two uploads costs a few redone steps, never a lost best.
- **`retries=0` on every job.** A failure stops the job and bills once; a human decides whether to run it again. The training job resumes, so a manual re-run loses at most one checkpoint interval.
- **`--run-name` has no default.** The same name resumes; a new name starts fresh. A default would make it too easy to resume into the wrong run.
