## Approach

A custom aggregation is a function from one group's column (a Series) to one value. `quantile(0.9)` already skips
missing values and interpolates linearly, so `p90` is one line. The named function shows up by name in error messages,
which a `lambda` does not. `count` (not `size`) gives the number of known values.

## Code

```python
import pandas as pd


def p90(s):
    return s.quantile(0.9)


def p90_delivery_days(orders):
    return orders.groupby("region", as_index=False).agg(
        delivered=("delivery_days", "count"),
        median_days=("delivery_days", "median"),
        p90_days=("delivery_days", p90),
    )
```

## Complexity

O(n log n) at most: each group's values are partly sorted to find the percentile. The custom function is called once
per group in Python, which is fine for a handful of regions (Ch. 3.3, 12.2).

## Another way

Without a custom function: `orders.groupby("region")["delivery_days"].quantile(0.9)` is a built-in, faster for many
groups. Then join it with the counts and medians. The custom form is the general pattern for statistics pandas does
not have.
