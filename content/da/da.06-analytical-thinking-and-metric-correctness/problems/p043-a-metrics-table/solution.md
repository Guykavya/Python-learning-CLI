## Approach

The point of a `MetricSpec` is that the table-building code knows nothing about any single metric: each definition
brings its own function, and the table calls them all the same way, for every month. Build a list of dict rows in a
double loop (metrics outside, months inside), then make the DataFrame once, with explicit columns so the order is fixed
even when the list is empty. Convert the period texts to Timestamps at the border, as the chapter does. A `None`
denominator becomes `NaN`, "not applicable" for counts.

## Code

```python
import pandas as pd


def metrics_table(ctx, specs, months):
    rows = []
    for spec in specs:
        for label, (start, end) in months.items():
            value, numerator, denominator = spec.fn(ctx, pd.Timestamp(start), pd.Timestamp(end))
            rows.append({"metric": spec.name, "month": label, "unit": spec.unit, "numerator": numerator,
                         "denominator": float("nan") if denominator is None else denominator, "value": value})
    return pd.DataFrame(rows, columns=["metric", "month", "unit", "numerator", "denominator", "value"])
```

## Complexity

O(S x M) calls of the metric functions (S specs, M months); each call is O(n) in the table size.

## Another way

The chapter formats each cell as text (`89.3%  (799/895)`) and makes one column per month. A long table with one
row per metric and month (as here) is better for further work (filter, plot, compare with SQL); the pretty wide table
is one `pivot` and one formatting step away. A second engine (SQL) should reproduce the numerator column.
