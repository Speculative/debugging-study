---
name: add-bug
description: Create a new bug branch from an existing project branch with a single debugging challenge
---

# Add Bug Branch

Creates a new bug branch from an existing project branch with a single debugging challenge.

## Usage

```
/add-bug
```

## Instructions

When this command is invoked:

1. **Detect or ask for project**:
   - Check the current git branch
   - If on a project branch (e.g., `tinydb`, `python-markdown`) or bug branch (e.g., `huey-bug1`), extract the project name automatically
   - Only ask the user to select a project if not currently on a project/bug branch
   - Auto-detect the next available bug number by checking for existing `<project-name>-bug*` branches

2. **Verify current state**:
   - Confirm the project branch exists
   - Check for uncommitted changes (warn if any exist)
   - Find the next available bug number

3. **Create the bug branch**:
   ```bash
   git checkout <project-name>
   git checkout -b <project-name>-bug<N>
   ```

4. **Automatically generate and introduce a bug**:
   - Explore the codebase to understand the project structure and identify a suitable location for a bug
   - Choose a bug type that follows the guidelines (conditional path change or method call change)
   - Introduce ONE bug that:
     - Is not obvious from simple code inspection
     - Will cause at least one test to fail
     - Is realistic and debuggable within 30 minutes
     - Follows the bug type guidelines from research (see below)
   - Do NOT tell the user what bug you introduced or where - this is for blind debugging studies

5. **Verify the bug causes a test failure**:
   - Run the test suite to identify which test(s) now fail
   - Verify that the failure is clear and reproducible
   - If no tests fail, modify the bug or add to it until there's a clear test failure

6. **Create the run script**:
   - Create `run.sh` with the command that reproduces the failure:
     ```bash
     #!/bin/bash
     uv run <command>
     ```
   - Make it executable: `chmod +x run.sh`
   - The command should run the specific failing test(s)

7. **Commit the bug**:
   ```bash
   git add .
   git commit -m "[<project-name>] Add bug <N>"
   ```
   - Use a generic commit message without describing what the bug is

8. **Verify the setup**:
   - Test that `./run.sh` reproduces the failure
   - Confirm all changes are committed
   - Report to the user that the bug has been added (without revealing what it is)

9. **Provide next steps**:
   - Suggest pushing the branch: `git push -u origin <project-name>-bug<N>`
   - Remind that this branch is now a complete debugging challenge

## Context

Bug branches are the actual debugging challenges given to participants. Each bug branch should:
- Contain exactly ONE bug (not multiple bugs)
- Have a `run.sh` script that demonstrates the failure
- Be small enough to debug within 30 minutes
- Have bugs that aren't obvious from simple code inspection
- Include clear test failures or observable incorrect behavior

### Types of Bugs

According to academic software engineering research, the majority of all bug fixes are one of two kinds:
1. Changes to a conditional path (adding a predicate to a branch, adding/removing a branch, adding an early exit branch)
2. Changing a method call by changing the expression passed to the method or changing the shape of the method call

Thus, bugs that we add should prefer to have _solutions_ that are one of these types of fixes.

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
