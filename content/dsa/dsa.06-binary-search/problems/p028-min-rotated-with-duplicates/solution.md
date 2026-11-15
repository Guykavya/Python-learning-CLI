## Approach

The three-way comparison of `a[mid]` with `a[hi]`: greater means the minimum is right of `mid`, smaller means at `mid` or left. Equal gives no information about the side, but `a[hi]` is redundant (a copy sits at `mid`), so drop it with `hi -= 1`.

## Code

```python
t = int(input())
for _ in range(t):
    n = int(input())
    a = [int(x) for x in input().split()]
    lo, hi = 0, n - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if a[mid] > a[hi]:
            lo = mid + 1
        elif a[mid] < a[hi]:
            hi = mid
        else:
            hi -= 1
    print(a[lo])
```

## Complexity

O(log n) typically, O(n) in the worst case (all equal but one). Memory O(n) for the input.

## Another way

Detect the drop explicitly: find an index `i` with `a[i] > a[i + 1]` using the same idea; with duplicates there is no way to be faster than O(n) in the worst case, because the single smaller element can hide anywhere in a block of equal numbers.
