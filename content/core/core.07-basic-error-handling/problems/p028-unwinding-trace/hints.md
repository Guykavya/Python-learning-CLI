## Hint 1

For `n = 3` nothing is raised. Which clauses run in `b` and in `a`? Remember that `a`'s `finally`
runs before `a` actually returns to the loop.

## Hint 2

For `n = 2`, `c` raises `KeyError`. `c` has no `except`, so its `finally` runs and the exception
goes up to `b`. Does `b` handle it?

## Hint 3

For `n = 1`, `c` raises `ValueError`. `b` has only `except KeyError`, so `b` is abandoned at the
line `result = c(n)`: none of `b`'s other lines run. `a` catches it.
