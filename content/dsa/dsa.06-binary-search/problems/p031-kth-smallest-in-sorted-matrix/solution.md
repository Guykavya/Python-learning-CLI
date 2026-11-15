## Approach

Binary search on the value. `count_le(v)` (entries `<= v`) is non-decreasing in `v` and costs O(n) with a staircase walk. The smallest `v` with `count_le(v) >= k` is the k-th smallest.

## Code

```python
n, k = map(int, input().split())
m = [[int(x) for x in input().split()] for _ in range(n)]


def count_le(v):
    r, c, cnt = n - 1, 0, 0
    while r >= 0 and c < n:
        if m[r][c] <= v:
            cnt += r + 1
            c += 1
        else:
            r -= 1
    return cnt


lo, hi = m[0][0], m[n - 1][n - 1]
while lo < hi:
    mid = (lo + hi) // 2
    if count_le(mid) >= k:
        hi = mid
    else:
        lo = mid + 1
print(lo)
```

## Complexity

O(n log(max - min)) time for the search (about 30 walks of 2n steps), plus O(n^2) to read the input.

## Another way

Use a min-heap with the first element of each row and pop `k` times: `O(k log n)`. It is fine for small `k` but slow when `k` is near `n^2`. A third way is a divide-and-conquer selection in `O(n)` (advanced).
