## Approach

An as-of join needs both tables sorted by their time key, so sort copies first (`sort_values` returns new frames; the
inputs are untouched). `by="product_id"` repeats the match inside each product, and `direction="backward"` (the
default) takes the latest price on or before the order date. Rows with no earlier price get `NaN`. Finally drop the
helper column `effective` and put the rows back in `order_id` order.

## Code

```python
import pandas as pd


def price_at_order(orders, price_history):
    left = orders.sort_values("order_date")
    right = price_history.sort_values("effective")
    out = pd.merge_asof(left, right, left_on="order_date", right_on="effective",
                        by="product_id", direction="backward")
    assert len(out) == len(orders), "an as-of join keeps every left row"
    return out.drop(columns="effective").sort_values("order_id").reset_index(drop=True)
```

## Complexity

O(n log n + m log m) for the two sorts; the as-of matching itself is one pass over both sorted tables.

## Another way

A plain merge on `product_id` followed by a filter `effective <= order_date` and keeping the latest row per order also
works, but it first builds every (order, price) pair of a product, which grows quickly. Add
`tolerance=pd.Timedelta("90D")` to `merge_asof` if a price older than 90 days should count as unknown.
