QUERY = """
SELECT c.name, o.order_id, o.ordered
FROM customers c
JOIN orders o ON o.customer_id = c.customer_id
WHERE o.order_id = (
    SELECT o2.order_id
    FROM orders o2
    WHERE o2.customer_id = c.customer_id
    ORDER BY o2.ordered DESC, o2.order_id DESC
    LIMIT 1
)
ORDER BY c.name
"""
