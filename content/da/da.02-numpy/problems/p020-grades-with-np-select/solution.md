## Approach

`np.select` is the vectorised `if / elif / else`: for each element it uses the first condition that is true. List `nan` first (it fails every comparison, so it would otherwise fall to the default `"F"`), then the grades from the strictest down. `>=` puts each boundary in the higher grade. All conditions are boolean arrays of the input's shape, so the result has that shape too.

## Code

```python
import numpy as np


def grades(scores):
    s = np.asarray(scores, dtype=float)
    return np.select(
        [np.isnan(s), s >= 90, s >= 75, s >= 60, s >= 40],
        ["missing", "A", "B", "C", "D"],
        default="F",
    )
```

## Complexity

O(n × number of conditions): each condition is one pass over the array.

## Another way

`np.digitize` (Ch. 14.5) does banding with a list of cut-offs: `labels = np.array(["F", "D", "C", "B", "A"])`, then `labels[np.digitize(s, [40, 60, 75, 90])]`, and finally `np.where(np.isnan(s), "missing", ...)`. Watch the string width: `np.where` on a `<U1` array and `"missing"` widens correctly, but **assigning** `"missing"` into an existing `<U1` array would cut it to `"m"`.
