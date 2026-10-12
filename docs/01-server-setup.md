# Stage 1 — Server Setup Checklist

Goal: an always-on cloud server you reach privately from any device, where code, agents, and long jobs keep running when your laptop is closed.

Replace placeholders: `<server-ip>`, `<username>`, `<github-username>`.

---

## Part A — GitHub account

- [x] **A1. Create a dedicated GitHub account and turn on 2FA.**
  *What it does:* gives the project a clean, professional home. 2FA means a stolen password alone can't take over your code.

- [x] **A2. Create the repository** (`cloud-ai-lab`, Python `.gitignore`, MIT license).
  *What it does:* the repo is where all code and docs live. The Python `.gitignore` already excludes `.env`, so secret files are never committed. MIT lets anyone reuse the project.

- [ ] **A3. Turn on secret scanning + push protection** (repo Settings → Code security).
  *What it does:* GitHub blocks any push that contains something that looks like an API key, a safety net for a public repo.

- [x] **A4. Give the laptop its own SSH key for this account** (only needed if the laptop already uses another GitHub account).
  ```bash
  ssh-keygen -t ed25519 -C "<email>" -f ~/.ssh/id_ed25519_lab
  pbcopy < ~/.ssh/id_ed25519_lab.pub        # paste into GitHub → Settings → SSH keys
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
  *What it does:* an SSH key is a password-less login for git. GitHub won't let one key belong to two accounts, so the `github-lab` alias tells git: "for this address, use the new key." Old projects keep using `github.com` and the old account.

- [x] **A5. Point the repo at the new account and set your identity.**
  ```bash
  git config user.name "<Your Name>"
  git config user.email "<email or noreply address>"
  git remote set-url origin git@github-lab:<github-username>/cloud-ai-lab.git
  ```
  *What it does:* `user.name/email` is the author name stamped on every commit (this repo only). The remote URL decides which key, and therefore which account, is used to push.

---

## Part B — Rent the server

- [x] **B1. Create a Hetzner account** (verification may require prepaid credit).
  *What it does:* Hetzner rents you the computer. Prepaid credit is a fraud check; it pays your first bills, it isn't a fee.

- [x] **B2. Make an SSH key for logging into the server** (on the laptop).
  ```bash
  ssh-keygen -t ed25519 -C "mac-to-server" -f ~/.ssh/id_ed25519_hetzner
  ```
  *What it does:* creates a key pair. The `.pub` half goes on the server like a lock; the private half stays on your laptop like the key. Never share the file without `.pub`.

- [x] **B3. Create the server:** Singapore · Ubuntu 24.04 · CPX22 (2 vCPU / 4 GB) · add the SSH key.
  *What it does:* Singapore is closest to Southeast Asia, so the remote IDE feels fast. Ubuntu 24.04 is the version most tools are tested on. 4 GB is enough because agents "think" on Anthropic's servers, not here.

- [x] **B4. Install the key on the server** (only if it wasn't attached at creation).
  ```bash
  ssh-copy-id -i ~/.ssh/id_ed25519_hetzner.pub root@<server-ip>
  ```
  *What it does:* copies your public key into the server's list of allowed keys, so you can log in without a password from now on.

---

## Part C — Lock the server down

- [ ] **C1. Log in with the key and update the system.**
  ```bash
  ssh -i ~/.ssh/id_ed25519_hetzner root@<server-ip>
  apt update && apt upgrade -y
  ```
  *What it does:* `apt update` fetches the latest list of software; `apt upgrade` installs security fixes. Always do this first on a new server.

- [ ] **C2. Create your own user with admin rights.**
  ```bash
  adduser <username>
  usermod -aG sudo <username>
  rsync --archive --chown=<username>:<username> ~/.ssh /home/<username>
  ```
  *What it does:* `root` can do anything with no confirmation, so working as root is risky. Your own user can still do admin tasks with `sudo` (asking for your password). The `rsync` line copies your SSH key to the new user so you can log in as them.

- [ ] **C3. Install Tailscale and join your private network.**
  ```bash
  curl -fsSL https://tailscale.com/install.sh | sh
  tailscale up --hostname=lab
  ```
  *What it does:* Tailscale creates a private network between your devices (laptop, phone, server). The server becomes reachable as `lab`, but only from your own devices, not the whole internet.

- [ ] **C4. Test logging in through Tailscale** (from the laptop, new terminal tab).
  ```bash
  ssh -i ~/.ssh/id_ed25519_hetzner <username>@lab
  ```
  *What it does:* proves the private route works **before** closing the public one. Do not continue until this succeeds, or you can lock yourself out.

- [ ] **C5. Turn off password logins and direct root login.**
  ```bash
  sudo tee /etc/ssh/sshd_config.d/99-hardening.conf <<'EOF'
  PasswordAuthentication no
  PermitRootLogin no
  EOF
  sudo systemctl restart ssh
  ```
  *What it does:* bots constantly try to guess passwords on every public server. After this, only someone holding your private key can log in, and never directly as root.

- [ ] **C6. Close public SSH with a firewall** (allow only Tailscale).
  ```bash
  sudo ufw allow in on tailscale0
  sudo ufw default deny incoming
  sudo ufw default allow outgoing
  sudo ufw enable
  ```
  *What it does:* the firewall drops all incoming traffic from the internet. Your devices still get in through Tailscale (`tailscale0`). Outgoing traffic (downloads, APIs, GitHub) still works.
  Re-test C4 in a new tab before closing your current session.

- [ ] **C7. Add a laptop shortcut** in `~/.ssh/config`:
  ```
  Host lab
    HostName lab
    User <username>
    IdentityFile ~/.ssh/id_ed25519_hetzner
  ```
  *What it does:* now `ssh lab` is enough; no flags to remember.

---

## Part D — Dev tools on the server

- [ ] **D1. Install core tools.**
  ```bash
  sudo apt install -y git tmux build-essential
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```
  *What it does:* `git` for version control; `tmux` keeps programs running after you disconnect; `build-essential` lets Python packages compile; `uv` is a fast Python package/environment manager.

- [ ] **D2. Give the server its own GitHub key.**
  ```bash
  ssh-keygen -t ed25519 -C "lab-server" -f ~/.ssh/id_ed25519
  cat ~/.ssh/id_ed25519.pub       # add to GitHub → Settings → SSH keys
  ssh -T git@github.com           # should greet your new username
  ```
  *What it does:* lets the server (and agents running on it) pull and push code. The server only knows the new account, so no alias is needed here.

- [ ] **D3. Clone the repo on the server.**
  ```bash
  git clone git@github.com:<github-username>/cloud-ai-lab.git
  ```
  *What it does:* the server copy becomes the real working copy; the laptop copy is now just a convenience.

- [ ] **D4. Connect the IDE** (PyCharm: JetBrains Gateway → SSH → host `lab`; or VS Code Remote-SSH).
  *What it does:* you edit files that live on the server, with the IDE's interface on your laptop. Nothing heavy runs locally.
  Note: PyCharm remote development may require a paid or student license.

---

## Part E — Storage and final test

- [ ] **E1. Cloudflare R2 bucket + rclone.**
  ```bash
  sudo apt install -y rclone
  rclone config        # type: s3 → provider: Cloudflare → paste R2 keys
  rclone copy test.txt r2:<bucket-name>/
  ```
  *What it does:* R2 holds big files (datasets, checkpoints, model weights) cheaply, with no download fees. `rclone` moves files between the server and R2.

- [ ] **E2. The "close the laptop" test.**
  ```bash
  tmux new -s test
  python3 -c "import time; [print(i, flush=True) or time.sleep(60) for i in range(600)]"
  # detach: Ctrl+B then D. Close the laptop. Later:
  ssh lab
  tmux attach -t test
  ```
  *What it does:* proves the core promise. The counter keeps going while your laptop is off. If the numbers continued, Stage 1 is done.

---

## Rules to keep

- Secrets live only in `.env` on the server (and a password manager). Never in git, never in chats.
- If a key leaks: revoke it and make a new one. Don't try to scrub history.
- Run `git status` before every commit.
