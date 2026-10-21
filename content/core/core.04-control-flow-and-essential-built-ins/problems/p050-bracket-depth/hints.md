## Hint 1

You do not need to remember **which** brackets are open, only **how many**. One counter, the
depth, is enough.

## Hint 2

`(` adds 1 to the depth, `)` subtracts 1. If the depth ever goes below 0, there was a `)` with
nothing to close. That is the moment to stop.

## Hint 3

Use `for pos, ch in enumerate(line):` with `break` for the early exit, and the loop's `else`
(or a flag) to know the loop got to the end. Track the deepest value with `max(deepest, depth)`.
