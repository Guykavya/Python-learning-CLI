## Hint 1

Extra space means: how much new storage does the code create that grows with `n`? A fixed number of variables is
O(1), however large the numbers in them.

## Hint 2

In C, what does `rest[1:]` create? How many elements does it copy the first time, the second time, ...?
In E, how many different values can `x % 10` take?

## Hint 3

In F, when `total(a, 0)` runs, it must wait for `total(a, 1)`, which waits for `total(a, 2)`, ... How many calls are
waiting at the deepest point? Each waiting call needs its own memory.
