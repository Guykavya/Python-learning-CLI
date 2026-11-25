# A natural experiment

Chapter section 5.4. On 7 October the price of the **3-meal** plan went up; the **2-meal** plan stayed the same. The 2-meal plan is a comparison group that lived through everything
else (the delivery problem, the season). The **difference in differences** removes what hit both plans:

```text
DiD = (treated after - treated before) - (control after - control before)
```

Write `price_change_effect(df, change_date, treated)`. `df` has one row per customer-week with `week` (timestamp), `plan` and `churn_now` (bool). Rates are the share of rows
with `churn_now`, in **percent**. A week on or after `change_date` is "after". `treated` is the plan whose price changed; the **other** plan is the control.

- Return the DiD in percentage points as a float.
- `df` must contain exactly two plans and `treated` must be one of them; otherwise raise `ValueError("need exactly two plans, one of them treated")`.

## Example

Control (2-meal): 2% before, 3% after. Treated (3-meal): 2% before, 5% after. Both rose, but the treated plan by 2 points more: `DiD = +2.0`.
