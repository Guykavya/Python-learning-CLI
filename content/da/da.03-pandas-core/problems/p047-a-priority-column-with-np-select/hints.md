## Hint 1

`np.select(conditions, values, default=...)` checks the conditions **in the order given** and uses the value of the first one that is true (section 15.3). Write each rule as a boolean column. How do you say "vip **and** overdue" for whole columns (not `and`)?

## Hint 2

```text
conditions = [overdue_days > 30,
              vip & (overdue_days > 0),
              amount >= 5000]
values     = ["urgent", "high", "medium"]
np.select(conditions, values, default="low")
```
Wrap the result in `pd.Series(..., index=df.index, name="priority")`, because `np.select` returns a bare array.
