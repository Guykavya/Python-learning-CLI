QUERY = """
SELECT u.country,
       count(DISTINCT u.user_id) FILTER (WHERE e.event_type = 'view_course') AS viewers,
       count(DISTINCT u.user_id) FILTER (WHERE e.event_type = 'purchase') AS buyers,
       count(DISTINCT u.user_id) FILTER (WHERE e.event_type = 'purchase') * 1.0
         / NULLIF(count(DISTINCT u.user_id) FILTER (WHERE e.event_type = 'view_course'), 0) AS purchase_rate
FROM users u LEFT JOIN events e USING (user_id)
GROUP BY u.country
""" 
