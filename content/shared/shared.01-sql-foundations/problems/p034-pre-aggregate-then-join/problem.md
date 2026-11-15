# Pre-aggregate, then join

An order has **many lines** (`order_items`) and **many payments** (`payments`, customers may pay in parts). If you join
both to `orders` and sum, every line is paired with every payment and the sums are multiplied.

```sql
CREATE TABLE orders (order_id INTEGER PRIMARY KEY, customer_id INTEGER, ordered TEXT);
INSERT INTO orders VALUES (101,1,'2024-01-05'),(102,1,'2024-02-10'),(103,4,'2024-02-11');
CREATE TABLE order_items (order_id INTEGER, book_id INTEGER, qty INTEGER, unit_price REAL, PRIMARY KEY (order_id, book_id));
INSERT INTO order_items VALUES (101,1,2,10.0),(101,3,1,30.0),(102,4,1,40.0),(103,5,1,15.0);
CREATE TABLE payments (payment_id INTEGER PRIMARY KEY, order_id INTEGER, amount REAL);
INSERT INTO payments VALUES (1,101,30.0),(2,101,20.0),(3,102,40.0);
```

Report, for every order (even one with no lines or no payments):

| column | meaning |
|---|---|
| `order_id` | the order |
| `items_total` | `SUM(qty * unit_price)` over its lines, 0.0 if it has none |
| `paid` | `SUM(amount)` over its payments, 0.0 if none |

Ordered by `order_id`. Method: summarise each many-side table **by order_id first** (a subquery or CTE with `GROUP BY`),
then `LEFT JOIN` those one-row-per-order summaries to `orders`.

**Example.** Order 101 has lines worth 20.0 + 30.0 = 50.0 and payments 30.0 + 20.0 = 50.0, so `(101, 50.0, 50.0)`.
A careless double join gives `(101, 100.0, 100.0)`: each of 2 lines is paired with each of 2 payments, so every sum is doubled.
Order 103 has a line but no payment: `(103, 15.0, 0.0)`.
