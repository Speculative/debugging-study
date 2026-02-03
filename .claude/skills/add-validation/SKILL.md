---
name: add-validation
description: Create a new validation branch from an existing project branch with a code validation challenge
---

# Add Validation Branch

Creates a new validation branch from an existing project branch with a code validation challenge. Validation tasks simulate the paradigm of LLM assistants writing code and programmers verifying whether the code is correct using execution inspection tools like autopsy.

## Usage

```
/add-validation
```

## Instructions

When this command is invoked:

1. **Detect or ask for project**:
   - Check the current git branch
   - If on a project branch (e.g., `tinydb`, `python-markdown`) or related branch (e.g., `huey-bug1`, `tinydb-validation1`), extract the project name automatically
   - Only ask the user to select a project if not currently on a project/related branch
   - Auto-detect the next available validation number by checking for existing `<project-name>-validation*` branches

2. **Verify current state**:
   - Confirm the project branch exists
   - Check for uncommitted changes (warn if any exist)
   - Find the next available validation number

3. **Create the validation branch**:
   ```bash
   git checkout <project-name>
   git checkout -b <project-name>-validation<N>
   ```

4. **Introduce a bug with failing test**:
   - Explore the codebase to understand the project structure and identify a suitable location for a bug
   - Choose a bug type that follows the guidelines (conditional path change or method call change)
   - Introduce ONE bug that:
     - Is not obvious from simple code inspection
     - Will cause at least one test to fail
     - Is realistic and debuggable
     - Follows the bug type guidelines from research (see below)
   - **IMPORTANT**: You may need to REMOVE some tests or adjust test coverage to set up the validation scenario (see step 6)
   - Do NOT tell the user what bug you introduced or where

5. **Verify the bug causes a test failure**:
   - Run the test suite to identify which test(s) now fail
   - Verify that the failure is clear and reproducible
   - If no tests fail, modify the bug or add to it until there's a clear test failure

6. **Create a plausible but subtly incorrect fix**:
   - Write a "fix" that appears to solve the problem and makes all tests pass
   - The fix should look like what an LLM coding assistant might produce - syntactically correct and seemingly logical
   - However, the fix should contain a SUBTLE LATENT BUG that:
     - Is not caught by the existing tests (due to insufficient test coverage)
     - Could be triggered by edge cases or different usage patterns
     - Would be detectable by carefully inspecting execution details with tools like autopsy
     - Represents a realistic mistake an AI assistant might make (e.g., off-by-one errors, incorrect boundary conditions, missing null checks, wrong operator precedence assumptions, incorrect type coercions)
   - **To set up this scenario, you may need to**:
     - Remove tests that would catch the latent bug
     - Adjust logic to create edge cases that aren't tested
     - Ensure the main happy path tests pass while edge cases fail
   - Document internally (not in commits) what the latent bug is for verification purposes

7. **Verify all tests pass**:
   - Run the full test suite to confirm all tests pass with the "fix"
   - If any tests fail, adjust the fix or remove/modify tests until all pass
   - The validation challenge should appear "solved" from a testing perspective

8. **Create the run script**:
   - Create `run.sh` with the command that runs the test suite:
     ```bash
     #!/bin/bash
     uv run <command>
     ```
   - Make it executable: `chmod +x run.sh`
   - The command should run the full test suite (which now passes)

9. **Commit the validation task**:
   ```bash
   git add .
   git commit -m "[<project-name>] Add validation <N>"
   ```
   - Use a generic commit message without describing the bug or fix

10. **Verify the setup**:
    - Test that `./run.sh` shows all tests passing
    - Confirm all changes are committed
    - Report to the user that the validation task has been added (without revealing the latent bug)
    - Inform the user about what the latent bug is so they can verify the challenge is valid

11. **Provide next steps**:
    - Suggest pushing the branch: `git push -u origin <project-name>-validation<N>`
    - Remind that this branch is now a complete validation challenge
    - Explain that users should use autopsy to inspect execution and identify the latent bug

## Context

Validation branches simulate real-world scenarios where LLM coding assistants write code that appears correct and passes tests, but contains subtle bugs due to insufficient test coverage. Each validation branch should:
- Contain exactly ONE bug that gets "fixed" with a subtly incorrect solution
- Have all tests passing (the fix appears to work)
- Have a latent bug that could be triggered by edge cases or different usage patterns
- Be verifiable through careful execution inspection using tools like autopsy
- Represent realistic mistakes AI assistants might make

### Types of Latent Bugs

Good latent bugs for validation tasks include:
- **Off-by-one errors**: Fix handles most cases but fails at boundaries
- **Incorrect boundary conditions**: Works for typical values but fails at min/max/zero/negative
- **Missing null/empty checks**: Handles normal cases but crashes on empty input
- **Wrong operator precedence**: Expression evaluates correctly in common cases but fails in edge cases
- **Incomplete conditionals**: Handles some cases but misses others
- **Incorrect type assumptions**: Works with expected types but fails with valid alternatives
- **Race conditions or timing issues**: Works in simple cases but fails under different execution orders

### Guidelines for Good Validation Challenges

A good validation challenge should:
- ✅ Have a fix that looks plausible and professional
- ✅ Pass all existing tests (simulate insufficient test coverage)
- ✅ Contain a subtle bug that's not obvious from code inspection alone
- ✅ Be detectable through careful execution inspection (using autopsy)
- ✅ Represent realistic AI assistant mistakes
- ✅ Require understanding the actual runtime behavior, not just reading code
- ❌ Not be obviously wrong from reading the code
- ❌ Not be so obscure that even execution inspection wouldn't help
- ❌ Not require deep domain knowledge to understand

## Validation Numbering

Validation numbers should be sequential per project. If `tinydb-validation1` and `tinydb-validation2` exist, the next validation should be `tinydb-validation3`.

The skill should auto-detect the next available number, but allow the user to override if needed.
