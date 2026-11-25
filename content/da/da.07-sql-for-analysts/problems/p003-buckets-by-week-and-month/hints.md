## Hint 1

Write the weekly count on its own first: what do you group by? Then the monthly count: the same query with another unit. How do you stack two result tables that have the same columns, and how do you put the word `week` or `month` into each?

## Hint 2

```text
SELECT 'week'  AS period, date_trunc('week',  signup_at)::DATE AS period_start, count(*) AS signups FROM users GROUP BY 2
UNION ALL
SELECT 'month' AS period, date_trunc('month', signup_at)::DATE AS period_start, count(*) AS signups FROM users GROUP BY 2
```

`::DATE` turns the timestamp that `date_trunc` returns into a plain date.
