## Hint 1

`groupby` accepts a list of keys. One key can be a column name, the other a `pd.Grouper` that says "use this date
column, cut into these bins". Which `key=` and `freq=` do you need?

## Hint 2

```text
g = orders.groupby(["store_id", pd.Grouper(key="order_date", freq="ME")])["revenue"].sum()
out = g.reset_index().rename(columns={"order_date": "month"})
sort by store_id, month; reset the index
```
