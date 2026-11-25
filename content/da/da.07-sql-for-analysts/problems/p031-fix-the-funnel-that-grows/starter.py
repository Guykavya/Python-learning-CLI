QUERY = """
SELECT 1 AS step, 'view_course' AS name, count(*) FILTER (WHERE e.event_type = 'view_course') AS users
FROM events e LEFT JOIN orders o USING (user_id)
UNION ALL
SELECT 2, 'add_to_cart', count(*) FILTER (WHERE e.event_type = 'add_to_cart')
FROM events e LEFT JOIN orders o USING (user_id)
UNION ALL
SELECT 3, 'checkout_start', count(*) FILTER (WHERE e.event_type = 'checkout_start')
FROM events e LEFT JOIN orders o USING (user_id)
UNION ALL
SELECT 4, 'purchase', count(o.order_id)
FROM events e LEFT JOIN orders o USING (user_id)
"""
