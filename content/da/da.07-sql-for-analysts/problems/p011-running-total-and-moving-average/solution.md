## Approach

Build the calendar from the first to the last order date, left join the daily revenue and fill the gaps with 0, and only then apply the windows. Since one row is now one day, `ROWS BETWEEN 6 PRECEDING AND CURRENT ROW` means exactly "the last 7 days". At the start the frame is shorter and `avg` averages the rows that exist.

## Code

```python
QUERY = """
WITH bounds AS (
  SELECT min(order_time)::DATE AS first_day, max(order_time)::DATE AS last_day FROM orders
),
cal AS (
  SELECT CAST(d AS DATE) AS day
  FROM bounds, generate_series(first_day, last_day, INTERVAL 1 DAY) AS t(d)
),
rev AS (
  SELECT order_time::DATE AS day, sum(amount) AS revenue FROM orders GROUP BY 1
),
filled AS (
  SELECT c.day, COALESCE(r.revenue, 0) AS revenue FROM cal c LEFT JOIN rev r USING (day)
)
SELECT day, revenue,
       sum(revenue) OVER (ORDER BY day) AS running_total,
       avg(revenue) OVER (ORDER BY day ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS avg_7
FROM filled
"""
```

## Complexity

O(days + orders).

## Another way

Without a calendar you can use `RANGE BETWEEN INTERVAL 6 DAYS PRECEDING AND CURRENT ROW` on the date, but `avg` would then ignore empty days instead of counting them as zero: a different definition. For revenue an empty day *is* a zero; for "average order value" it is not.
