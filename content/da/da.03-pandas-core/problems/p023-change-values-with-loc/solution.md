## Approach

Copy first so the caller's frame stays as it was. Build a True/False mask for the rows to change, then use one `loc[mask, column] = new_values`. The right side is computed from the same selected rows, so it has the same labels and the assignment lines up. In pandas 3 (Copy-on-Write) the copy is cheap: data is physically copied only when you change it.

## Code

```python
import pandas as pd


def apply_discount(df, category, pct):
    out = df.copy()
    rows = out["category"] == category
    out.loc[rows, "price"] = out.loc[rows, "price"] * (1 - pct / 100)
    return out
```

## Complexity

O(n) for the mask and for the copy of one column.

## Another way

`df.assign(price=df["price"].mask(df["category"] == category, df["price"] * (1 - pct / 100)))` returns a new frame without any in-place step. Or `out["price"] = out["price"] * factor` where `factor` is a Series made with `np.where` (da.02).

## Note

The starter edits `df` in place and returns the same object. With a plain function call the caller's frame changes too: assignment through `loc` on a frame you were given is a change to the caller's data.
