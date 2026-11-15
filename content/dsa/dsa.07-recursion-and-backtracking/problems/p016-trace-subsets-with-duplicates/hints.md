## Hint 1

The root is `go(0)` with path `[]`. Its loop tries `i = 0` (value 1), `i = 1` (value 2), `i = 2` (value 2). Which of these is skipped?

## Hint 2

Inside the child with path `[1, 2]` the call is `go(2)`: its loop starts at `i = 2 = start`, so the test `i > start` is false and the second 2 is allowed. Inside the child with path `[1]` (`go(1)`), `i = 2` is a **sibling** of `i = 1` with the same value.

## Hint 3

A skip line is printed in the parent's loop, **after** the sub-tree of the previous sibling has finished.
