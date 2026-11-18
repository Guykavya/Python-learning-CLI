## Approach

The recipe of chapter section 2:

- **State:** `f(i)` = the number of ways to stand on step `i`.
- **Transition:** the last move came from `i - 1` or from `i - 2`, so `f(i) = f(i - 1) + f(i - 2)`.
- **Base:** `f(0) = 1` (do nothing), `f(1) = 1`.
- **Answer:** `f(n)`. **Order:** increasing `i`.

Because only sums are involved, we can take the remainder at every step and store small numbers.

```python
MOD = 10**9 + 7


def climb_stairs(n):
    f = [0] * (n + 1)
    f[0] = 1
    if n >= 1:
        f[1] = 1
    for i in range(2, n + 1):
        f[i] = (f[i - 1] + f[i - 2]) % MOD
    return f[n]
```

## Complexity

`O(n)` time and `O(n)` space. No recursion, so no depth limit.

## Another way

Each cell only reads the two before it, so two variables are enough (chapter section 6):

```python
def climb_stairs(n):
    a, b = 1, 1                 # f(i-1), f(i)  starting at i = 1
    for _ in range(n - 1):
        a, b = b, (a + b) % MOD
    return b if n >= 1 else 1
```

`O(1)` space. A memoised recursion gives the same numbers for small `n`, but for `n = 10**5` it is 100,000 calls deep and raises `RecursionError`.
