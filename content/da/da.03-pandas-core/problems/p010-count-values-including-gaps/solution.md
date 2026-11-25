## Approach

Replace the missing values by the label `"(missing)"` and count. (Another route is `value_counts(dropna=False)`, which gives a `NaN` label that you then rename.) Build the frame, divide by `len(s)` (not by the number of non-missing values, so the shares add up to 1), then sort by two keys: `count` descending and `label` ascending. `value_counts` already sorts by count, but the order of ties is not promised, so the explicit sort matters.

## Code

```python
import pandas as pd


def category_counts(s):
    labels = s.astype("object").where(s.notna(), "(missing)")
    counts = labels.value_counts()
    out = pd.DataFrame({"label": counts.index.astype(str), "count": counts.to_numpy()})
    out["share"] = out["count"] / len(s)
    out = out.sort_values(["count", "label"], ascending=[False, True])
    return out.reset_index(drop=True)
```

## Complexity

O(n + k log k) for n values and k distinct labels.

## Another way

`s.value_counts(dropna=False, normalize=True)` gives the shares directly, with `NaN` as a label. Check what it does with ties before relying on its order.
