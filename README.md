# cloud-ai-lab

A self-hosted cloud lab for ML and data science: always-on server, AI agents, on-demand GPUs, and experiment tracking.

Your laptop becomes just a window. Code, data, agents, and training jobs live in the cloud, so work keeps running when the laptop is closed, and you can check in from any device.

> **Status:** being built in public. Stage 1 (the server) is in progress. Docs are written as each stage is completed, including the mistakes along the way.

---

## How it fits together

```
 Laptop / phone ──(Tailscale, private)──►  Always-on server (Hetzner)
                                             ├─ code (GitHub working copy)
                                             ├─ remote IDE
                                             ├─ job queue (Prefect)
                                             └─ agents (coordinator + workers)
                                                   │
                         ┌─────────────────────────┼──────────────────────┐
                         ▼                         ▼                      ▼
                 GPU jobs (Modal, RunPod)   Storage (Cloudflare R2)   Tracking (W&B)
                         │                                                │
                         └──────────► notifications (Telegram) ◄──────────┘
```

| Component | Tool | Role |
|---|---|---|
| Control plane | Hetzner (Ubuntu 24.04, Singapore) | Always-on box that holds code, queue, and agents |
| Secure access | Tailscale | Private network; nothing exposed to the public internet |
| Dev environment | Remote IDE over SSH | Edit files on the server from the laptop |
| Code | GitHub | Version control; agents work on branches, never `main` |
| Big files | Cloudflare R2 | Datasets, checkpoints, model weights (no egress fees) |
| GPU compute | Modal (batch) + RunPod (interactive) | Rented by the second/hour, only when needed |
| Experiment tracking | Weights & Biases | Metrics, plots, audio/image samples per run |
| Job queue | Prefect | Queued / running / failed / done states, retries |
| Agents | LLM-based coordinator + workers | Agent-agnostic by design |
| Notifications | Telegram bot | A record of jobs starting, finishing, failing |

Design rules:
- **GPU spending is manual.** Agents never rent or launch paid compute on their own.
- **Agents work on branches only**, one branch/worktree per agent session.
- **Training checkpoints go to R2**, so a lost GPU never means lost work.
- **Secrets live only in `.env` on the server**, never in git.

---

## Docs

| Stage | Doc |
|---|---|
| 1. Server, access, dev tools | [docs/01-server-setup.md](docs/01-server-setup.md) |
| 2. Storage (R2) | coming |
| 3. GPU compute | coming |
| 4. Experiment tracking | coming |
| 5. Job queue | coming |
| 6. Agents | coming |
| 7. Notifications | coming |
| Why each tool was chosen | [docs/decisions.md](docs/decisions.md) |

---

## Rough cost

| Item | Monthly |
|---|---|
| Server (Hetzner CPX22, Singapore) | ~$23 + VAT |
| R2 storage (~100–300 GB) | ~$2–5 |
| GPUs | $20–120, depending on use |
| Tailscale, W&B, GitHub | free tiers |

Prices change; check each provider before you start.

---

## License

MIT
