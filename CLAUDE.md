# BPMN — Project Guide for Claude

Python project for a technical task (details to be added once the task is defined).

## Stack & conventions

- **Python** 3.12+, managed with **uv** (`uv sync`, `uv run ...`). Dependencies live in `pyproject.toml`.
- **Layout:** `src/<package>/` for code, `tests/` for tests (src layout).
- **Quality gates** (run before every commit):
  - `uv run ruff format .` and `uv run ruff check .`
  - `uv run mypy src` (strict typing; type-hint all public functions)
  - `uv run pytest`
- Prefer small, pure functions; dataclasses / pydantic models for structured data; no global state.
- Write tests alongside every feature (pytest, plain `assert`, fixtures over setup classes).
- Never commit secrets; config via environment variables (`.env` is git-ignored, provide `.env.example`).

## Git

- Branch `main`. Conventional Commits: `feat:`, `fix:`, `refactor:`, `test:`, `docs:`, `chore:`.
- One logical change per commit. Commit only when the user asks.
- Git hooks live in `.githooks/` (enabled with `git config core.hooksPath .githooks`).

## Project history (mandatory)

The `history/` folder documents how this project is built. See `history/README.md`.

- `history/PROMPTS.md` — every user prompt, appended **automatically** by the
  `UserPromptSubmit` hook (`.claude/hooks/log-prompt.js`). Do not edit past entries.
- `history/COMMITS.md` — every commit, appended **automatically** by `.githooks/post-commit`.
  The new entry is included in the following commit; always stage `history/` when committing.
- `history/WORKLOG.md` — **you (Claude) must append an entry at the end of every task**
  that changed files or made decisions. Use the `worklog` skill for the format.
  Newest entries at the bottom. Never rewrite earlier entries.
