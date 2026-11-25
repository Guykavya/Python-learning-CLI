## Approach

Leakage happens when anything after `as_of` can reach the numbers. The three filters remove future rows, future departures and the incomplete month. Then the KPI function is the same one the full report uses.

## Code

```python
def quick_summary(customers, panel, as_of):
    as_of = pd.Timestamp(as_of)
    pnl = panel[panel["week"] <= as_of]
    cus = customers.assign(last_week=customers["last_week"].where(customers["last_week"] <= as_of))
    last_month = as_of.to_period("M") - 1
    k = monthly_kpis(cus, pnl[pnl["week"].dt.to_period("M") <= last_month])
    row = k.iloc[-1]
    return {"as_of": str(as_of.date()), "last_month": str(k.index[-1]), "months": int(len(k)),
            "opening_last": int(row["opening_actives"]), "churn_last": float(row["churn_rate_pct"]),
            "on_time_last": float(row["on_time_pct"])}
```

(`monthly_kpis` from the starter stays above it.)

## Complexity

O(n log n) for the KPI table.

## Another way

Keep a dated snapshot of the input files each month and run the report on the snapshot: nothing later can leak, at the cost of storing the snapshots.
