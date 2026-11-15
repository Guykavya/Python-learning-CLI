## Approach

The predicate `a[i] > x` flips from False to True exactly once. The first True index equals the number of elements `<= x`.

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
        if a[mid] <= x:
            lo = mid + 1
        else:
            hi = mid
    out.append(lo)
print("\n".join(map(str, out)))
```

## Complexity

O(q log n) time, O(1) extra space.

## Another way

Reuse the lower bound: the number of elements `<= x` for integers equals `lower_bound(x + 1)`. This trick works for integers only, not for floats.
