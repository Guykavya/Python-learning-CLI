## Hint 1

For part 1, which steps does the retention table need, and which CTE gives the cohort size? For part 2, take each broken query in turn: what must the data contain so that its answer differs from the correct one? (A user who logs in twice in one month; a user whose first active month is not the sign-up month, or who skips one; a user with no login at all.)

## Hint 2

```text
part 1: cohort CTE, size CTE, DISTINCT (user, active month) with login and event_time < cutoff, join, count(DISTINCT user), date_diff('month', ...)
part 2 ingredients:
   user A: signs up in January, logs in on two days of January and in March (double login in a month, skipped February)
   user B: signs up in January, never logs in (so it counts in cohort_size but is never active)
   one more user in another cohort, so both cohorts appear
compute expected rows by hand and write them as tuples
```
