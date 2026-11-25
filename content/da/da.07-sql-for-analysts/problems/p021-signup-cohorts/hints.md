## Hint 1

Which single table holds one row per user and the sign-up time? Do you need `events` at all for the cohort size? How do you map a timestamp to "its month" so that all the days of January give the same value?

## Hint 2

```text
SELECT date_trunc('month', signup_at)::DATE AS cohort, count(*) AS cohort_size
FROM users
GROUP BY 1
```
