INDEX = "CREATE INDEX idx_orders_customer ON orders(customer_id)"

QUERY = """
SELECT id, created FROM orders
WHERE customer_id = ?
ORDER BY created DESC, id DESC
LIMIT 20
"""
