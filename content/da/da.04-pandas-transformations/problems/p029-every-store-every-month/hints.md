## Hint 1

Which rows must the result have, whatever was sold? Where do they come from: the sales table, or the store list and
the month list? Which `how=` pairs every row of one table with every row of another? After that, which join keeps every
grid cell?

## Hint 2

```text
grid = stores[["store_id"]].merge(pd.DataFrame({"month": months}), how="cross")     # stores x months rows
out  = grid.merge(sales[["store_id", "month", "revenue"]], on=["store_id", "month"], how="left", validate="1:1")
out["revenue"] = out["revenue"].fillna(0.0)
sort by store_id, month; reset the index
```
