## Hint 1

If you join `users` to `events`, each user appears once per event. Which count survives that multiplication: `count(*)` or `count(DISTINCT user_id)`? And which join type keeps a user with no events?

## Hint 2

```text
FROM users u LEFT JOIN events e USING (user_id)
GROUP BY channel
users   = count(DISTINCT user_id)
buyers  = count(DISTINCT user_id) FILTER (WHERE event_type = 'purchase')
rate    = buyers * 1.0 / users
```

`FILTER` applies to one aggregate only, so the same query can hold a count with and a count without a condition.
