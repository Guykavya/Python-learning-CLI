## Hint 1

What are the groups (`PARTITION BY`) and what is the order inside each group? Then, once you have the previous time on the row, how do you count days between two timestamps so that midnight counts as a boundary: with a timestamp difference, or with the dates?

## Hint 2

```text
SELECT user_id, order_id, order_time,
       lag(order_time) OVER (PARTITION BY user_id ORDER BY order_time, order_id) AS prev_order_time,
       date_diff('day', prev_order_time::DATE, order_time::DATE) AS days_since_prev
```

You cannot use the alias `prev_order_time` in the same `SELECT` list: compute it in a CTE (or repeat the window) first.
