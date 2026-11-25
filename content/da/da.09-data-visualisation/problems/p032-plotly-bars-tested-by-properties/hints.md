## Hint 1

First add up the revenue per store and sort ascending. Which `px.bar` arguments choose the orientation, the title and the axis labels?

## Hint 2

```text
d = df.groupby("store", as_index=False)["revenue"].sum().sort_values("revenue")
fig = px.bar(d, x="revenue", y="store", orientation="h", title="Revenue by store",
             labels={"revenue": "Revenue (USD)", "store": "Store"})
```
