## Hint 1

Three filters before any KPI: rows up to `as_of`, departures up to `as_of`, months up to the last complete one. Which pandas method replaces values by `NaT` where a condition is false?

## Hint 2

```text
as_of = pd.Timestamp(as_of)
pnl = panel[panel["week"] <= as_of]
cus = customers.assign(last_week=customers["last_week"].where(customers["last_week"] <= as_of))
last_month = as_of.to_period("M") - 1
k = monthly_kpis(cus, pnl[pnl["week"].dt.to_period("M") <= last_month])
row = k.iloc[-1]
```
