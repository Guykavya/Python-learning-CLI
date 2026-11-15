## Approach

For three consecutive days 01, 02, 03 with row numbers 1, 2, 3, subtracting the row number as days gives 2023-12-31 for all three: the same group key. After the gap, 01-05 has row number 4, so the key is 2024-01-01, a different value. Group by that key and take `MIN`, `MAX`, `COUNT`.

## Code

```python
QUERY = """
WITH numbered AS (
  SELECT day, ROW_NUMBER() OVER (ORDER BY day) AS rn
  FROM activity
),
grouped AS (
  SELECT day, date(day, '-' || rn || ' days') AS grp
  FROM numbered
)
SELECT MIN(day) AS start_day, MAX(day) AS end_day, COUNT(*) AS days
FROM grouped
GROUP BY grp
ORDER BY start_day
"""
```

## Complexity

One window pass and one hash/sort group: O(n log n).

## Another way / portable SQL

Compare with the previous row using `LAG`: flag a row as a "new streak" if `julianday(day) - julianday(LAG(day) OVER (ORDER BY day)) <> 1`, then take a running `SUM` of the flags as the streak id.
In PostgreSQL you write `day - rn * INTERVAL '1 day'` (or `day - rn::int` for dates); MySQL uses `DATE_SUB(day, INTERVAL rn DAY)`.
