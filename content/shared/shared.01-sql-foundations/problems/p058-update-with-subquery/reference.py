SCRIPT = """
UPDATE books
SET price = ROUND(price * 1.10, 2)
WHERE category = 'Tech';

UPDATE customers
SET tier = 'gold'
WHERE customer_id IN (
  SELECT customer_id FROM orders
  GROUP BY customer_id
  HAVING COUNT(*) >= 2
);
"""
