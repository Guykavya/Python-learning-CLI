## Approach

The slope test "`a[i] > a[i + 1]`" is False on the rising part and True from the peak on. The peak is the first True; use the half-open template and compare each middle element with its right neighbour.

## Code

```python
n = int(input())


def ask(i):
    print("?", i, flush=True)
    return int(input())


lo, hi = 0, n - 1
while lo < hi:
    mid = (lo + hi) // 2
    if ask(mid) < ask(mid + 1):
        lo = mid + 1
    else:
        hi = mid
print("!", lo, flush=True)
```

## Complexity

O(log n) questions (two per step), O(1) memory.

## Another way

Ternary search works on unimodal data too, but needs more comparisons; the slope test with binary search is simpler and exact for integers.
