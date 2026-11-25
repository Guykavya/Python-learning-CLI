## Approach

`transform("min")` gives each order the date of its customer's first order, keeping one row per order. Comparing its
month with the order's month labels every order `new` or `repeat`. Then it is an ordinary two-key aggregation:
distinct customers and summed revenue per month and kind, spread with `unstack` so `new` and `repeat` become columns.
`reindex(columns=...)` guarantees both columns even when, say, the data have no repeat customer at all; `fill_value=0`
turns an empty group into 0. Counting **distinct** customers (`nunique`) matters: a customer with two orders in a month
is one customer.

## Code

```python
import pandas as pd


def new_vs_repeat(orders):
    month = orders["order_date"].dt.to_period("M")
    first = orders.groupby("customer_id")["order_date"].transform("min").dt.to_period("M")
    d = orders.assign(month=month.astype(str), kind=(month == first).map({True: "new", False: "repeat"}))
    g = d.groupby(["month", "kind"])
    cust = g["customer_id"].nunique().unstack("kind", fill_value=0).reindex(columns=["new", "repeat"], fill_value=0)
    rev = g["revenue"].sum().unstack("kind", fill_value=0.0).reindex(columns=["new", "repeat"], fill_value=0.0)
    return pd.DataFrame({
        "month": cust.index.to_list(),
        "new_customers": cust["new"].astype("int64").to_numpy(),
        "repeat_customers": cust["repeat"].astype("int64").to_numpy(),
        "new_revenue": rev["new"].astype("float64").to_numpy(),
        "repeat_revenue": rev["repeat"].astype("float64").to_numpy(),
    })
```

## Complexity

O(n log n) for the groupbys (they sort their keys); everything else is linear.

## Another way

Rank the orders per customer by date with `cumcount` as in chapter 15.8, merge the first-order month back with
`safe_merge`, or use `pivot_table(index="month", columns="kind", values="revenue", aggfunc="sum", fill_value=0)` for the
revenue part. A cohort table (rows = first month, columns = order month) is the natural next step.
