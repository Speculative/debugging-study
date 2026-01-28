# Debugging Study Repository

Repository for managing debugging challenges used in human trials.

## Branch Structure

```
main (only .claude/ directory)
  ├── project-name (baseline codebase from external repo)
  │   ├── project-name-bug1 (single debugging challenge)
  │   ├── project-name-bug2 (single debugging challenge)
  │   └── ...
  └── another-project (another baseline)
      └── another-project-bug1 (debugging challenge)
```

- **main**: Contains only `.claude/` directory. All other branches rebase on this.
- **Project branches** (e.g., `tinydb`): Clean baseline codebases, no bugs
- **Bug branches** (e.g., `tinydb-bug1`): Contain exactly one bug and a `run.sh` script

## Available Commands

- `/add-project` - Add new project branch from GitHub
- `/add-bug` - Add debugging challenge to a project
- `/rebase-branches` - Propagate .claude/ changes to all branches
