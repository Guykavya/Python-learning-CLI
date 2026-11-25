## Approach

Three steps, each at the grain "one row per buyer": the first order time, the channel plus the month label, and the total revenue. Because every CTE has exactly one row per user, joining them is safe (a many-to-many join would inflate the revenue, as in da.06). The last step only aggregates.

## Code

```python
QUERY = """
WITH first_purchase AS (
  SELECT user_id, min(order_time) AS first_time FROM orders GROUP BY user_id
),
buyer_channel AS (
  SELECT f.user_id, u.channel, date_trunc('month', f.first_time)::DATE AS first_purchase_month
  FROM first_purchase f JOIN users u USING (user_id)
),
revenue AS (
  SELECT user_id, sum(amount) AS total FROM orders GROUP BY user_id
)
SELECT b.channel, b.first_purchase_month, count(*) AS buyers, sum(r.total) AS revenue
FROM buyer_channel b JOIN revenue r USING (user_id)
GROUP BY b.channel, b.first_purchase_month
"""
```

## Complexity

Two passes over `orders` and one join of user-sized tables: O(orders + users).

## Another way

Steps 1 and 3 can be one CTE (`min(order_time)` and `sum(amount)` in the same `GROUP BY user_id`). Keeping them separate costs one more scan but makes each step answer one question, which is easier to check. A window function (`min(order_time) OVER (PARTITION BY user_id)`) would also find the first time, but then the grain stays "one row per order" and you must de-duplicate again.
