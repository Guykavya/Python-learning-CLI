## Hint 1

Print the broken query's four numbers and compare with the number of users. Which table in the `FROM` clause has more than one row per user, and what does a join to it do to every event row of that user? What does `count(*)` count after the join?

## Hint 2

```text
Is the `orders` join needed at all? The purchase step can use event_type = 'purchase' in events.
Count users, not rows: count(DISTINCT user_id) FILTER (WHERE event_type = ...)
```
