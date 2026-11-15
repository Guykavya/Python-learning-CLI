QUERY = """
SELECT c.name,
       ROUND(SUM(oi.qty * oi.unit_price), 2) AS revenue
FROM customers c
JOIN orders o       ON o.customer_id = c.customer_id
JOIN order_items oi ON oi.order_id   = o.order_id
WHERE o.status <> 'cancelled'
GROUP BY c.customer_id, c.name
ORDER BY revenue DESC, c.name
"""
