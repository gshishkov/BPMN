---
name: worklog
description: Append an entry to history/WORKLOG.md describing the work just done. Use at the end of every task that changed files, ran meaningful commands, or made design decisions, and before committing.
---

# Worklog entry

Append (never rewrite) one entry to the bottom of `history/WORKLOG.md`:

```markdown
## YYYY-MM-DD — <short title of the task>

**Prompt:** <one-line paraphrase of what the user asked>

**Done:**
- <concrete change, with file paths>
- ...

**Decisions:**
- <decision> — <why> (omit section if none)

**Verification:** <tests/linters run and their result, or "not verified" and why>

**Open items:** <follow-ups, known gaps> (omit section if none)

**Commit:** <short hash + subject, or "not committed">
```

Rules:
- Be factual and concise; record what was actually done, including failures.
- Use real dates (today's date), not relative ones.
- If the task ends with a commit, write the entry *before* committing and stage it
  together with the rest of `history/`, so the entry and the code land in the same commit.
  Fill **Commit** as "this commit" in that case.
