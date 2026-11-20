## Approach

This is coin change with the minimum (p017), where the coins are the squares up to `n`:

- **State:** `f(a)` = the fewest squares that add up to `a`.
- **Transition:** `f(a) = 1 + min(f(a - s))` over squares `s <= a`.
- **Base:** `f(0) = 0`. Every `a >= 1` can be made (with 1s), so no `-1` case.
- **Answer:** `f(n)`.

```python
INF = float("inf")


def num_squares(n):
    squares = []
    k = 1
    while k * k <= n:
        squares.append(k * k)
        k += 1
    f = [INF] * (n + 1)
    f[0] = 0                                   # zero squares make 0
    for a in range(1, n + 1):
        for s in squares:
            if s > a:
                break                          # squares are increasing
            if f[a - s] + 1 < f[a]:
                f[a] = f[a - s] + 1
    return f[n]
```

## Complexity

`n` amounts, at most `sqrt(n)` squares each: `O(n * sqrt(n))` time, `O(n)` space.

## Another way

**Number theory** (the tests use it as an oracle). Lagrange proved every positive integer is a sum of at most **four** squares, and Legendre that it needs four exactly when it has the form `4**a * (8*b + 7)`. So: answer 1 if `n` is a square; 2 if `n - a*a` is a square for some `a`; 4 if `n` is `4**a * (8b + 7)`; otherwise 3. That is `O(sqrt(n))`, but it only works for squares; the DP works for any set of "coins". **BFS** from `n` (subtract a square per step) also finds the answer, in at most 4 layers.
