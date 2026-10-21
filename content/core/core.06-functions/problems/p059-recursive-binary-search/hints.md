## Hint 1

What should `hi` be when the caller does not give it? Why not use `hi=len(items)` as the default?

## Hint 2

The range `lo..hi-1` is empty when `lo >= hi`. That is the 'not found' base case.

## Hint 3

```
if hi is None: hi = len(items)
if lo >= hi: return -1
mid = (lo + hi) // 2
if items[mid] == target: return mid
if items[mid] < target: return binary_search(items, target, mid + 1, hi)
return binary_search(items, target, lo, mid)
```
