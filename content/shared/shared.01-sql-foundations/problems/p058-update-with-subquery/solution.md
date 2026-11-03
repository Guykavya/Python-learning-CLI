## Approach

Step 1 is a plain `UPDATE ... WHERE category = 'Tech'`. Step 2 uses `IN (subquery)`: the subquery groups orders by customer and keeps groups with `COUNT(*) >= 2`. Customers who are not in the list keep their default `'basic'`.

## Code

```python
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
```

## Complexity

Step 1 scans `books` (or uses an index on `category`). Step 2 aggregates `orders` once, then probes the id list per customer.

## Another way / portable SQL

`UPDATE ... WHERE EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = customers.customer_id GROUP BY ... HAVING COUNT(*) >= 2)` also works. `UPDATE ... FROM` joins (SQLite 3.33+, PostgreSQL) are handy for taking values from another table; MySQL writes `UPDATE a JOIN b ON ... SET ...`.
Run the matching `SELECT` first to preview the rows you are about to change.
