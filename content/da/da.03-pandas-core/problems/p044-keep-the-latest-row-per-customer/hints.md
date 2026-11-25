## Hint 1

`drop_duplicates(subset="customer", keep="last")` keeps the **last** row of each customer *as the table is currently ordered* (section 14.4). So what order must the table have before you call it? Think: which row must come last for each customer, and how do you break a tie in `ts`?

## Hint 2

```text
ordered = df.sort_values(["ts", "row_id"])               # oldest first; ties: smaller row_id first
latest  = ordered.drop_duplicates(subset="customer", keep="last")    # last = newest (and larger row_id)
latest  = latest.sort_values("customer").reset_index(drop=True)
removed = len(df) - len(latest)
```
