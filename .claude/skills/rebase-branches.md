# Rebase All Challenge Branches

Rebases all challenge branches on the latest main branch to propagate changes.

## Usage

```
/rebase-branches
```

## Instructions

When this command is invoked:

1. Check that the repository is in a clean state (no uncommitted changes)
2. Execute the rebase script: `.claude/scripts/rebase-all-branches.sh`
3. Report the results to the user:
   - List successfully rebased branches
   - List any branches that had conflicts
   - Provide instructions for manually resolving conflicts if needed
   - Suggest push commands with `--force-with-lease` if rebases succeeded

## Context

This repository uses a branch-based structure where:
- The `main` branch contains only documentation in `.claude/`
- Each challenge branch contains a complete debugging challenge
- When `.claude/README.md` is updated, all challenge branches should be rebased to include those changes

The rebase script automates this process, handling conflicts gracefully and providing clear feedback.
