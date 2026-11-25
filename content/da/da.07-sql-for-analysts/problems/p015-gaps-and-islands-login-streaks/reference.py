QUERY = """
WITH d AS (SELECT DISTINCT user_id, event_time::DATE AS day FROM events WHERE event_type = 'login'),
n AS (SELECT user_id, day, day - CAST(row_number() OVER (PARTITION BY user_id ORDER BY day) AS INTEGER) AS island FROM d),
streaks AS (SELECT user_id, island, count(*) AS days FROM n GROUP BY user_id, island)
SELECT user_id, max(days) AS longest_streak FROM streaks GROUP BY user_id
""" 
