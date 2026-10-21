## Walkthrough

- `n = 3`: `c` returns 30; its `finally` prints first. In `b`, no exception, so `else` runs, then
  `b returns 30`. In `a`, `return b(n)` has computed 30, then `a`'s `finally` runs, then the loop
  prints `result 30`.
- `n = 2`: `c` raises `KeyError(2)`; `c`'s `finally` runs while it propagates. `b` catches it
  (`str(KeyError(2))` is `2`), sets `result = -1`; `else` is skipped; `b returns -1`. `a` sees an
  ordinary return; its `finally` runs.
- `n = 1`: `c` raises `ValueError`; `c`'s `finally` runs. `b` has no matching clause, so its frame
  is abandoned at `result = c(n)`: no `b else`, no `b returns`. `a` catches the `ValueError`,
  prints it and returns 0, and its `finally` runs before the return completes.

## The exact output

```text
c start 3
c finally 3
b else 30
b returns 30
a finally 3
result 30
c start 2
c finally 2
b caught KeyError 2
b returns -1
a finally 2
result -1
c start 1
c finally 1
a caught bad one
a finally 1
result 0
```
