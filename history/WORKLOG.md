# Worklog

What Claude did for each task. Append-only, newest at the bottom.

## 2026-11-04 — Bootstrap Claude Code, Git and project history

**Prompt:** Initialize Claude (skills + configuration) and Git; create a history folder storing every prompt, the work done, and every commit.

**Done:**
- `git init -b main`; local config `core.hooksPath=.githooks`, `core.autocrlf=false`.
- `.gitignore` (Python, tooling caches, secrets, personal Claude files) and `.gitattributes` (LF line endings).
- `CLAUDE.md` — stack conventions (Python 3.12+, uv, ruff, mypy, pytest, src layout), commit rules, history rules.
- `.claude/settings.json` — permission allowlist for safe git/test/lint commands, deny reading `.env`, `UserPromptSubmit` hook.
- `.claude/hooks/log-prompt.js` — appends each prompt to `history/PROMPTS.md`.
- `.claude/skills/worklog/SKILL.md` — format and rules for worklog entries.
- `.githooks/post-commit` — appends each commit to `history/COMMITS.md`.
- `history/` — `README.md`, `PROMPTS.md` (prompt #1 added manually), `WORKLOG.md`, `COMMITS.md`.

**Decisions:**
- Prompt hook written in Node.js, not Python — Python is not installed on this machine (only the Microsoft Store stub); Node is.
- Commit log via git hook rather than Claude instructions, so manual commits are logged too. Trade-off: each entry lands in the following commit.
- No `pyproject.toml` yet — waiting for the actual technical task to define package name and dependencies.

**Verification:** Prompt hook tested with a sample payload (quotes, unicode) in a scratch dir — entry written correctly, exit 0. Post-commit hook verified by this commit.

**Open items:**
- Install Python 3.12+ and `uv` before implementation work starts.
- Prompt hook activates from the next prompt (Claude Code may need a session restart to load project hooks).

**Commit:** this commit
