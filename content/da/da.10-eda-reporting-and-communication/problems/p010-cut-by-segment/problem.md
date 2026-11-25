# Cut by segment

Chapter section 4.4. After the time profile, cut the change by segment: for each segment, its **share** of the base and its **churn rate** before and after.
`o` has one row per customer-month (the opening actives) with a `month` column (`Period`, freq `M`), a boolean `churned` column and segment columns such as `channel`.

Write `segment_table(o, dim, before, after)`. `before` and `after` are pairs of month strings, inclusive: `("2024-04", "2024-08")`.

- For each period: the share of the period's rows in each segment (in percent, out of **all** rows of the period) and the churn rate of each segment (percent).
- Keep only segments that appear in **both** periods (no NaN in the result).
- Columns, in this order: `before share %`, `after share %`, `before churn %`, `after churn %`, `change (points)` (after churn minus before churn).
- Index: the segment values (index name = `dim`), sorted by `change (points)`, **largest first**.

## Example

Before: 4 paid rows (1 churned) and 6 organic rows (0 churned). After: 5 paid (2 churned) and 5 organic (1 churned).
Paid: shares 40% and 50%, churn 25% to 40%, change +15. Organic: 60% and 50%, 0% to 20%, +20. Organic comes first.
