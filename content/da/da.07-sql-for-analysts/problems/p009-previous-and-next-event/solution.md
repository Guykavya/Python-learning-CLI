## Approach

`lag` over a window partitioned by user and ordered by time gives the previous order on the same row. The days between two **dates** are `date_diff('day', d1, d2)`; casting both timestamps to `DATE` first turns "elapsed time" into "calendar days".

## Code

```python
QUERY = """
WITH x AS (
  SELECT user_id, order_id, order_time,
         lag(order_time) OVER (PARTITION BY user_id ORDER BY order_time, order_id) AS prev_order_time
  FROM orders
)
SELECT user_id, order_id, order_time, prev_order_time,
       date_diff('day', prev_order_time::DATE, order_time::DATE) AS days_since_prev
FROM x
"""
```

When `prev_order_time` is `NULL`, `NULL::DATE` is `NULL` and `date_diff` returns `NULL`: no `CASE` is needed.

## Complexity

One sort per user partition: O(n log n) in the worst case.

## Another way

A self join on "the largest earlier order_time of the same user" gives the same answer but needs a correlated subquery and is slower and harder to read. `lead` is the mirror of `lag`: the **next** row.

## Pitfall to remember

`lag` looks at rows, not at calendar time: if a user skips a month, `lag` returns the older order, which is what you want here but not for period-over-period metrics (Ch. 5.3).
