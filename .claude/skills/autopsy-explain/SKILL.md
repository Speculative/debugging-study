---
name: autopsy-explain
description: Use the `autopsy` python library to add logs to help the user learn about the code
---

# Autopsy Explain
Strategically adds `autopsy` logs to the code before running it in order to explain the code to the user by showing them intermediate execution steps which are connected back to the code.

## Usage
```
/autopsy-explain : gives an overview of the entire codebase's execution
/autopsy-explain <prompt> : targets logging to answer a specific question about the code
```

## Background & `autopsy` API
`autopsy` is a python library that combines print and time-travel debugging. The `autopsy` python library has an API for adding logs (which go beyond simple print logging) and a web-based viewer for these logs that allows for interactive exploration. The interactive viewer allows users to see:

1. History: view an entire historical log (similar to println output)
2. Streams: View output separated by logging site (as tables, where each row is a log invocation and columns correspond to the log arguments)
3. Call Stacks: For each log, see a complete stack trace with values of local variables (similar to what a breakpoint debugger would show when stopped on a breakpoint)
4. Dashboard: Get an overview of the entire execution with a data visualization dashboard that's connected to logs
5. Filter logs based on test they executed under, range within history (i.e., "from event X to event Y")
6. Computed Logs: Interactive, "retroactive" augmentation of logs by pulling information from call stacks
7. Time Travel: Time travel debug (stepping forward/back, jumping to arbitrary points in execution) between logs

The `autopsy` API consists of:
- `autopsy.log(...)`: a variadic function whose arguments are shown in the History and Stream views. This is the most common API call.
- `autopsy.happened("an event")`: a way to more prominently signal that some significant step has occurred, similar to `print("got to here")`
- `autopsy.timeline("an event")`: similar to happened, but will also be shown on the dashboard in a timeline view.
- `autopsy.count("event name")`: will increment by one each time it's called and show up on a bar plot
- `autopsy.hist(123)`: will aggregate over all invocations at this call site and display a histogram, useful for helping show if there's something interesting about the distribution

## Instructions

When this command is invoked:

1. **Understand the scope**
   - If the user provided a `<prompt>`, they are asking a specific question about the code (e.g., "how does the shortest path get computed?", "what order are the loops executing in?"). Your logging strategy should be targeted to answer that question.
   - If no prompt is given, your goal is to give the user an overview of the entire codebase's execution -- what functions get called, what data flows through them, and what the overall structure looks like at runtime.

2. **Read and understand the codebase**
   - Read the source files to understand the code's structure, key functions, data flow, and control flow.
   - Read any existing test files to understand what inputs exercise the code.
   - Identify the "interesting" parts of the code: loops, conditionals, recursive calls, algorithm steps, data transformations, function entry/exit points.

3. **Plan your logging strategy**
   - Decide which autopsy API calls to insert and where. Choose from:
     - `autopsy.log(...)` -- the workhorse. Use for capturing variable values at key points. Pass the actual expressions you want the user to see as arguments (e.g., `autopsy.log(i, j, dist[i][j])`). The viewer will automatically label columns with the expression names. You can also pass a string literal as the first argument to name the log entry (e.g., `autopsy.log("relaxation step", i, j, new_dist)`).
     - `autopsy.happened("message")` -- use for control flow landmarks: "entered this branch", "loop terminated early", "base case reached". Shows up prominently in the history.
     - `autopsy.timeline("event")` -- use for high-level phases of execution that should appear on the dashboard timeline (e.g., "initialization complete", "processing phase 2").
     - `autopsy.count("label")` -- use when the interesting thing is *how many times* something happens (e.g., how many cache hits vs misses, how many times a branch is taken).
     - `autopsy.hist(number)` -- use when you want to show the distribution of a numeric value across all invocations (e.g., distances computed, array sizes processed).
   - **Be strategic, not exhaustive.** Too many logs (especially inside tight inner loops) create noise and slow execution. Aim for 5-20 logging sites that tell a clear story. If a loop runs N^3 times, consider logging only on interesting conditions (e.g., when a value changes) or logging at a coarser granularity (e.g., per outer-loop iteration rather than innermost).
   - **For targeted questions**, focus logging around the specific code the user asked about.
   - **For overview mode**, spread logging across the main functions and key decision points to give a broad picture of execution flow.

4. **Plan the execution strategy**
   Decide what to run to generate the logs. Choose the best option:
   - **Existing tests** (preferred when available): Run the test suite or a subset of it. Tests provide well-defined inputs with known expected outputs, making the logs easier to interpret. Use `uv run --only-group dev pytest <test_file> -v --autopsy-live` to run with live mode.
   - **Bespoke input**: If the tests don't exercise the code path the user cares about, write a small script or modify the `if __name__ == "__main__"` block to call the relevant functions with specific inputs that illustrate the behavior.
   - **Custom execution harness**: For complex codebases where you want to drive just a subset of the code, create a small temporary Python script that imports the relevant module, sets up minimal inputs, and calls the functions of interest. This is useful when the full test suite is too slow or pulls in too many dependencies.

   When creating a custom harness, include `autopsy.init()` at the top and structure it like:
   ```python
   import autopsy
   autopsy.init()

   # Import the code under study
   from module import function_of_interest

   # Set up inputs
   ...

   # Run the code (autopsy.log calls inside it will be captured)
   result = function_of_interest(inputs)
   ```

5. **Insert the logging calls**
   - Add `import autopsy` at the top of any file you're instrumenting (if not already present).
   - Insert your planned autopsy calls at the chosen locations.
   - Do NOT remove or modify existing code logic -- only add autopsy calls.
   - Do NOT remove any existing autopsy calls that are already in the code (they were placed there intentionally).
   - Keep logging calls on their own lines so they're easy to identify and the source location tracking works correctly.

6. **Run the code**
   - Use `uv run --only-group dev` to run with only the dev dependencies (which include autopsy and pytest), avoiding heavy ML/scientific dependencies from the main project.
   - If running tests: `uv run --only-group dev pytest <test_file> -v --autopsy-live`
   - If running a custom harness: `uv run --only-group dev python <harness_file>`
   - If the code errors out or hangs, diagnose and fix the issue (e.g., reduce logging in hot loops, fix import errors).

7. **Present results to the user**
   - Tell the user the execution is complete and that they can view the autopsy report.
   - If running with `--autopsy-live`, explain that the live viewer in their VSCode sidebar should be showing the results.
   - If running without live mode, an `autopsy_report.html` file will be generated -- tell the user to open it in their browser.
   - Give a brief natural-language summary of what the logging is set up to show (e.g., "I've added logging to show the distance matrix after each iteration of the outer loop, so you can see how shortest paths are progressively discovered").
   - Do NOT attempt to interpret or explain the full execution output yourself -- the whole point is for the user to explore it interactively in the autopsy viewer.

### Guidelines

- **Preserve the code.** This skill is read-only with respect to the code's logic. You are only adding observability. Never fix bugs, refactor, or change behavior.
- **Be mindful of log volume.** An `autopsy.log()` inside a triply-nested loop over an N=100 graph produces 1M log entries. Either log at a coarser granularity, add a condition (e.g., `if new_val < old_val: autopsy.log(...)`), or use dashboard APIs (`count`, `hist`) that aggregate instead.
- **Use descriptive first arguments.** `autopsy.log("relaxation", i, j, new_dist)` is much more useful than `autopsy.log(i, j, new_dist)` because the string literal becomes the log entry's name in the viewer.
- **Use `timeline` for phases.** If the algorithm has distinct phases (initialization, main loop, finalization), mark them with `autopsy.timeline()` so they appear on the dashboard.
- **Prefer running existing tests** over writing custom harnesses when the tests already cover the relevant code paths. Tests provide structure (pass/fail per test case, log ranges per test) that the autopsy viewer can use.
