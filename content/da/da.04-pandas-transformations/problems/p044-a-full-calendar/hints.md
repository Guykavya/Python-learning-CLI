## Hint 1

First add up the revenue per day. Then build the list of **every** day you want with `pd.date_range(start, end)`.
Which method puts a Series onto a new set of labels and lets you choose the value for labels it did not have?

## Hint 2

```text
per_day = orders.groupby("order_date")["revenue"].sum()
days    = pd.date_range(start, end, freq="D")
full    = per_day.reindex(days, fill_value=0.0)          (days outside the range disappear here)
return full.rename_axis("date").reset_index(name="revenue")
```
