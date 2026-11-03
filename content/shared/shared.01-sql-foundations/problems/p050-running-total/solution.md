## Approach

`SUM(...) OVER (PARTITION BY store ORDER BY day)`: the partition splits rows into one group per store, the `ORDER BY` puts each
group in date order, and the default frame (`RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW`) adds everything up to the current row.

## Code

```python
QUERY = """
SELECT store, day, amount,
       SUM(amount) OVER (PARTITION BY store ORDER BY day) AS running
FROM daily_sales
ORDER BY store, day
"""
```

## Complexity

One sort by (store, day), then one pass: O(n log n). Each row keeps its place; no rows are collapsed.

## Another way / portable SQL

Spell the frame out to be safe with ties: `SUM(amount) OVER (PARTITION BY store ORDER BY day ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)`.
Portable to PostgreSQL and MySQL 8. Without windows you would use a self join (`d2.day <= d1.day`) and `GROUP BY`, which is O(n^2).
