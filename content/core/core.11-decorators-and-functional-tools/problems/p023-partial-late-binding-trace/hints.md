## Hint 1

The body of a `lambda` runs only when the lambda is **called**. At that moment it looks up the
name `e`. What is `e` after the loop has finished? What is it after the line `e = 10`?

## Hint 2

`partial(power, exp=e)` and the default `e=e` both **copy the current value** of `e` when the
line runs, so each one keeps its own value. A keyword given at call time overrides the keyword
stored in the partial. `partial(power, 3)` fixes the **first positional** argument, which is `base`.
