# BPMN — Project Guide for Claude

`bpmn_paths`: parses a BPMN 2.0 file into a graph, validates it, and prints every
start-to-end simple path with the conditions of the traversed sequence flows.
Run: `uv run python -m bpmn_paths src/data/invoice.bpmn`.

## Hard rules

- **Never claim tests pass unless they were actually run and passed in this session.**
  Report failures verbatim. Never fabricate output.
- **Never modify `src/data/*.bpmn`.** They are the task inputs (`invoice-broken.bpmn` is broken on purpose).
- Standard library only at runtime (`xml.etree.ElementTree`). No new dependencies or
  abstractions unless the user asks.
- uv is installed by winget at a path that may not be on `PATH` in Claude's shell yet:
  `export PATH="$LOCALAPPDATA/Microsoft/WinGet/Packages/astral-sh.uv_Microsoft.Winget.Source_8wekyb3d8bbwe:$PATH"`.

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
