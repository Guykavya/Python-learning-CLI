# Share of customers who ordered again within 30 days

A *cohort/funnel* question: of the customers who ordered at all, how many came back quickly? Define it carefully:

- A customer's **first order date** is the earliest `ordered` date among their orders (use dates, not order ids; order ids may not be in date order).
- A customer is a **repeater** if they placed another order on a date after their first order date and **at most 30 days** after it. (A second order on the same day does not count; day 30 counts.)
- Only customers with at least one order are in the base. Order status is ignored.

```sql
CREATE TABLE customers (customer_id INTEGER PRIMARY KEY, name TEXT);
CREATE TABLE orders (order_id INTEGER PRIMARY KEY, customer_id INTEGER, ordered TEXT, status TEXT);
INSERT INTO customers VALUES (1,'c1'),(2,'c2'),(3,'c3'),(4,'c4'),(5,'c5');
INSERT INTO orders VALUES
 (1,1,'2024-01-01','shipped'),(2,1,'2024-01-20','shipped'),
 (3,2,'2024-01-05','shipped'),(4,2,'2024-03-01','shipped'),(8,2,'2024-03-20','shipped'),
 (5,3,'2024-02-01','shipped'),
 (6,4,'2024-02-10','shipped'),(7,4,'2024-03-11','cancelled');
```

Write one query that returns exactly one row with columns `customers`, `repeaters`, `pct_repeat`: the number of customers with orders, the number of repeaters, and `100.0 * repeaters / customers` rounded to 1 decimal.
If nobody has orders, return `(0, 0, NULL)`.

**Example (for the data above)**

| customers | repeaters | pct_repeat |
|---|---|---|
| 4 | 2 | 50.0 |

c1 ordered again after 19 days (repeater). c2's second order is 56 days later and the third is 75 days after the first: not a repeater. c3 has one order. c4's first order is 2024-02-10 and the second 2024-03-11, exactly 30 days later (2024 is a leap year): a repeater, even though that order was cancelled. c5 has no orders and is not counted.
