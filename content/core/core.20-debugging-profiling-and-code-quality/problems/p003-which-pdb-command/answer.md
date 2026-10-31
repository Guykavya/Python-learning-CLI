1. **`s` (step).** It stops at the first line *inside* `apply_discount`. `n` would run the whole
   call as one step and you would never see its inside.
2. **`n` (next).** It runs the line, including the whole call, and stops at the next line of
   the *current* function. Then `p total` shows the new value.
3. **`r` (return).** It keeps running until the current function is about to return and stops
   there (you can still see the return value), so one more `n` puts you back in the caller.
   `c` would run on to the next breakpoint, maybe far away.
4. **A conditional breakpoint:** `b 88, row["id"] == 4071` then `c`. The condition is checked
   every time line 88 is reached, but pdb only stops when it is true. Pressing `c` 4,070 times,
   or adding an `if` with `breakpoint()` to the code, is the slow way. (`condition 1 <expr>`
   adds a condition to existing breakpoint 1.)
5. **`w` (where), then `u` twice.** `w` prints the call stack, innermost last, so you see the
   chain of callers. `u` moves the "current frame" one level up, so `p`, `ll` and `args` now
   show the *caller's* variables; `d` goes back down. The program does not move.
6. **Post-mortem.** In the REPL: `import pdb; pdb.pm()` opens pdb in the frame where the last
   uncaught exception was raised. From the terminal: `python -m pdb script.py`, press `c`, and
   pdb stops automatically at the crash. Nothing is re-run in the REPL case.
7. **`display`:** `display i`, `display total`, `display len(seen)`. Each displayed expression
   is printed whenever it **changed** at a stop. (`pp` only pretty-prints once.) `undisplay`
   removes them.
8. **`PYTHONBREAKPOINT=0 python script.py`.** `breakpoint()` calls `sys.breakpointhook()`,
   which reads this environment variable; `0` turns every `breakpoint()` into a no-op. (Setting
   it to another `module.function`, for example `PYTHONBREAKPOINT=ipdb.set_trace`, switches the
   debugger instead.) Then remove the calls before committing.

Small extra: `until` (`unt`) is handy on the last line of a loop: it continues until a line
greater than the current one is reached, so it runs the rest of the loop and stops after it.
