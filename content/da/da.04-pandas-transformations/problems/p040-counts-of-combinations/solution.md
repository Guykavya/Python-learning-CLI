## Approach

`crosstab` is the frequency table of two columns: it groups by both, counts and spreads the second key into columns,
with 0 for pairs that never occur. `normalize="index"` divides each row by its total, which answers "of each region's
orders, how many are online?". `"columns"` would answer a different question (of all online orders, which region
are they from?).

## Code

```python
import pandas as pd


def channel_by_region(orders):
    counts = pd.crosstab(orders["region"], orders["channel"])
    shares = pd.crosstab(orders["region"], orders["channel"], normalize="index")
    return counts, shares
```

## Complexity

O(n) to count the pairs, plus the size of the table.

## Another way

`orders.groupby(["region", "channel"]).size().unstack(fill_value=0)` gives `counts`, and
`counts.div(counts.sum(axis=1), axis=0)` gives `shares`. `crosstab` does both in one readable call.
