## Approach

`sorted` returns a new list, so the caller's list is never changed (`list.sort()` would). Counting with a dict gives the mode(s) in one pass.

## Code

```python
def mean(values):
    if not values:
        raise ValueError("mean of an empty list")
    return sum(values) / len(values)

def median(values):
    if not values:
        raise ValueError("median of an empty list")
    s = sorted(values)
    mid = len(s) // 2
    return s[mid] if len(s) % 2 else (s[mid - 1] + s[mid]) / 2

def modes(values):
    if not values:
        raise ValueError("modes of an empty list")
    counts = {}
    for v in values:
        counts[v] = counts.get(v, 0) + 1
    top = max(counts.values())
    return sorted(v for v, c in counts.items() if c == top)
```

## Complexity

`mean` O(n); `median` O(n log n) (sorting); `modes` O(n + k log k).

## Another way

`statistics.fmean`, `statistics.median` and `statistics.multimode` do the same. A selection algorithm (quickselect) finds the median in O(n) average time without a full sort.

Note the odd-length median keeps the data type (an int for int data); the even case divides by 2 and gives a float.
