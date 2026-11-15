## Approach

If `m * k > n` print -1. Otherwise binary search the day: `bouquets(day)` is a greedy left-to-right scan and is non-decreasing in `day`, so find the first day where it reaches `m`.

## Code

```python
n, m, k = map(int, input().split())
bloom = [int(x) for x in input().split()]


def bouquets(day):
    run = count = 0
    for b in bloom:
        if b <= day:
            run += 1
            if run == k:
                count += 1
                run = 0
        else:
            run = 0
    return count


if m * k > n:
    print(-1)
else:
    lo, hi = min(bloom), max(bloom)
    while lo < hi:
        mid = (lo + hi) // 2
        if bouquets(mid) >= m:
            hi = mid
        else:
            lo = mid + 1
    print(lo)
```

## Complexity

O(n log(max bloom)) time, O(1) extra space.

## Another way

Sort the distinct bloom days and binary search over that sorted list of candidate days (the answer is always one of them). The range-based search above does not need the sort.
