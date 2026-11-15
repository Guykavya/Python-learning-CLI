## Approach

The plain recursion tree for `fib(n)` has about `1.6^n` nodes, but only `n + 1` **different** sub-problems (`fib(0)` ... `fib(n)`). Store each answer the first time; afterwards each repeated sub-tree is replaced by one dictionary look-up.

## Code

```python
memo = {}


def fib(n):
    if n < 2:
        return n
    if n in memo:
        return memo[n]
    memo[n] = fib(n - 1) + fib(n - 2)
    return memo[n]
```

## Complexity

`O(n)` time (each `n` is computed once) and `O(n)` memory for the memo and the stack. The depth for `fib(500)` is about 500 calls, still under the limit of 1000.

## Another way

A loop with two variables needs no memo and no stack:

```python
def fib(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a
```

`functools.cache` on the plain recursive function does the same memoisation automatically.
