## Walkthrough

The call tree of `fib(4)` has one `fib(4)`, one `fib(3)`, two `fib(2)`, three `fib(1)` and two
`fib(0)`: 9 calls in total, returning 3.

For `fib(10)` the formula `calls(n) = 1 + calls(n-1) + calls(n-2)` gives 177 calls. `fib(1)` alone
is called 55 times (a Fibonacci number itself), while `fib(9)` is called once.

With the cache, `fast(10)` computes each `n` from 0 to 10 exactly once: 11 calls that do work.
`fast(12)` then only needs to compute 11 and 12, because 10 and below are cached: 13 in total.

## The exact output

```text
3
[(0, 2), (1, 3), (2, 2), (3, 1), (4, 1)]
9
177 55 1
55 11
144 13
```
