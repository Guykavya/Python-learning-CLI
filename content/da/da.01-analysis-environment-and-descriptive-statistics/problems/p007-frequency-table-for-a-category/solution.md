## Approach

Normalise first, count second, sort by a two-part key. Negating the count gives "descending count, ascending value" in one `sort`.

## Code

```python
from collections import Counter

def frequency_table(values):
    labels = ["(missing)" if v is None or v == "" else v for v in values]
    total = len(labels)
    counts = Counter(labels)
    rows = [(v, c, round(100 * c / total, 1)) for v, c in counts.items()]
    rows.sort(key=lambda r: (-r[1], r[0]))
    return rows
```

## Complexity

O(n) to count, O(k log k) to sort k distinct values.

## Another way

`Counter.most_common()` sorts by count but its tie order is first-seen, not alphabetical, so a second key is still needed.
