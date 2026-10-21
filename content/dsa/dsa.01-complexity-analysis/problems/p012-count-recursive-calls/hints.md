## Hint 1

Draw the recursion tree for `fib(4)`: a box for `fib(4)` with two children `fib(3)` and `fib(2)`, and so on until
every leaf is `fib(1)` or `fib(0)`. Count every box. Do not reuse boxes: the program does not remember results.

## Hint 2

One call to `fib(n)` (for `n >= 2`) is itself plus all calls made by `fib(n - 1)` plus all calls made by
`fib(n - 2)`. So `C(n) = 1 + C(n - 1) + C(n - 2)`, with `C(0) = C(1) = 1`.

## Hint 3

Build a table for `n = 0` to `10` for both the value (0, 1, 1, 2, 3, 5, ...) and `C(n)` (1, 1, 3, 5, ...).
