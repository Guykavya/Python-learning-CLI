## Hint 1

If you number the days 1, 2, 3, ... in date order and subtract that number of days from each date, what happens to the result for days that are consecutive? And for the day after a gap?

## Hint 2

```
WITH numbered AS (
  SELECT day, ROW_NUMBER() OVER (ORDER BY day) AS rn FROM activity
),
grouped AS (
  SELECT day, date(day, '-' || rn || ' days') AS grp FROM numbered
)
SELECT MIN(day), MAX(day), COUNT(*) FROM grouped GROUP BY grp ORDER BY ...
```
