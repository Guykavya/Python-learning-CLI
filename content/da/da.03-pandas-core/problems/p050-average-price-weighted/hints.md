## Hint 1

Three of the four numbers are one-liners (section 16.2). For the average price, think about what a price "weighs": a price that was used for 10 units should count ten times. What do you get if you divide the **total revenue** by the **total units**?

## Hint 2

```text
revenue = (df.qty * df.unit_price).sum()
units   = df.qty.sum()
avg     = revenue / units        # weighted by quantity; guard units == 0
return {"orders": len(df), "units": units, "revenue": revenue, "avg_price": avg}
```
Convert to plain Python numbers with `int(...)` and `float(...)`, and return `None` for `avg_price` when `units` is 0.
