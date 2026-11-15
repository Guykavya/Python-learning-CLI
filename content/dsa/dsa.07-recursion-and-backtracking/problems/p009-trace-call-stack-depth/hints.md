## Hint 1

Draw the tree: `5` has children `4` and `3`; `4` has children `3` and `2`; `3` has children `2` and `1`. Leaves are 1 and 2. Count the nodes.

## Hint 2

The deepest path always goes left (n-1) first: 5, 4, 3, ... down to the first leaf. `deepest` is copied only when the stack gets **taller** than before, so it keeps the first tallest stack.

## Hint 3

`f(3)` makes 3 calls (itself, `f(2)`, `f(1)`), `f(4)` makes `1 + 3 + 1 = 5`. Continue to `f(5)`.
