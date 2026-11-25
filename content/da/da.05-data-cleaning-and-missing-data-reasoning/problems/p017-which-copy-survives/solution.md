## Approach

The survivor rule is a **sort order**: first by how many cells are filled, then by `updated_at`, and (through a stable
sort) by position. With the best row last in each group, `drop_duplicates(keep="last")` picks it. The count must be taken
over the original columns, so compute it before you add the helper column. Using the sort only to *choose* the winners,
and then selecting them from the original frame, keeps the original order and labels.

## Code

```python
import pandas as pd


def best_copy(df, key):
    work = df.reset_index(drop=True)
    work["_filled"] = work.notna().sum(axis=1)
    order = work.sort_values(["_filled", "updated_at"], kind="stable")
    winners = order.drop_duplicates(subset=key, keep="last").index
    return df[work.index.isin(winners)].copy()
```

## Complexity

O(n log n) for the sort; counting the filled cells is O(n x c).

## Another way

A loop over the groups: for each key, pick `max(rows, key=lambda r: (r.filled, r.updated_at, r.position))`. It is easy to
believe and easy to test, but slow for many groups; the tests use it as the slow, obvious truth. Another rule is
**merge the copies**: `df.groupby(key).first()` takes the first non-missing value of each column. It can build a row
that never existed, so use it only when the copies describe the same facts at different times of knowing.
