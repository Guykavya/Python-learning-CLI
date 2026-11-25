## Approach

The categories are the full list of allowed values; `observed=False` tells `groupby` to make a group for each of them,
even when no row has it, and `size()` gives 0 there. Missing sizes are not a category, so they are not counted.
`reset_index(name="orders")` turns the counts into the two columns.

## Code

```python
import pandas as pd


def orders_per_size(df):
    counts = df.groupby("size", observed=False).size()
    return counts.reset_index(name="orders")
```

## Complexity

O(n + k) for n lines and k categories.

## Another way

`df["size"].value_counts(sort=False)` also lists every category (section 10.3) in category order. Or count with the
default `groupby` and then `reindex(df["size"].cat.categories, fill_value=0)`: the explicit list makes the intention
visible and also works for a plain text column, given the full list of sizes.
