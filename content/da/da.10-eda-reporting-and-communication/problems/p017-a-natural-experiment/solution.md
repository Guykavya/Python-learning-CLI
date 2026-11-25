## Approach

The change in the control plan estimates what would have happened to the treated plan without the price change (the **parallel trends** assumption). Subtracting it removes the delivery problem, the season and anything else that hit both.

## Code

```python
import pandas as pd


def price_change_effect(df, change_date, treated):
    plans = sorted(df["plan"].unique())
    if len(plans) != 2 or treated not in plans:
        raise ValueError("need exactly two plans, one of them treated")
    control = plans[0] if plans[1] == treated else plans[1]
    after = df["week"] >= pd.Timestamp(change_date)

    def rate(plan, period):
        return df.loc[(df["plan"] == plan) & period, "churn_now"].mean() * 100

    return float((rate(treated, after) - rate(treated, ~after)) - (rate(control, after) - rate(control, ~after)))
```

## Complexity

O(n).

## Another way

A regression `churn ~ treated + after + treated:after` gives the same number as the interaction coefficient, plus a standard error.
