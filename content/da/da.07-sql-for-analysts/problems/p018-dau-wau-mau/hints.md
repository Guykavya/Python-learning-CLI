## Hint 1

If you first reduce `events` to one row per (user, login day), what must the join between the calendar and that table look like so that each calendar day sees the logins of the last 30 days? Then `DAU`, `WAU` and `MAU` are the same distinct count over different slices: which feature restricts one aggregate to the last 1 or 7 days of the joined rows?

## Hint 2

```text
l   : SELECT DISTINCT user_id, event_time::DATE AS day FROM events WHERE event_type = 'login'
cal : one row per day from min(day) to max(day) of l
FROM cal c LEFT JOIN l ON l.day BETWEEN c.day - 29 AND c.day
dau = count(DISTINCT l.user_id) FILTER (WHERE l.day = c.day)
wau = count(DISTINCT l.user_id) FILTER (WHERE l.day > c.day - 7)
mau = count(DISTINCT l.user_id)
GROUP BY c.day
```
