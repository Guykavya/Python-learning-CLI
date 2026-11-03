QUERY = """
SELECT c.name, COUNT(o.order_id) AS shipped_orders
FROM customers AS c
LEFT JOIN orders AS o ON o.customer_id = c.customer_id AND o.status = 'shipped'
GROUP BY c.customer_id, c.name
"""
