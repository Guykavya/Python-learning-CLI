## Approach

The grain after `users LEFT JOIN events` is one row per **event** (or one row for a user with no event). To report at the grain of one row per channel we count *distinct users*, and we give the buyer count its own condition with `FILTER`. The `LEFT JOIN` keeps users with no events, so they still count in `users`.

## Code

```python
QUERY = """
SELECT u.channel,
       count(DISTINCT u.user_id) AS users,
       count(DISTINCT u.user_id) FILTER (WHERE e.event_type = 'purchase') AS buyers,
       count(DISTINCT u.user_id) FILTER (WHERE e.event_type = 'purchase') * 1.0
         / count(DISTINCT u.user_id) AS purchase_rate
FROM users u LEFT JOIN events e USING (user_id)
GROUP BY u.channel
"""
```

## Complexity

One join and one hash aggregation: O(users + events).

## Another way

Build one row per user first (`SELECT user_id, channel, bool_or(event_type = 'purchase') AS bought FROM ... GROUP BY ...`), then aggregate that table by channel with `sum(bought::INT)`. It is longer, but the grain of each step is obvious. The `SUM(CASE ...)` form works in every SQL engine.
