# Add Bug Branch

Creates a new bug branch from an existing project branch with a single debugging challenge.

## Usage

```
/add-bug
```

## Instructions

When this command is invoked:

1. **Ask the user for required information**:
   - Project name (the base project branch, e.g., `tinydb`, `quixbugs-challenge`)
   - Bug number (or auto-detect next available number)
   - Brief description of what bug they want to add (optional, for commit message)

2. **Verify current state**:
   - Confirm the project branch exists
   - Check for uncommitted changes (warn if any exist)
   - Find the next available bug number by checking for existing `<project-name>-bug*` branches

3. **Create the bug branch**:
   ```bash
   git checkout <project-name>
   git checkout -b <project-name>-bug<N>
   ```

4. **Guide the user through adding the bug**:
   - Explain that they should now:
     a. Modify the code to introduce the bug
     b. Verify the bug causes a test failure or observable issue
   - Wait for the user to make their changes (don't make code changes automatically)

5. **Help create the run script**:
   - Ask the user what command reproduces the bug (e.g., `pytest tests/test_foo.py::test_bar`)
   - Create `run.sh` with the appropriate command:
     ```bash
     #!/bin/bash
     uv run <command>
     ```
   - Make it executable: `chmod +x run.sh`

6. **Commit the bug**:
   ```bash
   git add .
   git commit -m "[<project-name>] Add bug <N>: <description>"
   ```

7. **Verify the setup**:
   - Test that `./run.sh` reproduces the failure
   - Confirm all changes are committed

8. **Provide next steps**:
   - Suggest pushing the branch: `git push -u origin <project-name>-bug<N>`
   - Remind that this branch is now a complete debugging challenge

## Context

Bug branches are the actual debugging challenges given to participants. Each bug branch should:
- Contain exactly ONE bug (not multiple bugs)
- Have a `run.sh` script that demonstrates the failure
- Be small enough to debug within 30 minutes
- Have bugs that aren't obvious from simple code inspection
- Include clear test failures or observable incorrect behavior

### Guidelines for Good Bugs
A good 30-minute debugging challenge should:
- ✅ Require executing code to understand the failure
- ✅ Have bugs that aren't obvious from simple inspection
- ✅ Be small enough to debug within the time limit
- ✅ Have clear test cases that show failures
- ✅ Test realistic debugging scenarios
- ❌ Not be solvable by just reading the code for 5 minutes
- ❌ Not be so complex that understanding the code takes most of the time

## Bug Numbering

Bug numbers should be sequential per project. If `tinydb-bug1` and `tinydb-bug2` exist, the next bug should be `tinydb-bug3`.

The skill should auto-detect the next available number, but allow the user to override if needed.
