## Hint 1

Which table has one row per month, even for months without orders? How do you generate it from the smallest and largest order month, and how do you get a 0 into the empty months? Then, once each month has exactly one row, which function brings the previous month onto the row, and what protects the percentage from a zero denominator?

## Hint 2

```text
cal : generate_series(first_month, last_month, INTERVAL 1 MONTH)
rev : SELECT date_trunc('month', order_time)::DATE AS month, sum(amount) AS revenue FROM orders GROUP BY 1
m   : cal LEFT JOIN rev, COALESCE(revenue, 0)
final: lag(revenue) OVER (ORDER BY month) AS prev_revenue ;  change = revenue - prev ;  pct = change * 100.0 / NULLIF(prev, 0)
```
