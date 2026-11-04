## Approach

Binary search the cost `S`. A greedy scan gives the fewest pieces needed for a given `S`; the predicate "fewest pieces <= m" is monotone in `S`. The answer is in `[max(a), sum(a)]`.

## Code

```python
n, m = map(int, input().split())
a = [int(x) for x in input().split()]


def pieces(limit):
    count, cur = 1, 0
    for x in a:
        if cur + x > limit:
            count += 1
            cur = 0
        cur += x
    return count


lo, hi = max(a), sum(a)
while lo < hi:
    mid = (lo + hi) // 2
    if pieces(mid) <= m:
        hi = mid
    else:
        lo = mid + 1
print(lo)
```

## Complexity

O(n log(sum a)) time, O(1) extra space.

## Another way

A dynamic programme `dp[j][i]` = best cost for the first `i` elements in `j` pieces runs in `O(m n^2)` (or `O(m n log n)` with tricks): fine for tiny inputs, impossible for 10^5.
