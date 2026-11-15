QUERY = """
WITH first_order AS (
  SELECT customer_id, MIN(ordered) AS first_day
  FROM orders
  GROUP BY customer_id
),
repeaters AS (
  SELECT DISTINCT o.customer_id
  FROM orders o
  JOIN first_order f ON f.customer_id = o.customer_id
  WHERE julianday(o.ordered) - julianday(f.first_day) BETWEEN 1 AND 30
)
SELECT (SELECT COUNT(*) FROM first_order) AS customers,
       (SELECT COUNT(*) FROM repeaters)   AS repeaters,
       ROUND(100.0 * (SELECT COUNT(*) FROM repeaters)
             / NULLIF((SELECT COUNT(*) FROM first_order), 0), 1) AS pct_repeat
"""
