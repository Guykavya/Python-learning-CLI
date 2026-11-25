QUERY = """
WITH e AS (SELECT * EXCLUDE (event_id) FROM events)
SELECT u.channel, u.country, e.event_type, count(*) AS events
FROM e JOIN users u USING (user_id)
GROUP BY ALL
""" 
