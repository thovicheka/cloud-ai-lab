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
