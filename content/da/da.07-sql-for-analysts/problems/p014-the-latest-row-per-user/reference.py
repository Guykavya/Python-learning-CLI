QUERY = """
SELECT event_id, user_id, event_time, event_type
FROM events
QUALIFY row_number() OVER (PARTITION BY user_id ORDER BY event_time DESC, event_id DESC) = 1
""" 
