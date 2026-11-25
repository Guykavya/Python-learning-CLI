## Approach

Restrict to users with a complete month 1, mark each as retained or not with `EXISTS` (one boolean per user, so no fan-out), then aggregate per channel. The minimum-sample rule is applied only to the percentage, so the reader still sees the counts behind a `NULL`.

## Code

```python
QUERY = """
WITH cohort AS (
  SELECT user_id, channel, date_trunc('month', signup_at)::DATE AS cohort_month
  FROM users WHERE signup_at < TIMESTAMP '2025-06-01'
),
flagged AS (
  SELECT c.channel,
         EXISTS (SELECT 1 FROM events e
                 WHERE e.user_id = c.user_id AND e.event_type = 'login'
                   AND date_trunc('month', e.event_time)::DATE = CAST(c.cohort_month + INTERVAL 1 MONTH AS DATE)) AS retained
  FROM cohort c
)
SELECT channel, count(*) AS users, count(*) FILTER (WHERE retained) AS retained_m1,
       CASE WHEN count(*) >= 3 THEN count(*) FILTER (WHERE retained) * 1.0 / count(*) END AS m1_retention
FROM flagged GROUP BY channel
"""
```

## Complexity

O(users x logins per user) for the correlated `EXISTS`.

## Another way

Join to a de-duplicated `(user, active month)` table instead of `EXISTS`: faster on big tables. Compare channels only after checking that the channel **mix per cohort** is similar (Simpson's paradox, da.06).

## Pitfall to remember

Small groups produce wild percentages (1 of 1 is 100%). Show the count next to every rate, and hide the rate when the count is too small.

## Check

For `ads` in the example: users 1, 2, 3, 4 measured; retained are users 1 and 3: 2 of 4 = 0.5.
