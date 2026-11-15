## Hint 1

`fib(5)` starts, then `fib(4)` (and everything below it) runs completely, and only then `fib(3)` starts. Write the left sub-tree first.

## Hint 2

`fib(2)` makes the calls `2, 1, 0`. `fib(3)` makes `3, 2, 1, 0, 1`. Build `fib(4)` = `4` + calls of `fib(3)` + calls of `fib(2)`.

## Hint 3

The leaves are the calls with `n < 2`. `fib(5) = 5` is the number of leaves with value 1.
