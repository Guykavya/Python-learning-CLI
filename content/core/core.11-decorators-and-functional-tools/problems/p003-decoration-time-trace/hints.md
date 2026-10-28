## Hint 1

`@loud` above `def hello` means `hello = loud(hello)`, and that line runs as soon as Python reaches the `def`.
Which `print` lines are in the body of `loud` itself, and which are inside `wrapper`?

## Hint 2

Split the run into three parts: before the `def` (`start`), the decoration (the prints in `loud`),
and each call of `hello()` (the prints in `wrapper`, with the body of the original in the middle).
After decoration, the name `hello` points at `wrapper`. What is `wrapper.__name__`?
