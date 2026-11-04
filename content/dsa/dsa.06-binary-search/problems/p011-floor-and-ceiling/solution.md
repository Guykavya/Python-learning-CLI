## Approach

Use the lower bound for the ceiling and the upper bound minus one for the floor, and guard both against the ends of the list.

## Code

```python
n = int(input())
a = [int(x) for x in input().split()]
q = int(input())
queries = [int(x) for x in input().split()]
out = []
for x in queries:
    lo, hi = 0, n
    while lo < hi:
        mid = (lo + hi) // 2
        if a[mid] < x:
            lo = mid + 1
        else:
            hi = mid
    i = lo
    hi = n
    while lo < hi:
        mid = (lo + hi) // 2
        if a[mid] <= x:
            lo = mid + 1
        else:
            hi = mid
    j = lo
    fl = a[j - 1] if j > 0 else "none"
    ce = a[i] if i < n else "none"
    out.append(f"{fl} {ce}")
print("\n".join(out))
```

## Complexity

O(q log n) time, O(1) extra space.

## Another way

One lower-bound search `i`: the ceiling is `a[i]`. The floor is `a[i]` if `a[i] == x`, else `a[i - 1]` (if `i > 0`). That saves one search but needs the extra equality check.
