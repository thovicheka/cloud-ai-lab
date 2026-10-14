# Stage 6 — Notifications (Telegram)

**What you'll have working by the end:** your phone gets a Telegram message whenever a job starts, finishes, fails, or is stopped, with how long it ran and its estimated GPU cost. You can close the laptop and still know when a training run is done.

**Status:** ✅ Stage 6 complete (tasks 6.1–6.2; this doc is task 6.3).

**How to read this guide:** instructions use placeholders like `<bot-token>`; replace them with your own values. After key steps, an **Example from this build** block shows the real commands and output from the author's setup:

| Placeholder | In this build |
|---|---|
| `<bot-token>` | kept private (`123456:ABC***`) |
| `<chat-id>` | kept private |
| `<bot-name>` | kept private |

**Which machine:** steps 1–3 happen in the Telegram app (phone or laptop). Everything else runs **on the server**, from the repo root `~/projects/cloud-ai-lab`.

This bot is separate from the AI News bot. Why Telegram: see [decisions.md](decisions.md#notifications-telegram-bot).

## Prerequisites
- Telegram installed on your phone.
- This repo cloned at `~/projects/cloud-ai-lab` on the server, with `uv` (Stage 1).
- For messages from real GPU jobs: [Stage 2](02-gpu-compute.md). Steps 1–6 work without it.

---

## Steps

### 1. Create a bot *(Telegram app)*
Open a chat with **@BotFather**, send `/newbot`, and answer its two questions (a display name, then a username ending in `bot`).

*What it does:* creates the bot and replies with its **token**, which looks like `123456:ABC...`. The token is a password for the bot: anyone with it can send messages as your bot. Don't paste it anywhere except `.env` in step 4.

### 2. Send your bot a message *(Telegram app)*
Open your new bot (BotFather's reply links to it), press **Start**, and send any message.

*What it does:* bots can't message someone first. Until you've written to it, every send fails.

### 3. Get your chat ID *(Telegram app)*
Open a chat with **@userinfobot** and send it any message.

*What it does:* it replies with your numeric user ID. For a one-to-one chat with your bot, that number is the chat ID.

### 4. Add the token and chat ID to `.env` *(on the server)*
```bash
test -f .env || (cp .env.example .env && chmod 600 .env)   # skip if Stage 2 already made it
nano .env
```
Fill in these two lines:
```bash
TELEGRAM_BOT_TOKEN=<bot-token>
TELEGRAM_CHAT_ID=<chat-id>
```
*What it does:* `lab/notify.py` reads both from `.env` (or from environment variables, which win). `.env` is git-ignored and readable only by you.

The Telegram keys stay **on the server only**. Don't add them to the Modal secret: notifications are sent by the part of each job that runs on the server (see step 7).

### 5. Send a test message *(on the server)*
```bash
uv run python -m lab.notify "hello from the lab"
echo $?    # 0 = sent, 1 = not sent (the reason is printed)
```
*What it does:* sends one message to your chat. Free, no GPU, no Modal.

> **If you see** `notify: TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID not set; not sent: ...`, one of the two keys is missing or empty in the repo's `.env`. Check it (step 4).
>
> **If you see** `notify: Telegram returned HTTP 401 ...`, the token is wrong. Copy it again from @BotFather (`/mybots` → your bot → API Token).
>
> **If you see** `notify: Telegram returned HTTP 400 Bad Request: chat not found`, the chat ID is wrong, or you haven't sent your bot a message yet (step 2).
>
> **If you see** `notify: couldn't reach Telegram (...)`, the server can't reach `api.telegram.org`. Outgoing HTTPS normally works; try again later.
>
> Error messages never print the token.

### 6. Test all three job messages *(on the server)*
```bash
uv run python -m lab.notify --test
```
*What it does:* runs two fake one-second "jobs", one that finishes and one that fails, without any GPU or Modal. **Expected:** four messages: ▶️ Started, ✅ Finished, ▶️ Started, ❌ Failed. **Cost:** $0.

<details><summary>Example from this build</summary>

Before the bot existed (no keys in `.env`), the same command shows the fallback. Nothing is sent, the messages are printed, and the command still succeeds:
```console
$ uv run python -m lab.notify --test
notify: TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID not set; not sent: ▶️ Started: notify test: a job that finishes (T4)
notify: TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID not set; not sent: ✅ Finished: notify test: a job that finishes in 0m 01s, ~$0.00 on T4
this is the note line
notify: TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID not set; not sent: ▶️ Started: notify test: a job that fails (T4)
notify: TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID not set; not sent: ❌ Failed: notify test: a job that fails after 0m 01s, ~$0.00 on T4
RuntimeError: simulated failure (this is expected)
$ echo $?
0
```
**Result:** ✅ A broken or missing Telegram setup never stops a job.
</details>

### 7. Add notifications to a job *(in the code)*
The jobs in `jobs/` already do this. For a new job, wrap the remote call in the **local entrypoint**:
```python
@app.local_entrypoint()
def main(run_name: str):
    from lab.notify import notify_job  # here, not at the top: containers don't need it

    with notify_job(f"train {PROJECT} {run_name}", gpu=GPU) as job:
        result = train.remote(run_name=run_name)
        job.note = f"best test loss {result['best_test_loss']}"   # optional extra line
```
*What it does:*

| When | Message |
|---|---|
| the block starts | `▶️ Started: <name> (<gpu>)` |
| it ends normally | `✅ Finished: <name> in <time>, ~$<cost> on <gpu>` + the note |
| it raises an error | `❌ Failed: <name> after <time>, ~$<cost> on <gpu>` + the error |
| you press Ctrl-C | `⏹️ Stopped: <name> after <time>, ~$<cost> on <gpu>` |

The local entrypoint runs on the server, where `.env` is, so Modal containers never need the Telegram keys. Pass `gpu=None` (or leave it out) for CPU-only jobs; the message then says `CPU only, < $0.01`.

> **Adapting:** the cost is wall-clock time on the server × the GPU's price in `GPU_PRICE_PER_SECOND` (`lab/notify.py`, Modal prices from 2026-10-13). For a GPU that isn't in the table, add its price there. For several GPUs, pass e.g. `gpu="A100-40GB:2"`.

## Verify it worked
Run any Stage 2 job (costs money; see [Stage 2](02-gpu-compute.md) for prices):
```bash
modal run jobs/hello_gpu.py
```
Expected in Telegram: `▶️ Started: hello-gpu (T4)`, then `✅ Finished: hello-gpu in ...`.

<details><summary>Example from this build</summary>

Real messages from real Modal jobs (2026-10-14):

`modal run jobs/hello_gpu.py`:
```text
✅ Finished: hello-gpu in 0m 09s, ~$0.00 on T4
Tesla T4: 3.84 TFLOPS
```
`modal run jobs/train_template.py --run-name try-1 --crash-at-step 1100`: ▶️ Started, then ❌ Failed (`RuntimeError: simulated crash at step 1100`).

`modal run jobs/train_template.py --run-name try-1`: ✅ Finished.

**Result:** ✅ all three kinds of message arrived from real jobs.
</details>

---

## Known limits
- **Cost is an estimate.** Duration is measured on the server and includes container start-up, so it slightly overestimates GPU time. CPU and memory charges (a few %) aren't counted. Modal's dashboard has the real bill.
- **Ctrl-C hasn't been tested on a real run.** If `modal run` stops the job some other way than a `KeyboardInterrupt` in the entrypoint, no ⏹️ Stopped message arrives.
- **`modal run --detach`:** if the server-side command exits, the job keeps going on Modal but no Finished message arrives. Stage 4 (Prefect) is the place to fix that.
- **Long messages** are cut at Telegram's 4096-character limit; error text is cut at 500 characters.

## What's in the repo

| File | What it is |
|---|---|
| `lab/notify.py` | `notify(text)`, `notify_job(...)`, the `.env` reader, GPU prices; run with `-m` for the tests above |
| `tests/test_notify.py` | 16 offline tests against a fake Telegram API: `uv run pytest -q` |
| `.env.example` | `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` with fake values |
