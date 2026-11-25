## Hint 1

How do you bring each event's customer's `predict_day` next to it? After that the condition is one comparison per row.

## Hint 2

```text
m = events.merge(customers, on="customer_id")
counts = m[m["day"] < m["predict_day"]].groupby("customer_id").size()
return counts.reindex(customers["customer_id"], fill_value=0).astype(int).rename("events_before")
```
