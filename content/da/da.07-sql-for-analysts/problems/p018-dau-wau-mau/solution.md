## Approach

Join each calendar day to every login day in the 30 days that end on it (a *range join*), then compute three distinct counts on the same joined rows, each restricted by `FILTER`. Distinct counts guarantee that a user seen on several days of the window counts once. The `LEFT JOIN` keeps days whose 30-day window is empty.

## Code

```python
QUERY = """
WITH l AS (
  SELECT DISTINCT user_id, event_time::DATE AS day FROM events WHERE event_type = 'login'
),
bounds AS (SELECT min(day) AS d0, max(day) AS d1 FROM l),
cal AS (
  SELECT CAST(d AS DATE) AS day FROM bounds, generate_series(d0, d1, INTERVAL 1 DAY) AS t(d)
)
SELECT c.day,
       count(DISTINCT l.user_id) FILTER (WHERE l.day = c.day)     AS dau,
       count(DISTINCT l.user_id) FILTER (WHERE l.day > c.day - 7) AS wau,
       count(DISTINCT l.user_id)                                   AS mau
FROM cal c LEFT JOIN l ON l.day BETWEEN c.day - 29 AND c.day
GROUP BY c.day
"""
```

## Complexity

The range join creates up to 30 rows per login day: O(days x 30 x users per day). Fine for analysis; for very large tables, precompute a "last seen" table instead.

## Another way

Window functions cannot do this: `count(DISTINCT ...) OVER (... RANGE ...)` is not supported for rolling distincts, which is why we join. Another approach is to store for each user the set of active days and test membership, which is what the `FILTER` clauses do.

## Pitfall to remember

DAU + DAU + ... is not WAU. A user who logs in every day is counted 7 times in the sum and once in the WAU (Ch. 5.2, problem 20).
