## Hint 1

Write each step as its own small `SELECT` and look at its result before you build the next one. What is the grain of the first step (one row per what)? If you join `orders` to the second step at the end, how many rows does each buyer have, and does that matter for `buyers`?

## Hint 2

```text
WITH first_purchase AS (SELECT user_id, min(order_time) AS first_time FROM orders GROUP BY user_id),
     buyer_channel  AS (SELECT f.user_id, u.channel, date_trunc('month', f.first_time)::DATE AS first_purchase_month
                        FROM first_purchase f JOIN users u USING (user_id)),
     revenue        AS (SELECT user_id, sum(amount) AS total FROM orders GROUP BY user_id)
SELECT channel, first_purchase_month, count(*) AS buyers, sum(total) AS revenue
FROM buyer_channel JOIN revenue USING (user_id)
GROUP BY ...
```

Each CTE has one row per user, so the final join cannot multiply rows.
