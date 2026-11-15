## Approach

The predicate "`a[i] <= a[last]`" is False for the left (high) part and True from the minimum on, so the minimum is the first True. Compare `a[mid]` with `a[hi]`, and shrink with the half-open template.

## Code

```python
n = int(input())


def ask(i):
    print("?", i, flush=True)
    return int(input())


lo, hi = 0, n - 1
while lo < hi:
    mid = (lo + hi) // 2
    if ask(mid) > ask(hi):
        lo = mid + 1
    else:
        hi = mid
print("!", ask(lo), flush=True)
```

## Complexity

O(log n) questions (two per step), O(1) memory.

## Another way

Compare against the first element of the original array: `a[i] < a[0]` is False...False True...True (when the array is really rotated). The first True is the minimum; if no True exists, `a[0]` is the minimum.
