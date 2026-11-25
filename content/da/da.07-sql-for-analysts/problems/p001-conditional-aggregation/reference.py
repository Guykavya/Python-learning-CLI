QUERY = """
SELECT u.channel,
       count(DISTINCT u.user_id) AS users,
       count(DISTINCT u.user_id) FILTER (WHERE e.event_type = 'purchase') AS buyers,
       count(DISTINCT u.user_id) FILTER (WHERE e.event_type = 'purchase') * 1.0 / count(DISTINCT u.user_id) AS purchase_rate
FROM users u LEFT JOIN events e USING (user_id)
GROUP BY u.channel
""" 
