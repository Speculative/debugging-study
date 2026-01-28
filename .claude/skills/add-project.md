# Add Project Branch

Creates a new project branch from an external GitHub repository.

## Usage

```
/add-project
```

## Instructions

When this command is invoked:

1. **Ask the user for required information**:
   - Project name (will be used as branch name and subtree prefix)
   - GitHub repository URL (e.g., `https://github.com/user/repo.git`)
   - Git branch/tag to use from the repository (e.g., `main`, `master`, `v1.0.0`)

2. **Verify current state**:
   - Ensure we're on the `main` branch
   - Check for uncommitted changes (warn if any exist)
   - Confirm the project name doesn't conflict with existing branches

3. **Create the project branch**:
   ```bash
   git checkout main
   git checkout -b <project-name>
   ```

4. **Add the repository as a git subtree**:
   ```bash
   git subtree add --prefix=<project-name> <github-url> <branch> --squash
   ```

5. **Set up dependencies**:
   - Check if `pyproject.toml` exists in the subtree
   - If not, initialize uv project:
     ```bash
     uv init --no-package
     ```
   - Add common test dependencies:
     ```bash
     uv add pytest pytest-timeout
     ```
   - Commit the dependency files if created

6. **Update documentation**:
   - Add the new project to `.claude/README.md` under "Available Challenge Branches"
   - Commit the documentation update

7. **Provide next steps**:
   - Suggest running `/rebase-branches` to propagate changes
   - Remind user to create bug branches from this project branch using `/add-bug`

## Context

Project branches serve as the base for debugging challenges. Each project branch contains:
- A complete external repository (via git subtree)
- Python dependencies managed with uv
- A clean, working codebase that bug branches will branch from

The project branch itself should NOT contain bugs - it's the baseline. Bugs are added in separate bug branches created with `/add-bug`.
