## Approach

Make a row for each user and each N, drop the pairs whose day N has not happened by the extraction date, and test with `EXISTS` whether the user has a login on that exact date (an `EXISTS` cannot multiply rows, a join to events could). Then count per N. The ratio uses `NULLIF` so that an N with no eligible users gives `NULL`.

## Code

```python
QUERY = """
WITH pairs AS (
  SELECT u.user_id, n.day_n,
         EXISTS (SELECT 1 FROM events e
                 WHERE e.user_id = u.user_id AND e.event_type = 'login'
                   AND e.event_time::DATE = u.signup_at::DATE + n.day_n) AS retained
  FROM users u CROSS JOIN (VALUES (1), (7), (30)) AS n(day_n)
  WHERE u.signup_at::DATE + n.day_n <= DATE '2025-07-15'
)
SELECT n.day_n,
       count(p.user_id) AS eligible_users,
       count(*) FILTER (WHERE p.retained) AS retained_users,
       count(*) FILTER (WHERE p.retained) * 1.0 / NULLIF(count(p.user_id), 0) AS retention
FROM (VALUES (1), (7), (30)) AS n(day_n) LEFT JOIN pairs p USING (day_n)
GROUP BY n.day_n
"""
```

## Complexity

O(users x 3 x logins per user) with the correlated `EXISTS`; for big data pre-aggregate the logins to (user, date).

## Another way

The "within a window" and "on or after" versions of Ch. 6.6 change only the condition on the date: `BETWEEN 1 AND N`, or `>= N`. They give much higher numbers: always name the version you report.

## Pitfall to remember

Counting ineligible users in the denominator lowers retention for the newest cohort, the one managers look at first.
