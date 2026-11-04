## Approach

Binary search on the capacity. The feasibility check is a greedy single pass that counts days. The range is `[max(w), sum(w)]` and the predicate "days <= D" is monotone.

## Code

```python
n, d = map(int, input().split())
w = [int(x) for x in input().split()]


def days_needed(cap):
    days, load = 1, 0
    for x in w:
        if load + x > cap:
            days += 1
            load = 0
        load += x
    return days


lo, hi = max(w), sum(w)
while lo < hi:
    mid = (lo + hi) // 2
    if days_needed(mid) <= d:
        hi = mid
    else:
        lo = mid + 1
print(lo)
```

## Complexity

O(n log(sum w)) time, O(1) extra space. For n = 10^5 and sums up to 10^14 about 4.7 million steps.

## Another way

For small inputs you can also use dynamic programming over (package, day) pairs, but it costs O(n^2 D). Binary search on the answer is the standard method.
