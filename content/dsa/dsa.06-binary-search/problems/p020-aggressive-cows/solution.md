## Approach

Binary search on the distance `d`. The greedy check places cows left to right as early as possible; if `c` fit, `d` is possible. Possible distances form a prefix, so search the last True (with a round-up midpoint).

## Code

```python
n, c = map(int, input().split())
stalls = sorted(int(x) for x in input().split())


def can_place(d):
    placed, last = 1, stalls[0]
    for s in stalls:
        if s - last >= d:
            placed += 1
            last = s
    return placed >= c


lo, hi = 1, (stalls[-1] - stalls[0]) // (c - 1)
while lo < hi:
    mid = (lo + hi + 1) // 2
    if can_place(mid):
        lo = mid
    else:
        hi = mid - 1
print(lo)
```

## Complexity

O(n log n) for the sort plus O(n log(range)) for the search; O(n) memory.

## Another way

Use the closed template with an answer variable: `if can_place(mid): ans = mid; lo = mid + 1 else: hi = mid - 1`. Then `mid` can round down and nothing gets stuck.
