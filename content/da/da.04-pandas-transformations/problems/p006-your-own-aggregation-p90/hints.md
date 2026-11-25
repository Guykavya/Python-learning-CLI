## Hint 1

What does your `p90` function receive: the whole table, or one group's `delivery_days` column? Which Series method
gives a percentile? Which counting method skips missing values?

## Hint 2

```text
def p90(s): return s.quantile(0.9)

orders.groupby("region", as_index=False).agg(
    delivered   = ("delivery_days", "count"),
    median_days = ("delivery_days", "median"),
    p90_days    = ("delivery_days", p90),      # the function itself, no quotes, no ()
)
```
