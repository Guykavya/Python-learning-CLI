## Approach

Split by the keys, sum `revenue` in each group, combine. `groupby` sorts the groups by key by default, so the order
comes for free. `as_index=False` puts the keys back as ordinary columns and gives a `RangeIndex`, which is what a
report or a later merge wants. A string key and a one-element list give the same table.

## Code

```python
import pandas as pd


def revenue_by(lines, keys):
    if isinstance(keys, str):
        keys = [keys]
    return lines.groupby(keys, as_index=False)["revenue"].sum()
```

## Complexity

O(n) to hash the keys plus O(g log g) to sort g groups. The input is only read.

## Another way

`lines.groupby(keys)["revenue"].sum().reset_index()` gives the same flat frame: `reset_index()` moves every index level
back into columns. Use it when you already have a grouped Series and decide later that you want columns.
