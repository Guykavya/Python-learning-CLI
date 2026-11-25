## Hint 1

A running total adds the rows **in the order they stand**. What order must the rows be in before you add them up?
And which groupby method adds up "so far" while restarting at every customer?

## Hint 2

```text
out = orders.sort_values(["customer_id", "order_date", "order_id"], ignore_index=True)   # a new frame
out["running_spend"] = out.groupby("customer_id")["amount"].cumsum()
return out
```
