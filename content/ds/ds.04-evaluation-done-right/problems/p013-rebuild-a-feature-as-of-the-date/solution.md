## Approach

Join each event to its customer's cut-off, keep only events strictly before it, count per customer, and fill customers with no events with 0.

## Code

```python
import pandas as pd


def as_of_feature(events, customers):
    m = events.merge(customers[["customer_id", "predict_day"]], on="customer_id", how="inner")
    counts = m[m["day"] < m["predict_day"]].groupby("customer_id").size()
    out = counts.reindex(customers["customer_id"], fill_value=0).astype(int)
    out.name = "events_before"
    return out
```

## Complexity

O(n_events + n_customers) for the join and the count.

## Another way

`pd.merge_asof` handles "the latest value before a date" for slowly changing attributes; for counts the filter-and-group shown here is clearer.
