## Approach

Turn "which balloon is first?" into "which balloon is **last**?" (chapter section 17). Pad with `1` on both ends, `a = [1] + nums + [1]`.

- State: `f(i, j)` = the most coins from bursting all balloons strictly between positions `i` and `j` of `a`, with `a[i]` and `a[j]` still standing.
- Transition: the last balloon `k` between them bursts with neighbours `a[i]` and `a[j]`, and before that the two sides `(i, k)` and `(k, j)` are separate problems, because `k` stands between them the whole time.
  `f(i, j) = max over i < k < j of f(i, k) + f(k, j) + a[i] * a[k] * a[j]`.
- Base: `f(i, i + 1) = 0`. Answer: `f(0, len(a) - 1)`.

```python
def max_coins(nums):
    a = [1] + nums + [1]
    n = len(a)
    f = [[0] * n for _ in range(n)]
    for gap in range(2, n):                    # distance between i and j: short ranges first
        for i in range(n - gap):
            j = i + gap
            f[i][j] = max(f[i][k] + f[k][j] + a[i] * a[k] * a[j]
                          for k in range(i + 1, j))
    return f[0][n - 1]
```

For `[1, 5]`, `a = [1, 1, 5, 1]`: `f[0][2] = 1*1*5 = 5`, `f[1][3] = 1*5*1 = 5`, and `f[0][3] = max(k=1: 0 + 5 + 1*1*1, k=2: 5 + 0 + 1*5*1) = max(6, 10) = 10`. For `[]` the loop does not run and `f[0][1] = 0`.

## Complexity

`O(n^2)` ranges times `O(n)` choices of `k`: `O(n^3)` time, `O(n^2)` memory. For 150 balloons, about 560,000 inner steps.

## Another way

Top-down with `@functools.cache`, exactly as `burst_balloons_topdown` in section 17: `best(i, j)` returns 0 when `j - i < 2`, else the same `max` over `k`. The recursion depth is at most `len(nums) + 2`, so it is safe here. Write both and compare them on random inputs; then compare both with a brute force that tries every order on up to 7 balloons.
