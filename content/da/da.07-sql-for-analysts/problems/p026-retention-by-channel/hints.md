## Hint 1

Which users are measured, and what condition on `signup_at` selects them? For each measured user, how do you test "has a login in the next calendar month" so that a user with five such logins counts once? Where does the small-sample rule go: in the `WHERE` (dropping the channel) or in the final `SELECT` (hiding only the percentage)?

## Hint 2

```text
cohort   : users WHERE signup_at < TIMESTAMP '2025-06-01'   -- month 1 complete
retained : EXISTS login with date_trunc('month', event_time) = date_trunc('month', signup_at) + INTERVAL 1 MONTH
final    : GROUP BY channel; users = count(*), retained_m1 = count(*) FILTER (WHERE retained),
           m1_retention = CASE WHEN count(*) >= 3 THEN retained_m1 * 1.0 / users END
```
