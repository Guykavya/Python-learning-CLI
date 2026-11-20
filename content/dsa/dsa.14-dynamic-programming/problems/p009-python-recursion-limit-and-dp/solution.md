## Approach

The memoised function is a correct DP; only its **depth** is wrong for Python. Convert it to a table (chapter section 4):

- **State:** `f(i)` = the fewest moves from `i` to 1.
- **Transition:** `f(i) = 1 + min(f(i - 1), f(i // 2) if i is even, f(i // 3) if 3 divides i)`.
- **Base:** `f(1) = 0`.
- **Order:** every dependency is smaller than `i`, so `i` goes up.

```python
def min_steps(n):
    f = [0] * (n + 1)                  # f[1] = 0: already at 1
    for i in range(2, n + 1):
        best = f[i - 1] + 1
        if i % 2 == 0 and f[i // 2] + 1 < best:
            best = f[i // 2] + 1
        if i % 3 == 0 and f[i // 3] + 1 < best:
            best = f[i // 3] + 1
        f[i] = best
    return f[n]
```

## Complexity

`O(n)` time and space, no recursion. `n = 2 * 10**5` takes a fraction of a second.

## Another way

Keep the memoised function and **warm the cache from the bottom**:

```python
import functools

@functools.cache
def go(n):
    if n == 1:
        return 0
    best = go(n - 1) + 1
    if n % 2 == 0:
        best = min(best, go(n // 2) + 1)
    if n % 3 == 0:
        best = min(best, go(n // 3) + 1)
    return best

def min_steps(n):
    for k in range(1, n, 500):
        go(k)                  # each call finds go(k - 500) cached: at most ~500 frames deep
    return go(n)
```

It works but is slower (function calls and hashing for every state) and it is easy to get the warm-up step wrong. The table is the standard answer for long chains of states.

This problem is also a shortest path in a graph whose edges go `i -> i - 1`, `i -> i/2`, `i -> i/3`; the test checks you with a BFS. DP works here because all edges point to smaller numbers (a DAG, chapter section 1).
