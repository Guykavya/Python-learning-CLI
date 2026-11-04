## Approach

First = lower bound, guarded by a presence check. Last = upper bound minus one. The second search can start from `lo = first` because nothing before it matters.

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
    if lo == n or a[lo] != x:
        out.append("-1 -1")
        continue
    first = lo
    hi = n
    while lo < hi:
        mid = (lo + hi) // 2
        if a[mid] <= x:
            lo = mid + 1
        else:
            hi = mid
    out.append(f"{first} {lo - 1}")
print("\n".join(out))
```

## Complexity

O(q log n) time, O(1) extra space.

## Another way

A single closed-template search that remembers `ans` and keeps going left (for the first) or right (for the last) after every hit: `if a[mid] == x: ans = mid; hi = mid - 1`.
