## Approach

`AVG(amount) OVER (ORDER BY day ROWS BETWEEN 2 PRECEDING AND CURRENT ROW)` slides a window of up to three rows. `AVG` divides by the rows really in the frame, so the first two rows average fewer values.

## Code

```python
QUERY = """
SELECT day, amount,
       ROUND(AVG(amount) OVER (ORDER BY day ROWS BETWEEN 2 PRECEDING AND CURRENT ROW), 2) AS ma3
FROM daily
ORDER BY day
"""
```

## Complexity

After sorting, the engine keeps a running sum, so it is O(n) for the pass (O(n log n) with the sort).

## Another way / portable SQL

Self join: `JOIN daily d2 ON d2.day BETWEEN d1.day - 2 AND d1.day` then `GROUP BY d1.day` and `AVG(d2.amount)`. That is O(n * window) and is the way to do it where windows are missing (MySQL before 8). The `ROWS BETWEEN` form is standard in PostgreSQL and MySQL 8.
Use `RANGE` or `GROUPS` frames when "three days" means calendar distance rather than three rows.
