## Approach

`row_number()` numbered per user from newest to oldest, with `event_id DESC` as the tie-break, gives exactly one row numbered 1 for each user. `QUALIFY` keeps that row.

## Code

```python
QUERY = """
SELECT event_id, user_id, event_time, event_type
FROM events
QUALIFY row_number() OVER (PARTITION BY user_id ORDER BY event_time DESC, event_id DESC) = 1
"""
```

## Complexity

O(n log n): the sort inside each partition.

## Another way

`arg_max` returns the value of one column at the row where another is largest. For several columns use the struct trick `arg_max(e, (e.event_time, e.event_id))`, or one `arg_max` per column. Using `max(event_time)` in a `GROUP BY` and joining back is a common wrong turn: with ties it returns two rows for the same user.
