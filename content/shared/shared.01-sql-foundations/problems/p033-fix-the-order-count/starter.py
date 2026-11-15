# This query is BUGGY: n_orders counts order lines, not orders. Fix it.
QUERY = """
SELECT c.name,
       COUNT(*) AS n_orders,
       ROUND(SUM(oi.qty * oi.unit_price), 2) AS revenue
FROM customers c
JOIN orders o       ON o.customer_id = c.customer_id
JOIN order_items oi ON oi.order_id   = o.order_id
GROUP BY c.customer_id, c.name
ORDER BY c.name
"""
