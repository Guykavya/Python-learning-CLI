QUERY = """
WITH f AS (
  SELECT u.user_id, u.channel,
         min(e.event_time) FILTER (WHERE e.event_type = 'add_to_cart') AS t_cart,
         min(e.event_time) FILTER (WHERE e.event_type = 'purchase') AS t_purchase
  FROM users u LEFT JOIN events e USING (user_id) GROUP BY u.user_id, u.channel
)
SELECT channel, count(*) AS converters, median(epoch(t_purchase - t_cart) / 3600.0) AS median_hours
FROM f WHERE t_purchase >= t_cart GROUP BY channel
""" 
