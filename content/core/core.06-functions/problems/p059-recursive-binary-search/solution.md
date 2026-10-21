## Approach

The search space is the index range `lo..hi-1`. Each call checks the middle and recurses on the
half that can still contain the target, so the range halves every time and the recursion depth is
about log₂(n): 21 levels for two million items. `hi=None` is the sentinel for "not given",
because a default cannot refer to another parameter.

## Code

```python
def binary_search(items, target, lo=0, hi=None):
    """Return an index of target in sorted items, or -1. Recursive, no slicing."""
    if hi is None:
        hi = len(items)
    if lo >= hi:
        return -1
    mid = (lo + hi) // 2
    if items[mid] == target:
        return mid
    if items[mid] < target:
        return binary_search(items, target, mid + 1, hi)
    return binary_search(items, target, lo, mid)
```

## Complexity

O(log n) time and O(log n) stack depth; no copying.

## Another way

The loop version keeps `lo` and `hi` in variables and is the one used in practice (and in the
standard library's `bisect` module). The recursive version shows clearly why it is O(log n): each
call does O(1) work and halves the problem.
