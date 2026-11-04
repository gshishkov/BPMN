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
