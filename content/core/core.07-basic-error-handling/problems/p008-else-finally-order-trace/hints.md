## Hint 1

For `"4"` and `"-2"` no exception happens. Which of `except`, `else`, `finally` run?

## Hint 2

For `"x"`, `int` raises `ValueError`, which is handled. Does `else` run? Does the code after the
`try` statement run?

## Hint 3

`int(None)` raises `TypeError`, which no clause handles. `finally` still runs, and then the
exception leaves the function immediately: the `print("  end", ...)` line is skipped.
