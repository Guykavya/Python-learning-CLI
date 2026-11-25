## Approach

The query has two bugs that feed each other. First, joining `events` to `orders` repeats every event of a user once per order of that user (the fan-out of da.06), so a user with two orders has every event doubled. Second, it counts **rows** (`count(*)`, `count(o.order_id)`), not users. The step `purchase` counts `o.order_id`, which is the number of event-order pairs. The fix drops the unnecessary join and counts distinct users on the events table.

## Code

```python
QUERY = """
SELECT 1 AS step, 'view_course' AS name, count(DISTINCT user_id) FILTER (WHERE event_type = 'view_course') AS users FROM events
UNION ALL
SELECT 2, 'add_to_cart', count(DISTINCT user_id) FILTER (WHERE event_type = 'add_to_cart') FROM events
UNION ALL
SELECT 3, 'checkout_start', count(DISTINCT user_id) FILTER (WHERE event_type = 'checkout_start') FROM events
UNION ALL
SELECT 4, 'purchase', count(DISTINCT user_id) FILTER (WHERE event_type = 'purchase') FROM events
"""
```

## Complexity

Four scans of `events`; one scan with a conditional aggregation per step also works (see below).

## Another way

Build the "first time per user and step" table and count non-NULL columns (Ch. 7.2): the grain is explicit and the check `rows = users` is one line. Whatever the form, the habit that finds this bug is **the grain check**: after every join ask what one row is now, and assert `count(*) = count(DISTINCT user_id)` where one row per user is expected (problem 38 turns this into a function).
