# Monthly KPIs

Chapter section 3.4. The FreshBox KPIs, defined in words before any code:

| KPI | Definition |
|---|---|
| `opening_actives` | customers with a panel row in the **first week present** in the month |
| `churned` | of the opening actives, those whose `last_week` falls in the month |
| `churn_rate_pct` | `churned / opening_actives * 100` |
| `on_time_pct` | share of **all** panel rows of the month with `late == False`, times 100 |
| `weekly_revenue_k` | sum of `price` per week, averaged over the weeks of the month, divided by 1,000 |

Write `monthly_kpis(customers, panel)`. `customers` has `customer_id` and `last_week` (empty `NaT` while the customer is active);
`panel` has `customer_id`, `week` (Monday timestamps), `late` (bool) and `price`. Return a DataFrame indexed by month (`Period`, freq `M`, sorted) with the five
columns above, in that order.

## Example

January 2024 with three customers active on 1 January, one of whom leaves in January: `opening_actives = 3`, `churned = 1`, `churn_rate_pct = 33.33...`.
A customer whose `last_week` is in **February** is not churned in January.
