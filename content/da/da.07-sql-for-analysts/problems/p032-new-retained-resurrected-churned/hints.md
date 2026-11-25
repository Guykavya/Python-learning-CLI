## Hint 1

First one row per user and active month (what must be de-duplicated?). Which window function gives the previous active month of the same user, and how do you compare it with "exactly one month before"? Churn is about a month where the user does **not** appear: which row is the *cause* of that month's `churned` row, and how can you generate the next-month row from it?

## Hint 2

```text
am     : DISTINCT user_id, date_trunc('month', event_time)::DATE AS month   (login, before 2025-07-01)
active : lag(month) OVER (PARTITION BY user_id ORDER BY month) AS prev
         state = CASE WHEN prev IS NULL THEN 'new' WHEN prev = month - INTERVAL 1 MONTH THEN 'retained' ELSE 'resurrected' END
churn  : from each active month m, month m + 1 is 'churned' if it is < 2025-07-01 and the same user has no active row in m + 1 (NOT EXISTS)
final  : UNION ALL of the two
```
