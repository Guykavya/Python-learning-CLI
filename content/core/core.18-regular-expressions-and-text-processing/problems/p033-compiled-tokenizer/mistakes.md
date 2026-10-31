- Putting `MISMATCH` (`.`) before the others: alternatives are tried left to right, so `.` would
  match every single character and nothing else would ever win.
- Using `\w+` for NAME and listing NAME before NUMBER: `\w` includes digits, so `42` and `12abc`
  come out as NAME tokens.
- `[+-*/=()]`: inside a class, `+-*` is a **range** from `+` to `*`, which is backwards, so
  `re.compile` raises an error.
  Put `-` first or last.
- Forgetting the dot escape: `\d+(?:.\d+)?` turns `3x5` into one number.
- Leaving out `MISMATCH`: `finditer` silently skips characters no alternative matches, so `$`
  disappears instead of raising an error.
- Compiling the pattern inside `tokens()`: it works (the `re` cache helps), but the point of the
  class is to build the pattern once.
- Using `m.groups()` and searching for the non-`None` entry by hand. `m.lastgroup` already names it.
