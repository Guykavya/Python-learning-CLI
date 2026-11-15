## Approach

Two off-by-one bugs. (1) `a[mid] <= x` sends the search right on equal elements, so it returns the **upper** bound; the lower bound needs `a[mid] < x`. (2) `hi = n - 1` removes the answer `n` from the range, so a value larger than everything gets `n - 1`. In the half-open template `hi` starts at `n`.

## Code

```python
n = int(input())
a = [int(x) for x in input().split()]
q = int(input())
queries = [int(x) for x in input().split()]


def lower_bound(x):
    lo, hi = 0, n
    while lo < hi:
        mid = (lo + hi) // 2
        if a[mid] < x:
            lo = mid + 1
        else:
            hi = mid
    return lo


for x in queries:
    print(lower_bound(x))
```

## Complexity

O(q log n) time, O(1) extra space.

## Another way

Keep the closed template instead and carry an answer variable: `ans = n; ...; if a[mid] >= x: ans = mid; hi = mid - 1 else: lo = mid + 1`. It cannot have the "hi = n - 1" bug because the "not found" value `n` is the initial `ans`.
