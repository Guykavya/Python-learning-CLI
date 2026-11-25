# Which bin does it fall in?

Chapter section 14.5. The interesting values are the ones that sit **exactly on an edge**: they decide whether a bin includes its left or its right end.

- `np.digitize(values, edges)` returns, for each value, the number of the bin: `0` before the first edge, `len(edges)` after the last. With the default `right=False` a bin includes its **left** edge (`edges[i-1] <= v < edges[i]`); with `right=True` it includes its **right** edge (`edges[i-1] < v <= edges[i]`).
- `np.searchsorted(sorted_array, values, side=...)` returns where each value would be inserted to keep the array sorted: `side="left"` (default) before any equal elements, `side="right"` after them.

```python
import numpy as np

edges = np.array([10, 20, 30])
values = np.array([5, 10, 15, 20, 30, 35])

print(np.digitize(values, edges).tolist())
print(np.digitize(values, edges, right=True).tolist())
print(np.searchsorted(edges, values).tolist())
print(np.searchsorted(edges, values, side="right").tolist())

labels = np.array(["low", "mid", "high", "top"])
print(labels[np.digitize(values, edges)].tolist())
print(np.bincount(np.digitize(values, edges, right=True), minlength=4).tolist())
```

Hand-trace the program and write **every line it prints** in `answer.txt` (six lines).

Do not run the code before you have written your answer.

## Example

With `edges = [10, 20, 30]`, the value `25` lies between 20 and 30, so `np.digitize([25], edges).tolist()` prints `[2]` with either `right` setting: it is not on an edge.

## After you answer

- Two of the four first lines are equal to each other, and the other two are equal too. Which pairs, and why?
- The chapter's grade cut-offs (Ch. 14.5) give a mark of exactly 40 a "D". Which `right` setting does that use?
