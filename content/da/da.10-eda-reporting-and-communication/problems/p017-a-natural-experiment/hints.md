## Hint 1

You need four rates: plan x period. Which column marks the period? With the four numbers, the formula is one line. Which plan is the control when you are only told the treated one?

## Hint 2

```text
plans = sorted(df["plan"].unique()); check len == 2 and treated in plans
control = the other plan
after = df["week"] >= pd.Timestamp(change_date)
rate(plan, period) = df[(plan) & (period)]["churn_now"].mean() * 100
did = (rate(t, after) - rate(t, before)) - (rate(c, after) - rate(c, before))
```
