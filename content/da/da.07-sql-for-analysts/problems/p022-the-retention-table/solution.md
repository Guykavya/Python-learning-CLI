## Approach

De-duplicate to the grain of the question (user and month) *before* counting, count distinct users per cohort and month number, and divide by the cohort size taken from `users`. Both `cohort` and `m` are first days of months, so `date_diff('month', ...)` is exact (it counts month boundaries, which is what we want here).

## Code

```python
QUERY = """
WITH cohort AS (
  SELECT user_id, date_trunc('month', signup_at)::DATE AS cohort FROM users
),
size AS (
  SELECT cohort, count(*) AS cohort_size FROM cohort GROUP BY 1
),
activity AS (
  SELECT DISTINCT user_id, date_trunc('month', event_time)::DATE AS m
  FROM events WHERE event_type = 'login' AND event_time < TIMESTAMP '2025-07-01'
),
counts AS (
  SELECT c.cohort, date_diff('month', c.cohort, a.m) AS month_number, count(DISTINCT c.user_id) AS active_users
  FROM cohort c JOIN activity a USING (user_id)
  GROUP BY 1, 2
)
SELECT cohort, month_number, active_users, cohort_size, active_users * 1.0 / cohort_size AS retention
FROM counts JOIN size USING (cohort)
"""
```

## Complexity

O(events + users).

## Another way

Pivot the long form into the familiar triangle with conditional aggregation (`max(retention) FILTER (WHERE month_number = 1)`) or DuckDB's `PIVOT`. Keep the long form for storing and charting, the matrix for reading. Month 0 is 100% by construction when the sign-up counts as a login.

## Pitfall to remember

This long form has **no row** for a month in which nobody was active; the next problem builds a full grid in which such cells are 0 when observed and `NULL` when the month is not complete yet.
