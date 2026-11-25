## Approach

The cohort of a user is the month of `signup_at`, `date_trunc('month', ...)`. The size is the number of users per cohort, counted in `users` (one row per user) so that users without events are not lost.

## Code

```python
QUERY = """
SELECT date_trunc('month', signup_at)::DATE AS cohort, count(*) AS cohort_size
FROM users
GROUP BY 1
"""
```

## Complexity

One pass over `users`: O(n).

## Another way

Joining `events` and counting `DISTINCT user_id` gives the number of *active* users, which is a different (smaller) number and the wrong denominator. A cohort size is fixed the moment the month ends: it must not depend on what the users did later.
