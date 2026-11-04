# Project history

A complete, append-only record of how this project was built.

| File | What it holds | Written by |
|---|---|---|
| [PROMPTS.md](PROMPTS.md) | Every prompt the user sent to Claude, verbatim, with timestamp and session id | `UserPromptSubmit` hook — `.claude/hooks/log-prompt.js` (automatic) |
| [WORKLOG.md](WORKLOG.md) | What Claude did for each task: changes, decisions, verification, open items | Claude, via the `worklog` skill (required by `CLAUDE.md`) |
| [COMMITS.md](COMMITS.md) | Every git commit: hash, date, author, message, changed files | `.githooks/post-commit` (automatic) |

## Notes

- The commit hook cannot include its own entry in the commit it describes, so each
  `COMMITS.md` entry is committed together with the *next* commit.
- On a fresh clone, enable the git hooks once:

  ```bash
  git config core.hooksPath .githooks
  ```

- The prompt hook requires **Node.js** on `PATH`.
