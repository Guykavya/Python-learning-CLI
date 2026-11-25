## Approach

`a + b` aligns on labels and produces `NaN` where one side has no label; `NaN` is a float, so the whole result becomes `float64`. The method `a.add(b, fill_value=0)` treats a missing side as 0, so no `NaN` appears. The result may still be float (pandas first reindexes both sides, which introduces the NaN, then fills), so convert back to `int64` once no NaN remains.

## Code

```python
import pandas as pd


def combine_months(a, b):
    return a.add(b, fill_value=0).sort_index().astype("int64")
```

## Complexity

O(n log n) for the union of labels and the sort.

## Another way

`pd.concat([a, b]).groupby(level=0).sum()` does the same thing but needs `groupby`, which comes in da.04. Or `a.reindex(all_labels, fill_value=0) + b.reindex(all_labels, fill_value=0)` makes the alignment explicit.
