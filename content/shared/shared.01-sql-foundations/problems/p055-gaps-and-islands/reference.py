QUERY = """
WITH numbered AS (
  SELECT day, ROW_NUMBER() OVER (ORDER BY day) AS rn
  FROM activity
),
grouped AS (
  SELECT day, date(day, '-' || rn || ' days') AS grp
  FROM numbered
)
SELECT MIN(day) AS start_day, MAX(day) AS end_day, COUNT(*) AS days
FROM grouped
GROUP BY grp
ORDER BY start_day
"""
