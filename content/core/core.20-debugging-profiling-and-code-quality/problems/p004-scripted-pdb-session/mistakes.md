- Thinking that a stop at line 11 means `total += cost` already ran. pdb shows the line it is
  **about** to run, so at A `total` is still 0.
- Expecting the second `n` to show `book` with a new cost. Line 10 has not run yet when pdb
  stops on it, so `cost` is still the pen's 30.
- Forgetting the condition and stopping at the book at D. The book has `qty` 1.
- Expecting another stop at line 11 for the ink. `cl 1` deleted that breakpoint.
- Thinking the loop variables disappear after the loop. Python keeps the last values, so `name`
  is `ink` at line 12.
- Writing pdb's prompts or `-> ...` lines in the answer. They go to `screen`, which is never
  printed.
