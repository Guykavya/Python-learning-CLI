## Approach

`np.lexsort` takes a sequence of keys and sorts by the **last** one first; earlier keys only break ties. So the keys go in from least to most important: `(names, ages, -scores)`. Negating the scores turns "descending" into the ascending order that `lexsort` always uses; ages and names are already ascending. `lexsort` is stable, so rows equal on all keys stay in their original order, and it returns positions (like `argsort`), which you can use to reorder any column.

Converting the names with `dtype=str` also makes an empty list a string array, so `lexsort` works on empty input.

## Code

```python
import numpy as np


def sort_records(names, scores, ages):
    names = np.asarray(names, dtype=str)
    scores = np.asarray(scores, dtype=float)
    ages = np.asarray(ages)
    return np.lexsort((names, ages, -scores))
```

## Complexity

O(n log n) per key, k keys: O(k × n log n). `-scores` is a new array, so the caller's scores are untouched.

## Another way

Sort several times with a **stable** sort, from the least important key to the most important: `order = np.argsort(names, kind="stable")`, then re-sort by age, then by `-score`, each time with `kind="stable"` and applying the result to the current order. That is what `lexsort` does internally. In pandas (da.03) the same table is `df.sort_values(["score", "age", "name"], ascending=[False, True, True])`.
