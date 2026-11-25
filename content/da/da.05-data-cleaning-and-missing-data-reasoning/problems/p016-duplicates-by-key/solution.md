## Approach

Sorting makes "the survivor" the **last** row of each group, and `drop_duplicates(keep="last")` keeps exactly that one.
A *stable* sort keeps rows with equal order values in file order, so a tie goes to the later row, as the rule says.
Instead of returning the sorted frame (which would shuffle the data as a side effect), the code only uses the sort to
find *which rows win*, then selects them from the original frame with a Boolean mask. The same mask, inverted, gives the
removed rows for the log.

## Code

```python
import pandas as pd


def dedupe_by_key(df, key, order_by):
    work = df.reset_index(drop=True)
    winners = work.sort_values(order_by, kind="stable").drop_duplicates(subset=key, keep="last").index
    keep = work.index.isin(winners)
    return df[keep].copy(), df[~keep].copy()
```

## Complexity

O(n log n) for the sort, O(n) for the rest.

## Another way

`df.loc[df.groupby(key)[order_by].idxmax()]` also picks the row with the largest value per key, but `idxmax` returns the
**first** row at a tie, which breaks the "later row wins" rule, and the result is ordered by key. Another option is
`df.sort_values(order_by).drop_duplicates(key, keep="last").sort_index()` for the kept rows, and
`df.drop(kept.index)` for the removed ones (works when the index labels are unique).
