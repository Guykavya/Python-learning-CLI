## Hint 1

Add a `month` column (`week.dt.to_period("M")`). Which week is the "first week present" of each month? Keep only the panel rows of those weeks: they are the opening actives. Then attach `last_week` to them.

## Hint 2

```text
p = panel with month
first = p.groupby("month")["week"].min()
opening = p[p["week"].isin(first.values)][["customer_id", "month"]] merged with customers[["customer_id", "last_week"]]
opening["churned"] = opening["last_week"].dt.to_period("M") == opening["month"]
out = opening.groupby("month").agg(opening_actives=(..., "size"), churned=("churned", "sum"))
on_time: (1 - p.groupby("month")["late"].mean()) * 100
revenue: p.groupby(["month", "week"])["price"].sum().groupby("month").mean() / 1000
```
