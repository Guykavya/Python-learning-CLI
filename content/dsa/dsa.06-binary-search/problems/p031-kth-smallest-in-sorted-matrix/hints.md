## Hint 1

The answer is a value in the matrix. What are the smallest and the largest value it can be? And how can you count the entries `<= v` without looking at all `n * n` of them?

## Hint 2

Start at the bottom-left cell `(n - 1, 0)`. If `m[r][c] <= v`, all `r + 1` entries of column `c` up to this row are `<= v`: add `r + 1`, and move right. Otherwise move up. That takes at most `2n` steps.

## Hint 3

```
lo, hi = m[0][0], m[n-1][n-1]
while lo < hi:
    mid = (lo + hi) // 2
    if count_le(mid) >= k: hi = mid       # mid may be the answer
    else: lo = mid + 1
print(lo)
```
The first value `v` with `count_le(v) >= k` is always a value that exists in the matrix.
