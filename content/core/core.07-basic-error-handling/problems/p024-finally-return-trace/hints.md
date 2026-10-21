## Hint 1

`else` runs only when the `try` block reaches its end without an exception **and without
leaving early**. Which of the three calls to `first` lets the `try` block reach its end?

## Hint 2

In `build`, the `return` statement evaluates `items, count` into a tuple **before** `finally`
runs. The tuple holds the list object (which `finally` then changes) and the int `1` (which
`finally` cannot change, it can only rebind the name `count`).

## Hint 3

A `return` in `finally` replaces any return value and discards a pending exception. In the loop,
`continue` and `break` inside `try` still run `finally` before they take effect.
