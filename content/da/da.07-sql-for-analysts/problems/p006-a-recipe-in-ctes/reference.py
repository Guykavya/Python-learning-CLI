QUERY = """
WITH first_purchase AS (SELECT user_id, min(order_time) AS first_time FROM orders GROUP BY user_id),
buyer_channel AS (
  SELECT f.user_id, u.channel, date_trunc('month', f.first_time)::DATE AS first_purchase_month
  FROM first_purchase f JOIN users u USING (user_id)
),
revenue AS (SELECT user_id, sum(amount) AS total FROM orders GROUP BY user_id)
SELECT b.channel, b.first_purchase_month, count(*) AS buyers, sum(r.total) AS revenue
FROM buyer_channel b JOIN revenue r USING (user_id)
GROUP BY b.channel, b.first_purchase_month
""" 
