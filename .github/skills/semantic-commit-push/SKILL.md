---
name: semantic-commit-push
description: 'Group current Git changes into meaningful semantic commits and push the current branch. Use when committing a working tree, splitting feature/fix/refactor/test/docs/chore changes, auditing sensitive files, preparing a commit plan, or safely pushing changes.'
argument-hint: 'Optional context for commit messages'
user-invocable: true
---

# Semantic Commit and Push

## Outcome

Create focused, semantic commits from the current working tree and push the current branch without losing existing changes or exposing sensitive files.

## Procedure

1. Inspect the full repository state:
   - `git status --short`
   - `git diff --stat`
   - `git diff`
   - `git log --oneline -10`
2. Audit the change set before staging:
   - Include modified, added, and deleted files in the review.
   - Check for sensitive or suspicious files such as `.env`, tokens, credentials, private keys, certificates, and secret configuration.
   - If a sensitive file appears in the change set, stop and ask the user before committing.
   - Do not revert changes that already existed in the worktree.
3. Group files by intent: feature, fix, refactor, tests, docs, chore, release, or configuration.
   - Keep independent changes in separate commits.
   - Use supplied context only when it accurately describes the changes.
   - Write the commit description in Spanish, keeping the semantic type prefix (`feat`, `fix`, `refactor`, `test`, `docs`, `chore`, or `release`) in its conventional form.
   - Match the repository's recent commit-message style.
4. Present a proposed commit plan listing each semantic commit and its files.
   - If the grouping is clear, continue.
   - If files have genuinely ambiguous ownership or intent, ask the user before staging.
5. For each approved group, stage only its files:
   - `git add <files>`
   - `git commit -m "<semantic message>"`
   - Never use `--no-verify`.
   - Never amend commits.
6. After all commits are created, verify the result with `git status --short` and push using:
   - `git push`
   - Never force-push.
7. Summarize the commits created, the files covered, and whether the branch was pushed successfully.

## Completion Checks

- Every intended changed file is either included in exactly one planned commit or intentionally left uncommitted with an explanation.
- No sensitive or suspicious file was committed.
- Each commit has one coherent purpose and follows the local commit style.
- Hooks and normal Git verification completed successfully.
- The push completed without force or amend operations.
