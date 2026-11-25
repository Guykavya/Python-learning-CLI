## Hint 1

How many rows does the daily revenue table have, compared with the number of calendar days? What do you need before the window function so that one row is one day? And which frame gives "this row and the 6 before it"?

## Hint 2

```text
cal   : SELECT d::DATE AS day FROM generate_series(min_day, max_day, INTERVAL 1 DAY) AS t(d)
rev   : SELECT order_time::DATE AS day, sum(amount) AS revenue FROM orders GROUP BY 1
filled: cal LEFT JOIN rev, COALESCE(revenue, 0)
final : sum(revenue) OVER (ORDER BY day)                       -- running total
        avg(revenue) OVER (ORDER BY day ROWS BETWEEN 6 PRECEDING AND CURRENT ROW)
```

Take the first and last day from `orders` with `min(order_time)::DATE` and `max(order_time)::DATE`.
