## Hint 1

`[[0] * 3] * 2` makes **one** inner list and puts two references to it in the outer list.

## Hint 2

`m = [row, row]` is the same situation, written by hand. What does `m[0] = [1, 1]` change: the
shared row, or only slot 0 of `m`?

## Hint 3

`k[1] = k[1] + ["y"]` builds a **new** list and puts it in slot 1. `k[0].append("x")` changes
the shared list.
