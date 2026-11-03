# Chained CTEs: customers with above-average orders

A `WITH` can define several CTEs separated by commas, and **a later one may use an earlier one**. This lets you build a
query in readable layers: lines -> order totals -> customer statistics -> answer.

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

Build it in three layers:

1. `order_totals`: one row per order: `order_id`, `customer_id`, `total` (`SUM(qty * unit_price)`).
2. `customer_stats`: one row per customer: `customer_id`, `n_orders`, `spent` (sum of totals).
3. The final `SELECT`: customers whose **average order value** (`spent / n_orders`) is strictly greater than the average of **all
   order totals**.

Columns: `name`, `n_orders`, `spent`, `avg_order` (`ROUND(spent * 1.0 / n_orders, 2)`). Ordered by `avg_order` descending, then `name`.
Every order counts (any status).

**Example.** Order totals: 50.0, 40.0, 15.0, 48.0, 78.0, so the overall average is 46.2. Customer averages: Asha 45.0 (not above),
Bala 48.0, Chitra 78.0, Dev 15.0. Result: Chitra then Bala.
