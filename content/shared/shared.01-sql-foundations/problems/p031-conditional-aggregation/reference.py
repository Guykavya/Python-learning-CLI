QUERY_A = """
SELECT customer_id,
       COUNT(*) AS total,
       SUM(CASE WHEN status = 'shipped'   THEN 1 ELSE 0 END) AS shipped,
       SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) AS cancelled
FROM orders
GROUP BY customer_id
ORDER BY customer_id
"""

QUERY_B = """
SELECT customer_id,
       COUNT(*) AS total,
       COUNT(*) FILTER (WHERE status = 'shipped')   AS shipped,
       COUNT(*) FILTER (WHERE status = 'cancelled') AS cancelled
FROM orders
GROUP BY customer_id
ORDER BY customer_id
"""
