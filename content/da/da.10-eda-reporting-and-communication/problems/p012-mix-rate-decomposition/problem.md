# Mix-rate decomposition

Chapter section 4.5. Turn the hand calculation of problem 11 into a function on data. `o` has one row per customer-month with `month` (`Period`), a boolean `churned`
and segment columns.

Write `mix_rate_decomposition(o, dim, before, after)` (periods are inclusive pairs of month strings, as in problem 10). It returns `(mix, rate, total)` in
**percentage points**:

```text
share = rows of the segment / rows of the period;  rate = churn rate of the segment in the period
mix   = sum over segments of (share after - share before) x (rate before + rate after) / 2
rate  = sum over segments of (rate after - rate before)   x (share before + share after) / 2
total = overall churn rate after - overall churn rate before
```

All three as plain floats times 100. Every segment must appear in **both** periods; otherwise raise `ValueError` with the text `segment missing in one period: <name>`.

## Example

Before: 200 new customers (20 churned) and 800 old (24). After: 100 new (15) and 900 old (45). This is problem 11's data: `(-0.85, 2.45, 1.60)`.
