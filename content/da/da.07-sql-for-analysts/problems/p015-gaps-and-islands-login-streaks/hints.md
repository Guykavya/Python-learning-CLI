## Hint 1

First reduce the table to one row per user and **login day**. If you number each user's days 1, 2, 3, ... in date order and subtract that number from the date, what happens to the result inside a run of consecutive days, and what happens after a missing day?

## Hint 2

```text
d : SELECT DISTINCT user_id, event_time::DATE AS day FROM events WHERE event_type = 'login'
n : SELECT user_id, day, day - CAST(row_number() OVER (PARTITION BY user_id ORDER BY day) AS INTEGER) AS island FROM d
s : SELECT user_id, island, count(*) AS days FROM n GROUP BY user_id, island
final: max(days) per user
```
