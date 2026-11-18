## Approach

All three versions share the recipe of chapter section 2:

- **State:** `F(n)`, the `n`-th Fibonacci number.
- **Transition:** `F(n) = F(n - 1) + F(n - 2)`.
- **Base cases:** `F(0) = 0`, `F(1) = 1`.

They differ only in how answers to smaller questions are remembered: not at all (naive), in a notebook filled on demand (memo, top-down), or in a list filled in order (table, bottom-up).

```python
import functools


def fib_naive(n):
    if n < 2:
        return n
    return fib_naive(n - 1) + fib_naive(n - 2)


@functools.cache
def fib_memo(n):
    if n < 2:
        return n
    return fib_memo(n - 1) + fib_memo(n - 2)


def fib_table(n):
    f = [0] * (n + 1)
    if n >= 1:
        f[1] = 1
    for i in range(2, n + 1):
        f[i] = f[i - 1] + f[i - 2]
    return f[n]
```

The guard `if n >= 1` is needed because for `n = 0` the list has only one cell.

## Complexity

| Version | Time | Extra space | Recursion depth |
|---|---|---|---|
| naive | `O(phi^n)`, about `1.6^n` calls | `O(n)` stack | `n` |
| memo | `O(n)` (each state computed once) | `O(n)` notebook + stack | `n` |
| table | `O(n)` | `O(n)` list | none |

The memo version is fast but still recursive: `fib_memo(5000)` in a fresh program raises `RecursionError`. The table has no such limit.

## Another way

The memo can be your own dictionary, as in chapter section 1:

```python
memo = {}

def fib_memo(n):
    if n in memo:
        return memo[n]
    result = n if n < 2 else fib_memo(n - 1) + fib_memo(n - 2)
    memo[n] = result
    return result
```

And the table can shrink to two variables (chapter section 6), `a, b = b, a + b`, which is `O(1)` memory. Problem p006 asks for exactly that.
