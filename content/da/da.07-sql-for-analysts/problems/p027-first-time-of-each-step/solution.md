## Approach

One `LEFT JOIN` from `users` to `events`, one `GROUP BY user_id`, and one `min(...) FILTER (WHERE ...)` per step. The grain of the result is "one row per user"; the `LEFT JOIN` keeps the users who did nothing, because in a funnel a user who did nothing is a drop-off, not a missing row.

## Code

```python
QUERY = """
SELECT u.user_id,
       min(e.event_time) FILTER (WHERE e.event_type = 'view_course')    AS t_view,
       min(e.event_time) FILTER (WHERE e.event_type = 'add_to_cart')    AS t_cart,
       min(e.event_time) FILTER (WHERE e.event_type = 'checkout_start') AS t_checkout,
       min(e.event_time) FILTER (WHERE e.event_type = 'purchase')       AS t_purchase
FROM users u LEFT JOIN events e USING (user_id)
GROUP BY u.user_id
"""
```

## Complexity

O(users + events).

## Another way

`PIVOT` can do the same in one statement, but `FILTER` works in every modern engine and shows exactly what each column means. Use `max(...)` for "last time of each step". The result is the base table of the funnel problems that follow: once it exists, every count is a `count(t_step)`.

## Pitfall to remember

`min` ignores `NULL`, so a `FILTER` that matches nothing gives `NULL`, which is what "never reached the step" must be.
