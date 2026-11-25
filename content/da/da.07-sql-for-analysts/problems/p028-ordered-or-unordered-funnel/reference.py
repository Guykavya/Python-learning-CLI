QUERY = """
WITH f AS (
  SELECT u.user_id,
         min(e.event_time) FILTER (WHERE e.event_type = 'view_course') AS t_view,
         min(e.event_time) FILTER (WHERE e.event_type = 'add_to_cart') AS t_cart,
         min(e.event_time) FILTER (WHERE e.event_type = 'checkout_start') AS t_checkout,
         min(e.event_time) FILTER (WHERE e.event_type = 'purchase') AS t_purchase
  FROM users u LEFT JOIN events e USING (user_id) GROUP BY u.user_id
)
SELECT 1 AS step, 'view_course' AS name, count(*) FILTER (WHERE t_view IS NOT NULL) AS users FROM f
UNION ALL SELECT 2, 'add_to_cart', count(*) FILTER (WHERE t_cart >= t_view) FROM f
UNION ALL SELECT 3, 'checkout_start', count(*) FILTER (WHERE t_checkout >= t_cart AND t_cart >= t_view) FROM f
UNION ALL SELECT 4, 'purchase', count(*) FILTER (WHERE t_purchase >= t_checkout AND t_checkout >= t_cart AND t_cart >= t_view) FROM f
""" 
