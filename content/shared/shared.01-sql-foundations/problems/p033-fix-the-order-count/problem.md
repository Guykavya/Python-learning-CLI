# Fix: the order count is too high

A teammate's report shows how many orders and how much revenue each customer has. The revenue is right, but `n_orders` is
too big for customers whose orders have several lines.

```sql
CREATE TABLE customers (customer_id INTEGER PRIMARY KEY, name TEXT NOT NULL, city TEXT);
INSERT INTO customers VALUES (1,'Asha','Pune'),(2,'Bala','Delhi'),(3,'Chitra',NULL),(4,'Dev','Pune');
CREATE TABLE orders (order_id INTEGER PRIMARY KEY, customer_id INTEGER, ordered TEXT, status TEXT);
INSERT INTO orders VALUES
 (101,1,'2024-01-05','shipped'),(102,1,'2024-02-10','shipped'),(103,4,'2024-02-11','cancelled'),
 (104,2,'2024-03-01','shipped'),(105,3,'2024-03-15','shipped');
CREATE TABLE order_items (order_id INTEGER, book_id INTEGER, qty INTEGER, unit_price REAL, PRIMARY KEY (order_id, book_id));
INSERT INTO order_items VALUES
 (101,1,2,10.0),(101,3,1,30.0),(102,4,1,40.0),(103,5,1,15.0),
 (104,2,3,6.0),(104,3,1,30.0),(105,6,1,50.0),(105,3,1,28.0);
```

`starter.py` already contains the buggy query:

```sql
SELECT c.name,
       COUNT(*) AS n_orders,
       ROUND(SUM(oi.qty * oi.unit_price), 2) AS revenue
FROM customers c
JOIN orders o       ON o.customer_id = c.customer_id
JOIN order_items oi ON oi.order_id   = o.order_id
GROUP BY c.customer_id, c.name
ORDER BY c.name;
```

On the data above it returns `('Asha', 3, 90.0)`, but Asha has only **2 orders**.

Fix it so the result is:

| column | meaning |
|---|---|
| `name` | customer name |
| `n_orders` | number of different orders (all statuses) |
| `revenue` | `ROUND(SUM(qty * unit_price), 2)` as before |

Same ordering as the buggy query (`name` ascending), customers without orders do not appear. Keep the column names.

**Example.** Expected for the data above: `Asha 2 90.0`, `Bala 1 48.0`, `Chitra 1 78.0`, `Dev 1 15.0`.
Hint for diagnosis: Asha's order 101 has two lines, so after the join it is two rows.
