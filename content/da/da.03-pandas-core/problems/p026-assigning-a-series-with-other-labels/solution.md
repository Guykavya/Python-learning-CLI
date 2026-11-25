## Approach

Assignment `df[col] = series` aligns **by index label**, so the customer ids in `targets.index` were compared with the row labels `0, 1, 2...` of `df`. Where they coincide by accident you get a target of the wrong customer; where not, `NaN`. `Series.map(other_series)` instead looks each **value** of the id column up in the *index* of `other_series`, which is the join you meant. Absent ids give a missing value. To count the rows that had no entry, ask `isin(targets.index)` rather than looking for `NaN`, since a present customer may also have a missing target.

## Code

```python
import pandas as pd


def attach_targets(df, targets):
    out = df.copy()
    out["target"] = out["customer_id"].map(targets)
    n_missing = int((~out["customer_id"].isin(targets.index)).sum())
    return out, n_missing
```

## Complexity

O(n) with a hash lookup per row.

## Another way

`df.merge(targets.rename("target"), left_on="customer_id", right_index=True, how="left")` does the same as a join (da.04); it does not keep the row labels the same way, so check the index. Alternatively `out["customer_id"].map(targets.to_dict())` with a plain dict.

## Note

The measured starter result, `[80.0, nan, 50.0, nan]` for the example, is the lesson: each target landed on the row **numbered** like the customer id (row 0 got customer 0's target 80 although it belongs to customer 2).
