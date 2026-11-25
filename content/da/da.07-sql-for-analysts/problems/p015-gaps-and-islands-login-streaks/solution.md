## Approach

After `DISTINCT`, each row is a login day. `day - row_number()` (a date minus an integer is a date in DuckDB) is the same for all days of one run: for the days 1, 2, 3 with numbers 1, 2, 3 the result is Dec 31 each time; after the gap, 5 with number 4 gives Jan 1, a new value. Group by that value to get the length of every run, then take the longest per user.

## Code

```python
QUERY = """
WITH d AS (
  SELECT DISTINCT user_id, event_time::DATE AS day FROM events WHERE event_type = 'login'
),
n AS (
  SELECT user_id, day, day - CAST(row_number() OVER (PARTITION BY user_id ORDER BY day) AS INTEGER) AS island
  FROM d
),
streaks AS (
  SELECT user_id, island, count(*) AS days FROM n GROUP BY user_id, island
)
SELECT user_id, max(days) AS longest_streak FROM streaks GROUP BY user_id
"""
```

## Complexity

O(n log n) for the sort inside each user.

## Another way

`lag` plus a running sum (the sessions recipe of Ch. 4.9): flag a row as a new run when the gap to the previous day is not 1, then `sum(flag)` gives the run number. Same result; it generalises to "gap of at most 2 days" more easily.
