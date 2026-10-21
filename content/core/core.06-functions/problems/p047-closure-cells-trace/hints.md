## Hint 1

`get` and `inc` from one call of `make_pair` share a cell. A second call of `make_pair` makes a new cell.

## Hint 2

In `snapshot`, the inner function reads `value` when it is called, after the outer function changed it.

## Hint 3

In `loop_funcs`, all three lambdas share the one cell for `i`. In `fixed_funcs`, each lambda has its own parameter default.
