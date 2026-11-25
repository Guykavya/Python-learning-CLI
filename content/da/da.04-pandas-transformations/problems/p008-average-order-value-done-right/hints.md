## Hint 1

On the test data, S1 has four orders of 100, S2 one order of 600 and S3 two orders of 200. What is the total revenue,
and how many orders are there? Compare that answer with the mean of 100, 600 and 200. Which store "counts" too much in
the second number?

## Hint 2

```text
revenue per line = qty * unit_price
overall  = revenue.sum() / order_id.nunique()        -> float(...)
by_store = lines.assign(revenue=...).groupby("store_id", as_index=False)
                .agg(revenue=("revenue", "sum"), orders=("order_id", "nunique"))
by_store["aov"] = by_store["revenue"] / by_store["orders"]
```
