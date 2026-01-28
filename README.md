# Debugging Study Repository

This repository is used to run human trials for a research project building a new debugging tool. It contains debugging challenges for participants to solve using our tool.

## Repository Structure

**IMPORTANT**: The `main` branch contains ONLY this README file. All debugging challenges are organized as separate branches.

Each branch contains:
- A complete debugging challenge or problem set
- Setup instructions specific to that challenge
- Test cases to verify solutions
- Dependencies managed via `uv` with committed `pyproject.toml` and lock files

## Available Challenge Branches

### QuixBugs
**Branch**: `quixbugs-challenge`

The QuixBugs benchmark - a collection of 40 classic algorithms, each with a single-line bug.

**Recommended challenges for 30-minute sessions**:
- `rpn_eval` - Reverse Polish Notation calculator (operand order bug)
- `kth` - QuickSelect algorithm (recursion parameter bug)
- `hanoi` - Towers of Hanoi (wrong destination in recursive call)
- `shunting_yard` - Infix to RPN conversion (missing operator append)
- `wrap` - Text wrapping (missing final line)

**Setup**:
```bash
git checkout quixbugs-challenge
# See branch README for detailed instructions
```

## Goals

This repository aims to:
1. Provide reproducible debugging challenges for research participants
2. Test the effectiveness of debugging tools in controlled environments
3. Collect data on debugging workflows and problem-solving approaches
4. Support various difficulty levels from simple bugs to complex algorithmic issues

## Adding New Projects and Bugs

### Creating a New Challenge Branch

1. **Start from main** (which contains only this README):
```bash
git checkout main
git pull
git checkout -b your-challenge-name
```

2. **Add your debugging challenge**:
   - Add the buggy code/project files
   - Create or include test cases
   - Write a README.md with challenge-specific instructions

3. **Set up dependency management with uv**:
```bash
# Initialize uv project (if not already present)
uv init --no-package

# Add dependencies
uv add pytest pytest-timeout
# Add other dependencies as needed

# This creates pyproject.toml and uv.lock
```

4. **Create a challenge-specific README**:
   - Explain what the challenge is
   - Provide setup instructions
   - Document how to run tests
   - List any prerequisites
   - Include expected time to complete
   - Document the bug location (for your reference, not for participants)

5. **Commit everything**:
```bash
git add .
git commit -m "Add [challenge-name] debugging challenge"
```

6. **Update this main README** with the new branch information:
```bash
git checkout main
# Edit README.md to add new branch to "Available Challenge Branches"
git add README.md
git commit -m "Document [challenge-name] branch"
```

7. **Rebase your challenge branch on main**:
```bash
git checkout your-challenge-name
git rebase main
```

### Adding External Git Repositories as Challenges

For challenges that use external git repos:

1. **Branch from main**:
```bash
git checkout main
git checkout -b challenge-name
```

2. **Add as git subtree**:
```bash
git subtree add --prefix=project-name https://github.com/user/repo.git branch --squash
```

3. **Add uv dependencies and README** as described above

4. **Commit and update main README**

### Guidelines for Good Debugging Challenges

A good 30-minute debugging challenge should:
- ✅ Require executing code to understand the failure
- ✅ Have bugs that aren't obvious from simple inspection
- ✅ Be small enough to debug within the time limit
- ✅ Have clear test cases that show failures
- ✅ Test realistic debugging scenarios
- ❌ Not be solvable by just reading the code for 5 minutes
- ❌ Not be so complex that understanding the code takes most of the time

## Dependency Management with uv

All projects in this repository use [uv](https://github.com/astral-sh/uv) for Python dependency management.

### Why uv?
- Fast and reliable dependency resolution
- Automatic virtual environment management
- Reproducible builds via lock files
- No manual virtualenv activation needed

### Standard Setup Pattern

Each challenge branch should include:
- `pyproject.toml` - Project metadata and dependency specifications
- `uv.lock` - Locked dependency versions for reproducibility

Participants can run tests without manual setup:
```bash
uv run --with pytest --with pytest-timeout pytest path/to/tests/
```

### Committing Dependencies

**Always commit**:
- ✅ `pyproject.toml`
- ✅ `uv.lock`

**Never commit**:
- ❌ `.venv/` (add to .gitignore)
- ❌ `__pycache__/` (add to .gitignore)
- ❌ `.pytest_cache/` (add to .gitignore)

## Branch Management

### Main Branch Rules
- Contains ONLY this README file
- Never contains any project code or bugs
- All challenge branches should be rebased on main when this README is updated
- Serves as the common starting point for all challenge branches

### Challenge Branch Rules
- Each challenge is a separate branch
- Branches should be rebased on main when the main README is updated
- Branch names should be descriptive (e.g., `quixbugs-challenge`, `project-x-bug`)
- Each branch has its own README with challenge-specific instructions

## Workflow Summary

```
main (README only)
  ├── quixbugs-challenge (QuixBugs benchmark + README + deps)
  ├── future-challenge-1 (Project 1 + README + deps)
  └── future-challenge-2 (Project 2 + README + deps)
```

When main README is updated:
```bash
# Update each challenge branch
git checkout challenge-branch-name
git rebase main
```

## For Research Participants

If you're participating in a debugging study:

1. **Clone this repository**:
```bash
git clone [repository-url]
cd debugging-study
```

2. **Check out your assigned challenge**:
```bash
git checkout [challenge-branch-name]
```

3. **Follow the instructions** in that branch's README

4. **Use the provided debugging tool** as instructed by the research team

## Contact

For questions about this repository or the research project, contact [research team contact info].
