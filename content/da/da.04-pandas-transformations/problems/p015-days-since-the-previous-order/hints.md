## Hint 1

"The previous order" only makes sense after sorting by date inside each customer. Which groupby method subtracts the
previous row of the same group? What type is the difference of two dates, and which accessor turns it into a number of
days?

## Hint 2

```text
out = orders.sort_values(["customer_id", "order_date", "order_id"], ignore_index=True)
gap = out.groupby("customer_id")["order_date"].diff()      # Timedelta, NaT for first orders
out["days_since_prev"] = gap.dt.days                         # float, NaN stays NaN
```
