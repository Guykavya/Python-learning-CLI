# Explain: which pdb command?

You are stopped at a `(Pdb)` prompt (or about to start one). For **each** situation below,
name the pdb command (or the way to start pdb) you would use, write the exact thing you would
type, and give a one-sentence reason why that command and not a near neighbour.

1. You are on the line `total = apply_discount(total, code)`. You suspect the bug is **inside**
   `apply_discount` and want to watch it run line by line.
2. You are on the same line, but you trust `apply_discount` and only want to see `total`
   **after** it returns.
3. You stepped into a 60-line helper by accident and want to get back to the caller as soon as
   the helper finishes.
4. A loop runs 10,000 times and goes wrong only when `row["id"] == 4071`. You want to stop on
   line 88 only in that case.
5. You have stopped deep inside `parse_line`, and you want to see **who called it** and with
   what, two levels up.
6. Your script crashed with a traceback a moment ago in the REPL (or you are running it from
   the terminal), and you want to inspect the variables **at the moment of the crash** without
   adding `breakpoint()` and running again.
7. You are stepping through a loop and want `i`, `total` and `len(seen)` printed automatically
   every time the program stops, instead of typing `p` three times at each stop.
8. Your code is full of `breakpoint()` calls from a debugging session, and you want to run it
   once **without** stopping, without editing any file.

Write `answer.md`: one short paragraph or bullet per situation (about 250 to 350 words).

**Example of the level of detail expected (a different situation)**

> *"I want to see the source around where I stopped."* `ll` (longlist) shows the whole current
> function with an arrow at the current line. `l` shows only 11 lines and continues from where
> the last listing ended when repeated, so `ll` is easier to keep your bearings with.
