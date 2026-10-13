# Stage 0 — Agent on the server

**What you'll have working by the end:** Claude Code running inside `tmux` on the server, logged in with your Claude subscription, so an agent can work on this repo while your laptop is closed.

**Status:** ✅ Stage 0 complete (task 0.1 done; this doc is task 0.2).

**How to read this guide:** instructions use placeholders like `<username>`; replace them with your own values. After key steps, an **Example from this build** block shows the real commands and output from the author's setup:

| Placeholder | In this build |
|---|---|
| `<username>` (server user) | `thovicheka` |
| Tailscale name | `lab` |
| `<session-name>` (tmux) | `claude` |
| `<email>`, login codes, tokens | kept private |

## Prerequisites
- [Stage 1](01-server-setup.md) done: you can `ssh lab`, and `git`, `tmux` work on the server (Part D).
- This repo cloned at `~/projects/cloud-ai-lab` on the server (step D3).
- A paid **Claude subscription** (Pro or Max) on claude.ai. An API key also works but bills per token; this build uses the subscription.
- A browser on your laptop, for the one-time login.

---

## Steps

### 1. Install Claude Code *(on the server)*
```bash
curl -fsSL https://claude.ai/install.sh | bash   # installs to ~/.local/bin/claude, no sudo needed
```
*What it does:* downloads the native Claude Code binary into your home folder. Takes under a minute. No `sudo`, no Node.js.

> **If you see** a note that `~/.local/bin` is not in your `PATH`, the binary installed fine but the shell can't find it yet. Step 2 fixes it.

### 2. Reload the shell and check the version *(on the server)*
```bash
source ~/.bashrc
claude --version
```
*What it does:* makes the current shell pick up the new `PATH`, then confirms the binary runs.

> **If you see** `claude: command not found`, `~/.local/bin` isn't on your `PATH`. Add it and reload:
> ```bash
> echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
> source ~/.bashrc
> ```
> Opening a new SSH session also works, because Ubuntu's `~/.profile` adds `~/.local/bin` at login if the folder exists.

<details><summary>Example from this build</summary>

```console
thovicheka@ubuntu-4gb-sin-2:~$ claude --version
2.1.296 (Claude Code)

thovicheka@ubuntu-4gb-sin-2:~$ which claude
/home/thovicheka/.local/bin/claude

thovicheka@ubuntu-4gb-sin-2:~$ ls -la ~/.local/bin/claude
lrwxrwxrwx 1 thovicheka thovicheka 53 Oct 13 15:03 /home/thovicheka/.local/bin/claude -> /home/thovicheka/.local/share/claude/versions/2.1.296
```
**Result:** ✅ installed (2026-10-13). `~/.local/bin/claude` is a link to a versioned binary; updates swap the link.
**Problem hit:** `claude` was run once *before* the install script:
```console
thovicheka@ubuntu-4gb-sin-2:~$ claude
claude: command not found
```
**Cause:** Claude Code wasn't installed yet. **Fix:** run step 1, then `source ~/.bashrc`; `claude --version` then worked.
**Note:** the install script's own output wasn't saved during the build, so it isn't shown here.
</details>

### 3. Start a tmux session for the agent *(on the server)*
```bash
tmux new -s claude                 # named session that survives SSH disconnects
cd ~/projects/cloud-ai-lab         # start Claude here so it reads this repo's CLAUDE.md
```
*What it does:* the agent lives inside `tmux`, so closing the laptop or losing Wi-Fi doesn't kill it. See [Stage 1, E2](01-server-setup.md) for the tmux basics.

> **If you see** `duplicate session: claude`, the session already exists. Attach to it instead: `tmux attach -t claude`.

### 4. Launch Claude Code and log in with your subscription *(on the server, inside tmux)*
```bash
claude
```
*What it does:* starts Claude Code. On first launch it asks you to pick a theme, then a login method.

1. Choose **Claude account with subscription** (not "Anthropic Console / API key").
2. Claude Code prints a long login URL. The server has no browser, so **copy the URL and open it on your laptop**.
3. Sign in on claude.ai and approve. The page shows a **code**.
4. Paste the code back into the server terminal and press Enter.
5. Accept the folder-trust prompt for `~/projects/cloud-ai-lab`.

> **If you see** `Invalid OAuth request — Unknown scope: user:mcp_` (or any "invalid link" error), tmux wrapped the long URL across lines and your copy was cut short. Zoom the pane with `Ctrl-b z` (or widen the window), copy it again, and join it into **one line** with no spaces or line breaks before opening it. Check the `scope=` part: it must end in `user%3Amcp_servers`, not `user%3Amcp_`.
>
> **If you see** `Invalid code` or the login times out, the code is single-use and expires quickly. Press Enter to restart the login and use the new URL.
>
> **If you see** a prompt for an API key, you picked the Console option. Exit with `/exit` (or `Ctrl-c` twice), run `claude` again, and choose the subscription option.
>
> **If** a browser tries to open on the server or nothing happens, that's expected on a headless machine. Use the printed URL from your laptop.
>
> **If you need to switch accounts later,** run `/logout` inside Claude Code, then `/login`.

> **If you see** a tmux notice about **focus events** after login, turn them on so Claude Code can tell when its pane is active:
> ```bash
> echo 'set -g focus-events on' >> ~/.tmux.conf && tmux source-file ~/.tmux.conf
> ```

<details><summary>Example from this build</summary>

The login URL (masked: `https://claude.ai/oauth/authorize?...`) wrapped across lines in tmux, and the copied URL was cut at `user%3Amcp_`. Opening it gave:
```text
Invalid OAuth request — Unknown scope: user:mcp_
```
**Result:** ❌ login failed.
**Cause:** tmux wrapped the long URL, so the copy stopped at `user%3Amcp_` and the scope `user:mcp_servers` was cut in half.
**Fix:** rejoined the URL into one line (the scope must read `user%3Amcp_servers`), opened it on the laptop, authorized, and pasted the code back into the server terminal.
**Result:** ✅ logged in with the subscription. Claude Code started in **auto mode**.
**Second problem:** tmux showed the focus-events notice. **Fix:**
```console
thovicheka@ubuntu-4gb-sin-2:~$ echo 'set -g focus-events on' >> ~/.tmux.conf && tmux source-file ~/.tmux.conf
thovicheka@ubuntu-4gb-sin-2:~$ cat ~/.tmux.conf
set -g focus-events on
```
**Result:** ✅ notice gone.
</details>

*Why the subscription and not an API key:* agent sessions use a lot of tokens; a subscription has a fixed monthly price instead of a per-token bill. API keys are kept for scripts that call the model directly (Stage 5).

### 5. Detach and reattach *(on the server)*
```text
Ctrl-b  then  d                    # detach: Claude keeps running in the background
```
```bash
tmux attach -t claude              # later, from any SSH session: back to the agent
```
*What it does:* lets you close the terminal without stopping the agent.

> **If you see** `no sessions` after `tmux attach`, the server rebooted (tmux sessions don't survive a reboot). Repeat steps 3–4; the login is saved, so step 4 skips straight to the prompt.

---

## Verify it worked

From a fresh SSH session on the server:
```bash
tmux ls
claude --version
```
Expected: a line starting `claude: 1 windows` and a version line ending in `(Claude Code)`. Then `tmux attach -t claude` shows the Claude Code prompt, already logged in.

<details><summary>Example from this build</summary>

```console
thovicheka@ubuntu-4gb-sin-2:~$ tmux ls
claude: 1 windows (created Tue Oct 13 15:15:21 2026) (attached)
test: 1 windows (created Tue Oct 13 13:04:01 2026)      # left over from Stage 1, E2

thovicheka@ubuntu-4gb-sin-2:~$ claude --version
2.1.296 (Claude Code)

thovicheka@ubuntu-4gb-sin-2:~$ free -h      # memory with one agent running
               total        used        free      shared  buff/cache   available
Mem:           3.7Gi       1.6Gi       333Mi       4.8Mi       2.0Gi       2.1Gi
Swap:          4.0Gi       512Ki       4.0Gi

thovicheka@ubuntu-4gb-sin-2:~$ ps -o pid,rss,cmd -C claude
    PID   RSS CMD
   5708 396176 claude                          # ~390 MB for one session
```
**Result:** ✅ Claude Code is running inside the `claude` tmux session and wrote this doc (task 0.2) from there.
**Memory note:** one session uses about 400 MB. On a 4 GB server, two or three parallel sessions fit; more than that will push into swap.
</details>

---

## Rules to keep
- The agent's rules live in [`CLAUDE.md`](../CLAUDE.md); it reads them on every start. Assign work by task ID from [`ROADMAP.md`](ROADMAP.md).
- Claude Code has no `sudo` password. Anything needing `sudo` comes back to you as an exact command to run.
- Run each parallel agent in its own tmux window and its own branch.
