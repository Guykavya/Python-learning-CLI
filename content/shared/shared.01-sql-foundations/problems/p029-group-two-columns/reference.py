QUERY = """
SELECT customer_id, status, COUNT(*) AS n_orders
FROM orders
GROUP BY customer_id, status
ORDER BY n_orders DESC, customer_id DESC, status
"""
