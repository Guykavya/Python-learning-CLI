## Hint 1

Precedences: `+ -` are 1, `* /` are 2. At `*` the stack top is `+` (1), which is lower than 2: nothing leaves, `*` is pushed. At `/` the top is `*` (2): equal, so it leaves first. What is the new top then, and does it leave?

## Hint 2

A `(` is not in `PREC`, so the `while` loop stops at it: nothing below a `(` can leave until the `)`. At `)`, pop operators to the output until you see `(`, then drop the `(`. At the end, pop everything that is left, top first.
