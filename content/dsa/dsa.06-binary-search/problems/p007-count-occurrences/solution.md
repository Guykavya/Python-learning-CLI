## Approach

All copies of `x` are one contiguous block `[lower_bound(x), upper_bound(x))` in a sorted list. Its length is the count.

## Code

```python
n = int(input())
a = [int(x) for x in input().split()]
q = int(input())
queries = [int(x) for x in input().split()]


def lower(x):
    lo, hi = 0, n
    while lo < hi:
        mid = (lo + hi) // 2
        if a[mid] < x:
            lo = mid + 1
        else:
            hi = mid
    return lo


def upper(x):
    lo, hi = 0, n
    while lo < hi:
        mid = (lo + hi) // 2
        if a[mid] <= x:
            lo = mid + 1
        else:
            hi = mid
    return lo


print("\n".join(str(upper(x) - lower(x)) for x in queries))
```

## Complexity

O(q log n) time, O(1) extra space.

## Another way

Store the sorted list as run-length pairs `(value, count)` and search the distinct values once: useful when the same list is queried millions of times.
