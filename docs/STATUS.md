# Status

Live progress for agent work. The agent updates this after every step and pushes it (see "Working unattended" in [`CLAUDE.md`](../CLAUDE.md)). Task definitions live in [`ROADMAP.md`](ROADMAP.md).

## Summary

*(Written when all given tasks are done or blocked: what finished, what's blocked, and what the human must do, in order.)*

---

<!-- Template for each task:

## <id> — <title>
- **Branch:** `task/<id>-<short-name>`
- **State:** in progress / done / blocked
- **Done:** <what's finished>
- **Next:** <the next step>
- **Human must:** <exact commands, keys, approvals, or costs; "nothing" if none>

-->

## 0.2 — Document Stage 0
- **Branch:** `task/0.2-document-stage-0`
- **State:** done, committed and pushed; waiting for the human's review and merge
- **Done:** `docs/00-agent-setup.md` written (install, PATH fix, tmux, subscription login, wrapped-URL `Unknown scope: user:mcp_` failure, focus-events fix, verify). README Stage 0 row added; 0.1 and 0.2 ticked in ROADMAP.
- **Next:** nothing.
- **Human must:** review and merge.

## 0.3 — Unattended agent rules
- **Branch:** `task/0.3-unattended-rules`
- **State:** done, waiting for the human's review and merge
- **Done:** hard rule 2 replaced (commit and push freely to own branch); "Working unattended" section added to `CLAUDE.md`; this file created; `.claude/settings.json` with `permissions.deny` rules.
- **Next:** nothing.
- **Human must:** review and merge. The new rule 2 takes effect once it's on `main`.

<details><summary>Steps and output from this build</summary>

**1. Check the settings format** in the current docs (code.claude.com/docs/en/settings and /permissions, read 2026-10-13):
- the `"$schema"` URL is `https://json.schemastore.org/claude-code-settings.json`;
- `Bash(x:*)` is still supported and means the same as `Bash(x *)`;
- `Read(./.env)` matches `.env` in the current directory; `Read(**/.env)` matches any `.env` at or under it;
- Read deny rules also cover `cat`, `head`, `tail`, `sed` on that file in Bash, but not scripts (Python, Node) that open it themselves.

**Result:** ✅ the rule list as given is valid syntax.

**2. Write `.claude/settings.json` and validate the JSON**
```console
$ python3 -m json.tool .claude/settings.json >/dev/null && echo "JSON valid"
JSON valid
```
**Result:** ✅

**3. Test that deny rules block commands** (harmless commands chosen so nothing happens even if not blocked):
```console
$ git merge --abort
Permission to use Bash with command git merge --abort has been denied.

$ rm -rf ./does-not-exist-deny-test
Permission to use Bash with command rm -rf ./does-not-exist-deny-test has been denied.
```
**Result:** ✅ both blocked by Claude Code 2.1.296, in the same session that created the file.

**Limits (from the docs):** deny rules match the command as written. They are not a security wall: a bare `git push` while on `main`, `git push origin HEAD:main`, `rm -fr`, `/usr/bin/sudo`, `bash -c "..."`, or a Python script reading `.env` aren't matched. They catch the usual form; the rules in `CLAUDE.md` and branch protection on GitHub cover the rest.
</details>

## 2.2 — Hello-GPU job
- **Branch:** `task/2.2-hello-gpu`
- **State:** blocked: code written and checked locally; can't run until 2.1 is done
- **Done:** `uv` project (`pyproject.toml`, `uv.lock`, Python 3.12, `modal` 1.6.1). `jobs/hello_gpu.py`: a T4 function that prints `nvidia-smi`, times a 4096×4096 PyTorch matmul, and returns GPU name, torch/CUDA versions, ms and TFLOPS. 5-minute hard timeout. Cost estimate in the file's docstring.
- **Next:** the human runs it (below).
- **Human must:**
  1. Finish **2.1**: sign up for Modal, **set a monthly spending limit**, then on the server:
     ```bash
     uv tool install modal    # the `modal` command; not installed yet
     modal token new          # opens a login link; writes ~/.modal.toml
     ```
  2. Run the job: `modal run jobs/hello_gpu.py`
     **Estimated cost:** T4 at $0.000164/s (modal.com/pricing, 2026-10-13). ~1–2 min of GPU time plus a few minutes of CPU for the first image build: **under $0.05**, inside the Starter plan's $30/month free credit.
  3. Check: output shows `gpu: Tesla T4` and the command returns to the prompt by itself.

<details><summary>Steps and output from this build</summary>

**1. Check whether 2.1 is done**
```console
$ which modal; test -f ~/.modal.toml && echo "modal.toml exists" || echo "no modal.toml"
bash: line 1: modal: command not found
no modal.toml
```
**Result:** ❌ 2.1 not done: no `modal` command and no token. The code can still be written; running it waits for the human.

**2. Create the project and add the Modal client library**
```console
$ uv init --bare --python 3.12 --name cloud-ai-lab
Initialized project `cloud-ai-lab`
$ uv add modal
...
$ uv run python -c "import modal; print(modal.__version__)"
1.6.1
$ uv python pin 3.12
Pinned `.python-version` to `3.12`
```
**Result:** ✅ The library only; it needs no account.

**3. Pick the GPU and estimate the cost** (modal.com/pricing, read 2026-10-13)

| GPU | $/s | $/h |
|---|---|---|
| T4 | 0.000164 | 0.59 |
| L4 | 0.000222 | 0.80 |
| A10 | 0.000306 | 1.10 |

**Result:** ✅ T4 is the cheapest. Pinned `torch==2.14.1` (released 2026-09-30).

**4. Check the job loads** (no network, no Modal account needed)
```console
$ uv run python -m py_compile jobs/hello_gpu.py
$ uv run python -c "import runpy; m = runpy.run_path('jobs/hello_gpu.py'); app = m['app']; print('app:', app.name, '| functions:', list(app.registered_functions)); print('entrypoints:', list(app.registered_entrypoints))"
app: hello-gpu | functions: ['hello']
entrypoints: ['main']
```
**Result:** ✅ (Modal warns that `registered_functions` is deprecated in 1.7; only the check uses it, not the job.)

**5. Run on a GPU:** not done. Needs 2.1 and the human (`modal run` costs money).
</details>
