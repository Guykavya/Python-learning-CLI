## Approach

`LAG(revenue) OVER (ORDER BY month)` is the previous month's revenue. Subtracting it from the current one gives the change; the first row has no previous row, so `LAG` gives `NULL` and so does the subtraction.

## Code

```python
QUERY = """
SELECT month, revenue,
       revenue - LAG(revenue) OVER (ORDER BY month) AS change
FROM monthly_sales
ORDER BY month
"""
```

## Complexity

One sort by month and one pass: O(n log n); O(n) if the data is already indexed by month.

## Another way / portable SQL

Self join: `FROM monthly_sales a LEFT JOIN monthly_sales b ON b.month = date(a.month || '-01', '-1 month')` (SQLite date arithmetic). That also handles
*missing* months correctly (the change would be NULL after a gap), which `LAG` does not: `LAG` just takes the previous row. `LAG` is standard in PostgreSQL and MySQL 8.
