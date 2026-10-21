## Hint 1

`fib(4)` calls `fib(3)` and `fib(2)`; `fib(3)` calls `fib(2)` and `fib(1)`; and so on. Count every node in the tree.

## Hint 2

The total number of calls for `fib(n)` satisfies `calls(n) = 1 + calls(n-1) + calls(n-2)`, with `calls(0) = calls(1) = 1`.

## Hint 3

With the cache, each `n` is computed once; later requests are answered from the dict without counting a call to `slow`.
