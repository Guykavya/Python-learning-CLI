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
