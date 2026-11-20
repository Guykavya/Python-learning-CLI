INDEX = "CREATE INDEX idx_orders_customer_created ON orders(customer_id, created)"

QUERY = """
SELECT id, created FROM orders
WHERE customer_id = ?
ORDER BY created DESC, id DESC
LIMIT 20
"""
