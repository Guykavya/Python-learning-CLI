## Approach

Binary search the time `T`. `made(T)` is non-decreasing, the fastest machine alone gives the upper limit, and a candidate time costs one O(n) pass.

## Code

```python
n, t = map(int, input().split())
k = [int(x) for x in input().split()]
lo, hi = 1, min(k) * t
while lo < hi:
    mid = (lo + hi) // 2
    if sum(mid // x for x in k) >= t:
        hi = mid
    else:
        lo = mid + 1
print(lo)
```

## Complexity

O(n log(min(k) * t)) time, about 60 passes over the machines; O(1) extra space.

## Another way

Early exit inside the check: stop summing as soon as the running total reaches `t`; it makes the check faster for large `n` and does not change the result.
