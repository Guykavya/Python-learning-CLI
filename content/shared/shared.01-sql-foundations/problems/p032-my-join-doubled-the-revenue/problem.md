# Explain: my join doubled the revenue

A teammate wrote a report of revenue per customer. Each order stores its own `total` (already the sum of its lines).
The report shows a number that is **too high** for customer 10.

```sql
CREATE TABLE orders (order_id INTEGER PRIMARY KEY, customer_id INTEGER, total REAL);
CREATE TABLE order_items (order_id INTEGER, book_id INTEGER, qty INTEGER, unit_price REAL, PRIMARY KEY (order_id, book_id));
INSERT INTO orders VALUES (1, 10, 50.0), (2, 10, 40.0), (3, 20, 15.0);
INSERT INTO order_items VALUES (1,1,2,10.0),(1,3,1,30.0),(2,4,1,40.0),(3,5,1,15.0);

SELECT o.customer_id, SUM(o.total) AS revenue
FROM orders o
JOIN order_items oi ON oi.order_id = o.order_id
GROUP BY o.customer_id
ORDER BY o.customer_id;
```

The query returns:

| customer_id | revenue |
|---|---|
| 10 | 140.0 |
| 20 | 15.0 |

But customer 10's two orders (50.0 and 40.0) add up to **90.0**.

Answer in your own words in `answer.md` (150 to 400 words):

1. Why is 140.0 wrong? Say exactly which numbers were added to get 140.0, and what the join did to the `orders` rows.
2. What one-line check shows the problem *before* you trust the report (hint: compare two counts)?
3. Give **two** different ways to fix the query so customer 10 shows 90.0. Say when you would pick each.
4. Would the same bug also hurt `COUNT(*)` and `COUNT(DISTINCT o.order_id)`? Which of the two is safe?

Then compare with the model answer by self-rating. A good answer names the idea of the **grain** of a result (what one row means).
