# Stage 1 — Server, access, and dev tools

**What you'll have working by the end:** an always-on cloud server that only your own devices can reach, where code, agents, and long jobs keep running after you close your laptop.

**Status:** Parts A–B done · Part C in progress (C1–C4 done, C5 being fixed) · Parts D–E not started.

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

- [ ] **C5. Turn off password logins and direct root login** *(on the server)*.
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

  Verify from the laptop that passwords are refused:
  ```bash
  ssh -o PubkeyAuthentication=no <username>@lab
  ```
  ✅ Expected: `Permission denied (publickey)`. If it asks for a password, the rule isn't active.

- [ ] **C6. Close the public door with a firewall** *(on the server)*.
  ```bash
  sudo ufw allow in on tailscale0
  sudo ufw default deny incoming
  sudo ufw default allow outgoing
  sudo ufw enable
  ```
  *What it does:* drops all incoming internet traffic. Your devices still get in through Tailscale (`tailscale0`); outgoing traffic (downloads, APIs, GitHub) still works. Re-test C4 in a new tab before closing your current session.

- [ ] **C7. Laptop shortcut** in `~/.ssh/config`:
  ```
  Host lab
    HostName lab
    User <username>
    IdentityFile ~/.ssh/id_ed25519_hetzner
  ```
  *What it does:* now plain `ssh lab` works.

- [ ] **C8. Reboot once** *(on the server)* if the login message says `*** System restart required ***`:
  ```bash
  sudo reboot
  ```
  Wait a minute, then `ssh lab`.

---

## Part D — Dev tools on the server

- [ ] **D1. Install core tools.**
  ```bash
  sudo apt install -y git tmux build-essential
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```
  *What it does:* `git` for version control; `tmux` keeps programs running after you disconnect; `build-essential` lets Python packages compile; `uv` manages Python versions and packages.

- [ ] **D2. Give the server its own GitHub key.**
  ```bash
  ssh-keygen -t ed25519 -C "lab-server" -f ~/.ssh/id_ed25519
  cat ~/.ssh/id_ed25519.pub   # add to GitHub → Settings → SSH and GPG keys
  ssh -T git@github.com       # should greet your project account
  ```
  *What it does:* lets the server (and agents on it) pull and push code. The server knows only one account, so no alias is needed.

- [ ] **D3. Clone the repo on the server.**
  ```bash
  git clone git@github.com:<github-username>/cloud-ai-lab.git
  ```
  *What it does:* the server copy becomes the real working copy.

- [ ] **D4. Connect the IDE** (PyCharm: JetBrains Gateway → SSH → host `lab`; or VS Code Remote-SSH).
  *What it does:* you edit files that live on the server through your laptop's IDE. PyCharm remote development may need a paid or student license.

---

## Part E — Storage and final test

- [ ] **E1. Cloudflare R2 bucket + rclone.**
  ```bash
  sudo apt install -y rclone
  rclone config        # type: s3 → provider: Cloudflare → paste R2 keys
  rclone copy test.txt r2:<bucket-name>/
  ```
  *What it does:* R2 holds big files (datasets, checkpoints) cheaply with no download fees.

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
