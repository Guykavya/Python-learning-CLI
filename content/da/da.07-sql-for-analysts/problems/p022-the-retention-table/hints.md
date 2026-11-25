## Hint 1

What are the three grains you need: one row per user (with the cohort), one row per user and active month, and one row per cohort and month number? Which keyword removes the repeated logins in the same month? And what do you divide by: the number of active users or the size of the whole cohort?

## Hint 2

```text
cohort   : SELECT user_id, date_trunc('month', signup_at)::DATE AS cohort FROM users
size     : cohort, count(*) AS cohort_size GROUP BY cohort
activity : SELECT DISTINCT user_id, date_trunc('month', event_time)::DATE AS m FROM events
           WHERE event_type = 'login' AND event_time < TIMESTAMP '2025-07-01'
counts   : cohort JOIN activity USING (user_id), month_number = date_diff('month', cohort, m), count(DISTINCT user_id)
final    : counts JOIN size USING (cohort), retention = active_users * 1.0 / cohort_size
```
