## Approach

Index arithmetic instead of a search: `int((x - low) / width)` gives the bin; the maximum would give index `bins` (one too many), so clamp it. Everything outside the range is counted separately instead of being squeezed into the end bins.

## Code

```python
def histogram_counts(values, bins, low=None, high=None):
    if bins < 1:
        raise ValueError("bins must be at least 1")
    if low is None or high is None:
        if not values:
            raise ValueError("empty list needs an explicit range")
        low = min(values) if low is None else low
        high = max(values) if high is None else high
    width = (high - low) / bins
    counts = [0] * bins
    outside = 0
    for x in values:
        if x < low or x > high:
            outside += 1
            continue
        i = 0 if width == 0 else min(int((x - low) / width), bins - 1)
        counts[i] += 1
    rows = []
    for i in range(bins):
        left = low + i * width
        right = high if i == bins - 1 else low + (i + 1) * width
        rows.append((left, right, counts[i]))
    return rows, outside
```

## Complexity

O(n + bins).

## Another way

`bisect` over the list of edges, which also works for unequal bin widths. For decimal data, floating-point edges can put a value on the wrong side of an edge, so real libraries (NumPy's `histogram`) check the edges after computing the index.
