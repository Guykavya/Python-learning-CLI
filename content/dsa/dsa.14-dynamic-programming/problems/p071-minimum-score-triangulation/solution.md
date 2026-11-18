## Approach

Interval DP over the corners (chapter section 17). The side from corner `i` to corner `j` must be in one triangle, whose third corner `k` lies between them. That triangle cuts the piece `i..j` into two smaller pieces, `i..k` and `k..j`, which are triangulated independently.

- State: `f(i, j)` = cheapest triangulation of the piece with corners `i..j`.
- Transition: `f(i, j) = min over i < k < j of f(i, k) + f(k, j) + values[i] * values[k] * values[j]`.
- Base: `f(i, j) = 0` when `j - i < 2` (a side, not a polygon).
- Order: by gap `j - i`, short pieces first. Answer: `f(0, n - 1)`.

```python
def min_score_triangulation(values):
    n = len(values)
    f = [[0] * n for _ in range(n)]
    for gap in range(2, n):                     # short pieces first
        for i in range(n - gap):
            j = i + gap
            f[i][j] = min(f[i][k] + f[k][j] + values[i] * values[k] * values[j]
                          for k in range(i + 1, j))
    return f[0][n - 1]
```

For `[3, 7, 4, 5]`: `f[0][2] = 3*7*4 = 84`, `f[1][3] = 7*4*5 = 140`, and `f[0][3] = min(k=1: 0 + 140 + 3*7*5, k=2: 84 + 0 + 3*4*5) = min(245, 144) = 144`.

## Complexity

`O(n^3)` time, `O(n^2)` memory.

## Another way

Three problems in this module share one skeleton: matrix chain (`min`, split **between** `k` and `k+1`), burst balloons (`max`, `k` is the **last** balloon and both parts keep `k` as a boundary), and this one (`min`, both parts keep `k`). Write a top-down version with `@functools.cache`; then notice that it is `burst_balloons_topdown` with `max` replaced by `min` and no padding. Seeing that the three are one pattern is the real lesson of interval DP.
