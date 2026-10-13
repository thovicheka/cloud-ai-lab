# Stage 1 — Server, access, and dev tools

**What you'll have working by the end:** an always-on cloud server that only your own devices can reach, where code, agents, and long jobs keep running after you close your laptop.

**Status:** Parts A–D done · E1 (R2 storage) done · E2 ("close the laptop" test) next.

Placeholders: `<server-ip>`, `<username>`, `<github-username>`, `<email>`.

## Prerequisites
- A laptop with a terminal (macOS or Linux; Windows works with WSL).
- A credit card or PayPal for the server provider.
- About 2–3 hours, including account verification waits.

## Know which machine you're on

Most mistakes in this stage come from running a command on the wrong machine. After you SSH in, that terminal tab **is the server** until you type `exit`. Read the prompt:

| Prompt looks like | You're on |
|---|---|
| `you@your-laptop ~` | your laptop |
| `<username>@<server-name>:~$` or `root@<server-name>:~#` | the server |

Tip: keep one terminal tab for the laptop and one for the server.

---

## Part A — GitHub account

- [x] **A1. Create a dedicated GitHub account and turn on 2FA.**
  *What it does:* gives the project a clean home. 2FA means a stolen password alone can't take over your code. Save the recovery codes somewhere off your laptop.

- [x] **A2. Create the repository** (Python `.gitignore`, MIT license).
  *What it does:* the Python `.gitignore` already excludes `.env`, so secret files are never committed. MIT lets anyone reuse the project.

- [ ] **A3. Turn on secret scanning + push protection** (repo Settings → Code security).
  *What it does:* GitHub blocks pushes that contain something that looks like an API key.

- [x] **A4. Give the laptop its own SSH key for this account** *(on your laptop; only needed if the laptop already uses another GitHub account)*.
  ```bash
  ssh-keygen -t ed25519 -C "<email>" -f ~/.ssh/id_ed25519_lab
  pbcopy < ~/.ssh/id_ed25519_lab.pub   # paste into GitHub → Settings → SSH and GPG keys
  ```
  Add to `~/.ssh/config`:
  ```
  Host github-lab
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_ed25519_lab
    IdentitiesOnly yes
    AddKeysToAgent yes
    UseKeychain yes
  ```
  Save the passphrase in the macOS keychain so you aren't asked on every push:
  ```bash
  ssh-add --apple-use-keychain ~/.ssh/id_ed25519_lab
  ssh -T git@github-lab   # should greet the NEW username
  ```
  *What it does:* GitHub won't let one key belong to two accounts. The `github-lab` alias tells git "for this address, use the new key." Old projects keep using `github.com` and the old account.

  > **If you see** `<path> already exists. Overwrite (y/n)?` on a second run, answer `n`. You already have the key; the `-C` text is only a label.

- [x] **A5. Point the repo at the new account and set your identity** *(inside the repo folder on your laptop)*.
  ```bash
  git config user.name "<Your Name>"
  git config user.email "<email or noreply address>"
  git remote set-url origin git@github-lab:<github-username>/cloud-ai-lab.git
  git commit --allow-empty -m "Test push" && git push
  ```
  *What it does:* the name/email is stamped on every commit in this repo. The remote URL decides which key, and so which account, pushes.
  Optional privacy: GitHub → Settings → Emails → "Keep my email addresses private," then use the `...@users.noreply.github.com` address above.

---

## Part B — Rent the server

- [x] **B1. Create a Hetzner account.**
  *What it does:* Hetzner rents you the computer.

  > **If you see** a request to add prepaid credit (e.g. $25), it's a fraud check for new accounts, mostly outside Europe. The credit pays your first bills; it isn't a fee. A "Private" customer needs no VAT ID.
  >
  > **Adapting:** DigitalOcean, Vultr, or Akamai work instead. Everything after server creation is the same.

- [x] **B2. Make an SSH key for logging into the server** *(on your laptop, before creating the server)*.
  ```bash
  ssh-keygen -t ed25519 -C "laptop-to-server" -f ~/.ssh/id_ed25519_hetzner
  pbcopy < ~/.ssh/id_ed25519_hetzner.pub
  ```
  *What it does:* the `.pub` half goes on the server like a lock; the private half stays on your laptop like the key. Never share the file without `.pub`.

- [x] **B3. Create the server:** Singapore · Ubuntu 24.04 · CPX22 (2 vCPU / 4 GB) · paste the key under **SSH keys** and make sure it's ticked.
  *What it does:* Singapore is closest to Southeast Asia, so the remote IDE feels fast. 4 GB is enough because agents "think" on the model provider's servers. Ignore the "new release 26.04 available" login message; stay on 24.04.

- [x] **B4. Install the key on the server** *(only if B3's key wasn't attached)*.

  > **If you see** a password prompt on first login, or `Changing password for root. Current password:`, the key wasn't attached. Hetzner emailed a temporary root password and forces a change on first login: enter the emailed password twice, then a new one. (No email? Server → **Rescue** → **Reset root password**.)
  >
  > **If you see** `failed to open ID file ... No such file or directory`, step B2 was skipped. Run it, then:

  ```bash
  ssh-copy-id -i ~/.ssh/id_ed25519_hetzner.pub root@<server-ip>
  ssh -i ~/.ssh/id_ed25519_hetzner root@<server-ip>   # should log in without the server password
  ```
  *What it does:* adds your public key to the server's allowed list. From now on the laptop logs in with the key.

---

## Part C — Lock the server down

- [x] **C1. Update the system** *(on the server, as root)*.
  ```bash
  apt update && apt upgrade -y
  ```
  *What it does:* installs security fixes. Takes 1–3 minutes. If a purple screen asks which services to restart, press Enter. "0 upgraded" just means it was already current.

- [x] **C2. Create your own user with admin rights** *(on the server, as root)*.
  ```bash
  adduser <username>
  usermod -aG sudo <username>
  rsync --archive --chown=<username>:<username> ~/.ssh /home/<username>
  ```
  *What it does:* working as `root` is risky because it can do anything without confirmation. Your own user does admin tasks with `sudo`. `rsync` copies your SSH key to the new user.
  `adduser` asks for a password (save it; `sudo` needs it), then Full Name / Room / Phone: press Enter through them and answer `Y`. No output from the last two commands means success.

- [x] **C3. Install Tailscale on the server *and* the laptop, on the same account.**
  On the server, run **one line at a time**:
  ```bash
  curl -fsSL https://tailscale.com/install.sh | sh
  ```
  ```bash
  tailscale up --hostname=lab
  ```
  Open the printed link and approve the server. On the laptop, install the Tailscale app (tailscale.com/download or the Mac App Store) and log in with **the same account**.
  *What it does:* creates a private network (a "tailnet") of your own devices. The server joins it under the name `lab`, reachable only from your devices.

  > **If you see** `shtailscale: command not found`, two pasted lines merged into one. Run them separately.
  >
  > **If you see** `Could not resolve hostname lab` on the laptop, the laptop isn't in the same tailnet. Check the machines list at login.tailscale.com/admin/machines: you need both the laptop and `lab`.
  >
  > **If the laptop app hangs at "Authentication in progress"**, turn off any other VPN. macOS runs only one VPN at a time. Also check System Settings → General → Login Items & Extensions → Network Extensions → Tailscale is on.
  >
  > **If the laptop app shows an old account**, it belongs to a different tailnet. Use **Add Account…** (not "Alternate Server") and log in with the account the server used.

- [x] **C4. Test the private route** *(on the laptop, new tab; keep the server tab open)*.
  ```bash
  ssh -i ~/.ssh/id_ed25519_hetzner <username>@lab
  ```
  ✅ You land at `<username>@<server-name>:~$`. Don't continue until this works, or the next steps can lock you out.
  Save the key passphrase so you aren't asked each time *(on the laptop)*:
  ```bash
  ssh-add --apple-use-keychain ~/.ssh/id_ed25519_hetzner
  ```

- [x] **C5. Turn off password logins and direct root login** *(on the server)*.
  ```bash
  sudo tee /etc/ssh/sshd_config.d/00-hardening.conf <<'EOF'
  PasswordAuthentication no
  PermitRootLogin no
  EOF
  sudo systemctl restart ssh
  sudo sshd -T | grep -Ei 'passwordauthentication|permitrootlogin'
  ```
  ✅ Expected output: `permitrootlogin no` and `passwordauthentication no`.
  *What it does:* bots constantly guess passwords on public servers. After this, only your private key gets in, and never directly as root.

  > **Why `00-` and not `99-`:** cloud images ship `/etc/ssh/sshd_config.d/50-cloud-init.conf` with `PasswordAuthentication yes`. SSH reads these files alphabetically and **the first value wins**, so a `99-` file is silently ignored.
  >
  > **If you see** `50-cloud-init.conf: Permission denied` when running `sshd -T`, add `sudo`.
  >
  > **Check the file exists** with `ls /etc/ssh/sshd_config.d/`. You should see `00-hardening.conf` and `50-cloud-init.conf`. If yours is missing, the `tee` command didn't run; run it again.

  Verify from the laptop that passwords are refused:
  ```bash
  ssh -o PubkeyAuthentication=no <username>@lab
  ```
  ✅ Expected: `Permission denied (publickey)`. If it asks for a password, the rule isn't active.

- [x] **C6. Close the public door with a firewall** *(on the server)*.
  ```bash
  sudo ufw allow in on tailscale0
  sudo ufw default deny incoming
  sudo ufw default allow outgoing
  sudo ufw enable
  ```
  *What each line does:*
  - `allow in on tailscale0`: lets your Tailscale devices in. Added **first**, so enabling the firewall can't lock you out.
  - `default deny incoming`: drops every other incoming connection; the public IP looks dead to the internet.
  - `default allow outgoing`: the server can still reach GitHub, updates, model APIs, and GPU providers. Replies to its own requests come back normally.
  - `enable`: activates the rules and keeps them on after reboots. Answer `y` to the SSH warning; you're connected through Tailscale.

  ```bash
  sudo ufw status
  ```
  ✅ Expected: `Status: active` with `Anywhere on tailscale0  ALLOW` (plus a v6 line).

  Verify from the **laptop** (not the server, where the test is meaningless because the traffic never crosses the internet):
  ```bash
  ssh -i ~/.ssh/id_ed25519_hetzner <username>@lab                              # ✅ still logs in
  ssh -i ~/.ssh/id_ed25519_hetzner -o ConnectTimeout=10 <username>@<server-ip>  # ✅ Operation timed out
  ```

  > **Emergency access:** if Tailscale ever breaks, the provider's web console (Hetzner: server → **Console**) still opens a screen on the server, bypassing the firewall. Log in with your user's password.
  >
  > **What this does and doesn't protect against:** it stops internet scanners and password-guessing bots. It does not protect a compromised laptop, a stolen Tailscale/GitHub/Hetzner account, or a leaked API key. Keep 2FA on every account and secrets in `.env`.

- [x] **C7. Laptop shortcut** in `~/.ssh/config`:
  ```
  Host lab
    HostName lab
    User <username>
    IdentityFile ~/.ssh/id_ed25519_hetzner
  ```
  Append it in one go *(on the laptop)*:
  ```bash
  cat >> ~/.ssh/config <<'EOF'

  Host lab
    HostName lab
    User <username>
    IdentityFile ~/.ssh/id_ed25519_hetzner
  EOF
  ssh lab
  ```
  *What it does:* now plain `ssh lab` works.
  Why the name `lab`: name machines by role, not by project. One server will host several projects.

- [x] **C8. Reboot once** *(on the server)* if the login message says `*** System restart required ***`:
  ```bash
  sudo reboot
  ```
  Wait a minute, then `ssh lab`. ✅ The restart message is gone, and logging in still works, which proves Tailscale and the firewall come back on their own after a reboot.

---

## Part D — Dev tools on the server

All commands in this part run **on the server** (`ssh lab`) unless marked otherwise.

> **Paste one command at a time.** Some terminals drop line breaks when pasting several lines, which merges commands into one (`...install.sh | shtailscale up`, `git clone ...gitcd cloud-ai-lab`). If you see `command not found` or `unknown option` on a multi-line paste, that's why. Nothing breaks; rerun the commands separately.

- [x] **D1. Install core tools.**
  ```bash
  sudo apt install -y git tmux build-essential
  ```
  *What it does:* `git` for version control; `tmux` keeps programs running after you disconnect (the key to "close the laptop and it keeps working"); `build-essential` provides compilers some Python packages need.
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```
  *What it does:* installs `uv`, one tool for Python versions, virtual environments, and packages (replaces pip + venv + pyenv).
  ```bash
  source ~/.bashrc
  uv --version
  ```
  ✅ Expected: `uv 0.x.x`.

  > **If you see** `WARNING: terminal is not fully functional` (e.g. from `git log`), your laptop's terminal reports a type the server doesn't know. Fix once:
  > ```bash
  > echo 'export TERM=xterm-256color' >> ~/.bashrc
  > source ~/.bashrc
  > ```

- [x] **D2. Give the server its own GitHub key.**
  ```bash
  ssh-keygen -t ed25519 -C "lab-server" -f ~/.ssh/id_ed25519
  ```
  Press **Enter twice** at the passphrase prompts: agents will push unattended, so this key must work without one. Tailscale and the firewall are what protect it.

  > **If you typed a passphrase by mistake,** remove it without making a new key: `ssh-keygen -p -f ~/.ssh/id_ed25519` → old passphrase → Enter → Enter.

  ```bash
  cat ~/.ssh/id_ed25519.pub
  ```
  Copy the line into GitHub (project account) → **Settings → SSH and GPG keys → New SSH key**, title `lab-server`. GitHub may ask you to re-authenticate ("sudo mode"); use your passkey, password, or 2FA code.
  ```bash
  ssh -T git@github.com
  ```
  ✅ Expected: `Hi <github-username>! You've successfully authenticated...` with **no** passphrase prompt. Type `yes` at the first-time fingerprint question; GitHub's official ED25519 fingerprint is `SHA256:+DiY3wvvV6TuJJhbpZisF/zLDA0zPMSvHdkr4UvCOqU`.

  *What it does:* lets the server (and agents on it) pull and push code. The server only uses one account, so no alias is needed here.

  > **Trade-off:** an account-level key can reach every repo on the account. If that's too broad later, use per-repo **deploy keys** instead.

- [x] **D3. Set the commit identity and clone the repo.**
  ```bash
  git config --global user.name "<Your Name>"
  git config --global user.email "<email or noreply address>"
  ```
  *What it does:* stamps your name on commits made from the server. `--global` is fine because the server only uses the project account.
  ```bash
  mkdir -p ~/projects && cd ~/projects
  git clone git@github.com:<github-username>/cloud-ai-lab.git
  cd cloud-ai-lab
  git log --oneline -3
  ```
  *What it does:* `~/projects` holds every repo you'll work on. The server copy becomes the **real working copy**; the laptop copy is only a backup. Run `git pull` on the laptop copy before editing it.

- [x] **D4. Connect PyCharm** *(on the laptop)*.

  Remote development is a **PyCharm Pro** feature. Options: the 30-day Pro trial, the free **JetBrains student license** (jetbrains.com/student), or the **GitHub Student Developer Pack**, which includes it. Free alternative: VS Code + the Remote-SSH extension.

  1. PyCharm → **File → Remote Development → SSH → New Connection**: Username `<username>`, Host `lab`, Port `22`.
  2. Tick **Specify private key** → `~/.ssh/id_ed25519_hetzner` (in the file picker, **Cmd+Shift+.** shows hidden folders like `.ssh`). Pick the file **without** `.pub`.
  3. **Check Connection and Continue.** When asked for a passphrase, it's the **laptop key's passphrase**, not the server's sudo password.
  4. **IDE version:** pick the newest *stable* release (avoid "RC"/"EAP" if a stable one is listed).
  5. **Project directory:** `/home/<username>/projects/cloud-ai-lab` → **Download IDE and Connect**. The first run installs PyCharm's backend on the server (3–5 min).

  > **If you see** "The host doesn't meet the minimal requirements" (4 GB RAM / 4 cores), a 2 vCPU / 4 GB server still works for editing. Click **Continue Anyway** and add swap (D5). If it feels slow, resize the server (Hetzner → server → **Rescale**; takes a reboot).

- [x] **D5. Add swap.**
  ```bash
  sudo fallocate -l 4G /swapfile
  sudo chmod 600 /swapfile
  sudo mkswap /swapfile
  sudo swapon /swapfile
  echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
  free -h
  ```
  *What it does:* uses 4 GB of disk as emergency memory, so the server slows down instead of crashing when the IDE, agents, and jobs run together. The `fstab` line keeps it on after reboots. ✅ `free -h` shows `Swap: 4.0Gi`.
  Read the **available** column, not **free**: Linux fills spare memory with cache and hands it back when needed.

---

## Part E — Storage and final test

- [x] **E1. Cloudflare R2 storage + rclone.**

  **What R2 is:** object storage, a place for big files (datasets, audio, checkpoints, final models). It's "S3-compatible," so every tool that speaks Amazon S3 works with it (rclone, `boto3`, PyTorch/Hugging Face loaders), and it has **zero egress fees**: downloading your own data is free. That matters because training jobs pull the dataset to a GPU on every run. Why R2 over S3 or Backblaze B2: see [decisions.md](decisions.md).

  **E1a. Turn on R2** *(Cloudflare dashboard)*. Sign up at dash.cloudflare.com → **Storage & databases → R2 Object Storage** → **Add R2 subscription**. A card is required, but nothing is charged under the free tier (10 GB stored, 1M writes, 10M reads per month at the time of writing).

  > **2FA note:** if you signed up with Google, the Cloudflare account has no password and its 2FA page asks for one. Protect the **Google** account with 2-Step Verification instead; that's the real lock.

  **E1b. Create the bucket.** **Create bucket** → name `<bucket-name>` (permanent, lowercase) → location **Automatic** or **APAC** (closest to a Singapore server) → storage class **Standard**.
  *Why Standard:* it counts toward the free tier and has no per-read fees. "Infrequent Access" charges per read, which is bad for training data that gets read often.
  One bucket can hold every project; separate them by path (`project-a/datasets/...`, `project-b/checkpoints/...`).

  **E1c. Create an API token** (a login for programs, not people). R2 overview → **Manage API tokens** (if you can't find it, search "R2 API tokens" in the dashboard) → **Create Account API token**:

  | Setting | Value | Why |
  |---|---|---|
  | Name | `lab-server` | Know which machine uses it, and which to revoke if it leaks |
  | Permission | **Object Read & Write** | Can upload/download/delete files, but not create or delete buckets or change settings |
  | Buckets | Only `<bucket-name>` | A leaked key can't touch other buckets |
  | TTL | Forever | Convenient for a server; revoke manually if it leaks |
  | IP filtering | Empty | GPU workers (Modal, RunPod) have changing IPs and need access too |

  Account tokens (rather than User tokens) keep working regardless of who's in the account, which suits servers.

  Save the three values in a password manager. They're shown **once**. **Never commit them or paste them into chats.**

  | Value | Think of it as |
  |---|---|
  | Access Key ID | Username |
  | Secret Access Key | Password (the dangerous one) |
  | Endpoint (`https://<account-id>.r2.cloudflarestorage.com`) | Address |

  The separate "Token value" is for Cloudflare's own API; S3 tools don't use it.

  **E1d. Install a current rclone** *(on the server)*. rclone is `cp` for cloud storage.
  ```bash
  curl https://rclone.org/install.sh | sudo bash
  rclone version
  ```

  > **Don't use `apt install rclone`** on Ubuntu 24.04. It's an old (2022) version, and uploads to R2 failed with `NotImplemented: Not Implemented (status code: 501)` before succeeding on retry. If you already installed it: `sudo apt remove -y rclone`, then run the install script above. Your saved config is kept.

  **E1e. Configure the connection.**
  ```bash
  rclone config
  ```
  Type the **words**, not menu numbers (numbers change between versions):

  | Prompt | Answer |
  |---|---|
  | `e/n/d/r/c/s/q>` | `n` (new remote) |
  | `name>` | `r2` |
  | `Storage>` | `s3` |
  | `provider>` | `Cloudflare` |
  | `env_auth>` | Enter |
  | `access_key_id>` / `secret_access_key>` | paste from the password manager |
  | `region>` | Enter (auto) |
  | `endpoint>` | paste the endpoint |
  | other prompts | Enter |
  | `Edit advanced config?` | `n` |
  | `Keep this "r2" remote?` | `y`, then `q` |

  A **remote** is rclone's name for a saved storage connection; `r2:` now means "my R2 account." The summary screen shows the secret in plain text, so don't screenshot or paste it.
  ```bash
  rclone config update r2 no_check_bucket true
  chmod 600 ~/.config/rclone/rclone.conf
  ```
  *What these do:* rclone normally tries to create the bucket before uploading; the token is deliberately limited to files, so that attempt would be refused. `no_check_bucket` skips it. `chmod 600` makes the config (which now holds the secret) readable only by your user.

  **E1f. Test: text file.**
  ```bash
  echo "hello from lab" > test.txt
  rclone copy test.txt r2:<bucket-name>/test/ -v
  rclone ls r2:<bucket-name>
  ```
  ✅ Expected: `Copied (new)`, then `15 test/test.txt` in the listing.
  Running the same `copy` again transfers `0 B`: rclone only uploads files that are new or changed. Useful later when re-syncing a dataset.

  **E1g. Test: image round trip** *(laptop → server → R2, checked byte for byte)*. A binary file proves real files arrive intact, not just text.
  ```bash
  # on the laptop (tip: type "scp ", drag the file into the terminal, then add " lab:~/")
  scp ~/Downloads/<image>.jpg lab:~/
  ```
  ```bash
  # on the server
  rclone copy ~/<image>.jpg r2:<bucket-name>/test/ -v
  rclone check ~/<image>.jpg r2:<bucket-name>/test/ --one-way
  ```
  ✅ Expected: `Copied (new)`, then `0 differences found`. You can also open the bucket in the Cloudflare dashboard and preview the image. Filenames are case-sensitive.

  **E1h. Clean up** (this also proves the token can delete):
  ```bash
  rclone delete r2:<bucket-name>/test/
  rm ~/test.txt ~/<image>.jpg
  ```

  **How the server and R2 relate:** they're independent. Deleting a file in one doesn't touch the other, which makes R2 a natural backup. You won't mirror every action by hand:

  | Where | What lives there | How it gets there |
  |---|---|---|
  | GitHub | Code, docs, configs | `git push` |
  | Server disk | Working copy, temporary files | You edit them |
  | R2 | Datasets, checkpoints, final models, results | rclone occasionally; training code automatically (Stage 2) |

  > **Use `rclone copy`, not `rclone sync`,** unless you're sure. `sync` makes the destination an exact mirror of the source, which **deletes** files in the destination that aren't in the source.

- [ ] **E2. The "close the laptop" test.**
  ```bash
  tmux new -s test
  python3 -c "import time; [print(i, flush=True) or time.sleep(60) for i in range(600)]"
  # detach: Ctrl+B then D. Close the laptop. Later:
  ssh lab
  tmux attach -t test
  ```

## Verify it worked
- `ssh lab` from the laptop logs in with no password prompt.
- `ssh -o PubkeyAuthentication=no <username>@lab` is refused.
- `sudo ufw status` shows `Status: active` with only `tailscale0` allowed.
- After E2, the counter kept going while the laptop was closed.

---

## Rules to keep
- Secrets live only in `.env` on the server (and a password manager). Never in git, never in chats.
- If a key leaks: revoke it and make a new one. Don't try to scrub history.
- Run `git status` before every commit.
