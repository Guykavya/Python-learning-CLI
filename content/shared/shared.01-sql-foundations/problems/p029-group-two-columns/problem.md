# Orders per customer and status

When you `GROUP BY` two columns, each **pair** of values is its own group. Here: one group per
(customer, status) that exists in the data.

```sql
CREATE TABLE orders (order_id INTEGER PRIMARY KEY, customer_id INTEGER, ordered TEXT, status TEXT);
INSERT INTO orders VALUES (1,1,'2024-01-01','shipped'),(2,1,'2024-01-09','shipped'),(3,1,'2024-02-01','cancelled'),(4,2,'2024-02-03','shipped'),(5,2,'2024-02-05','shipped'),(6,2,'2024-02-07','shipped'),(7,3,'2024-03-01','cancelled'),(8,3,'2024-03-02','cancelled');
```

Return, for each (customer, status) pair that exists:

| column | meaning |
|---|---|
| `customer_id` | the customer |
| `status` | the order status |
| `n_orders` | number of orders in that pair |

Order: `n_orders` descending, then `customer_id` **descending**, then `status` ascending (A to Z).

**Example.** Customer 1 has two `shipped` orders and one `cancelled`, so rows `(1, 'shipped', 2)` and `(1, 'cancelled', 1)` appear.
Pairs that do not exist (customer 3 has no `shipped` order) do not appear as rows with 0.
