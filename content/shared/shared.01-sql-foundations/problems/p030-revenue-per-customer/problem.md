# Revenue per customer

Revenue of an order line is `qty * unit_price`. Join the three tables, then group by customer.

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

Return one row per customer who has at least one **non-cancelled** order (`status <> 'cancelled'`):

| column | meaning |
|---|---|
| `name` | customer name |
| `revenue` | sum of `qty * unit_price` over all lines of the customer's non-cancelled orders, `ROUND(..., 2)` |

Order: revenue descending, then `name` ascending.

**Example.** Asha has orders 101 (2 x 10.0 + 1 x 30.0 = 50.0) and 102 (40.0), so her revenue is `90.0`.
Dev has only a cancelled order, so Dev does **not** appear. Dev's row would be `('Dev', 15.0)` if cancelled orders counted.
