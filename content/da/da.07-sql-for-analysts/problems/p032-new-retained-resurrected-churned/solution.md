## Approach

Two parts glued with `UNION ALL`. The active states come from `lag` over each user's active months: no previous month means `new`; a previous month exactly one month earlier means `retained`; any older previous month means `resurrected`. The churned rows are derived from the *active* rows: for each active month, the next month is a churn row when it is complete and the user has no active row there.

## Code

```python
QUERY = """
WITH am AS (
  SELECT DISTINCT user_id, date_trunc('month', event_time)::DATE AS month
  FROM events WHERE event_type = 'login' AND event_time < TIMESTAMP '2025-07-01'
),
lagged AS (
  SELECT user_id, month, lag(month) OVER (PARTITION BY user_id ORDER BY month) AS prev FROM am
),
active AS (
  SELECT user_id, month,
         CASE WHEN prev IS NULL THEN 'new'
              WHEN prev = CAST(month - INTERVAL 1 MONTH AS DATE) THEN 'retained'
              ELSE 'resurrected' END AS state
  FROM lagged
),
churn AS (
  SELECT a.user_id, CAST(a.month + INTERVAL 1 MONTH AS DATE) AS month, 'churned' AS state
  FROM am a
  WHERE CAST(a.month + INTERVAL 1 MONTH AS DATE) < DATE '2025-07-01'
    AND NOT EXISTS (SELECT 1 FROM am b WHERE b.user_id = a.user_id AND b.month = CAST(a.month + INTERVAL 1 MONTH AS DATE))
)
SELECT * FROM active UNION ALL SELECT * FROM churn
"""
```

## Complexity

O(active months x log) for the window, plus an anti-join for the churn rows.

## Another way

Build a **full grid** of (user, month) from the user's first month to the last complete month and label every cell, including the long absence. Counting states per month is then a `GROUP BY month, state`. The grid is bigger but also answers "how many users are currently dormant?".

## Pitfall to remember

`retained` is about the previous **calendar month**, not the previous **active** month: comparing `prev = month - 1 month` is the whole difference between `retained` and `resurrected`.
