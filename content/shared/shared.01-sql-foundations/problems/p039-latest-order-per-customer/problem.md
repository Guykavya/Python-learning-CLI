# Latest order per customer

A **correlated subquery** refers to a column of the outer query, so it is evaluated once per outer row. A classic use is "the
latest X for each Y".

```sql
CREATE TABLE customers (customer_id INTEGER PRIMARY KEY, name TEXT NOT NULL, city TEXT);
INSERT INTO customers VALUES (1,'Asha','Pune'),(2,'Bala','Delhi'),(3,'Chitra',NULL),(4,'Dev','Pune');
CREATE TABLE orders (order_id INTEGER PRIMARY KEY, customer_id INTEGER, ordered TEXT, status TEXT);
INSERT INTO orders VALUES
 (101,1,'2024-01-05','shipped'),(102,1,'2024-02-10','shipped'),(103,4,'2024-02-11','cancelled'),
 (104,2,'2024-03-01','shipped'),(105,3,'2024-03-15','shipped');
```

Return each customer who has orders, with their **most recent order**:

| column | meaning |
|---|---|
| `name` | customer name |
| `order_id` | id of the latest order |
| `ordered` | its date |

Ordered by `name`. If a customer has two orders on the same latest date, return **only the one with the larger `order_id`**.
Customers with no orders do not appear. Use a correlated subquery, not window functions.

**Example.** Asha has orders 101 (2024-01-05) and 102 (2024-02-10): the row is `('Asha', 102, '2024-02-10')`.
