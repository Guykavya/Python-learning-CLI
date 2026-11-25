QUERY = """
SELECT 1 AS step, 'view_course' AS name, count(DISTINCT user_id) FILTER (WHERE event_type = 'view_course') AS users FROM events
UNION ALL
SELECT 2, 'add_to_cart', count(DISTINCT user_id) FILTER (WHERE event_type = 'add_to_cart') FROM events
UNION ALL
SELECT 3, 'checkout_start', count(DISTINCT user_id) FILTER (WHERE event_type = 'checkout_start') FROM events
UNION ALL
SELECT 4, 'purchase', count(DISTINCT user_id) FILTER (WHERE event_type = 'purchase') FROM events
""" 
