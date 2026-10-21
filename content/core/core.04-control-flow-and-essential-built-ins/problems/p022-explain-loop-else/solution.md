See the model answer shown when you check. The ideas that must appear:

1. The `else` runs when the loop ends normally (iterable exhausted, or `while` condition false). Only `break` (or an error, or leaving the program) skips it.
2. Zero iterations: it runs. `continue`: it still runs.
3. It is designed for searches: `break` on found, `else` for not found.
4. Flag version: `found = False`, set `True` before `break`, `if not found:`. The flag is clearer to readers unfamiliar with loop `else`, and needed if you want the result later.
5. It looks like it pairs with an `if` inside; a `# no break` comment helps.
