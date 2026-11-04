# Commits

Every git commit, appended automatically by `.githooks/post-commit`.

## 2480ab8 — chore: bootstrap Claude Code config, git and project history

- **Date:** 2026-11-04 09:46:29 +0200
- **Author:** Geno Shishkov <gshishkov@users.noreply.github.com>
- **Hash:** 2480ab8701f6d7396ddad74e9c84974a8612123b

```text
chore: bootstrap Claude Code config, git and project history

- CLAUDE.md with Python conventions and history rules
- .claude/settings.json: permissions + UserPromptSubmit prompt-logging hook
- .claude/skills/worklog: worklog entry skill
- .githooks/post-commit: logs every commit to history/COMMITS.md
- history/: prompts, worklog, commits

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>

 .claude/hooks/log-prompt.js     | 25 +++++++++++++++++++++++++
 .claude/settings.json           | 38 ++++++++++++++++++++++++++++++++++++++
 .claude/skills/worklog/SKILL.md | 34 ++++++++++++++++++++++++++++++++++
 .gitattributes                  |  5 +++++
 .githooks/post-commit           | 17 +++++++++++++++++
 .gitignore                      | 38 ++++++++++++++++++++++++++++++++++++++
 CLAUDE.md                       | 33 +++++++++++++++++++++++++++++++++
 history/COMMITS.md              |  3 +++
 history/PROMPTS.md              |  9 +++++++++
 history/README.md               | 21 +++++++++++++++++++++
 history/WORKLOG.md              | 30 ++++++++++++++++++++++++++++++
 11 files changed, 253 insertions(+)
```

## 9bdc856 — feat: BPMN parser, validator and simple-path enumeration CLI

- **Date:** 2026-11-04 10:39:32 +0200
- **Author:** Geno Shishkov <gshishkov@users.noreply.github.com>
- **Hash:** 9bdc856e72e4a7ab8b0f4ddb5c3e25c9b3070675

```text
feat: BPMN parser, validator and simple-path enumeration CLI

- Parse BPMN 2.0 with xml.etree.ElementTree into nodes and sequence flows,
  keeping conditionExpression text verbatim
- Validate references, incoming/outgoing consistency, connectivity, diverging
  gateways and reachability; every issue names the faulty element ID
- Enumerate simple start-to-end paths with an iterative DFS; loop flows are
  reported, not re-traversed (2 paths in invoice.bpmn)
- CLI: python -m bpmn_paths FILE (exit 1 on invalid file)
- 29 pytest tests, including both defects in invoice-broken.bpmn
- Add task input files src/data/*.bpmn (unchanged), README, FINAL_RESULT.md

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>

 .claude/settings.json        |   4 +-
 .gitattributes               |   1 +
 CLAUDE.md                    |  14 +-
 FINAL_RESULT.md              | 115 ++++++++++++++
 README.md                    |  41 +++++
 history/COMMITS.md           |  31 ++++
 history/PROMPTS.md           |  84 ++++++++++
 history/WORKLOG.md           |  39 +++++
 pyproject.toml               |  34 ++++
 src/bpmn_paths/__init__.py   |  31 ++++
 src/bpmn_paths/__main__.py   |   5 +
 src/bpmn_paths/cli.py        |  64 ++++++++
 src/bpmn_paths/model.py      | 105 +++++++++++++
 src/bpmn_paths/parser.py     | 116 ++++++++++++++
 src/bpmn_paths/paths.py      |  55 +++++++
 src/bpmn_paths/validation.py | 134 ++++++++++++++++
 src/data/invoice-broken.bpmn | 254 ++++++++++++++++++++++++++++++
 src/data/invoice.bpmn        | 259 +++++++++++++++++++++++++++++++
 tests/conftest.py            |  36 +++++
 tests/test_cli.py            |  34 ++++
 tests/test_parser.py         | 111 +++++++++++++
 tests/test_paths.py          | 115 ++++++++++++++
 tests/test_validation.py     | 122 +++++++++++++++
 uv.lock                      | 360 +++++++++++++++++++++++++++++++++++++++++++
 24 files changed, 2162 insertions(+), 2 deletions(-)
```
