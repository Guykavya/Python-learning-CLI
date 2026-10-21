## Hint 1

The starter returns `None` after logging. What does the caller learn from `None`? What should
happen instead?

## Hint 2

Inside an `except` block, `raise` with nothing after it re-raises the exception being handled.
