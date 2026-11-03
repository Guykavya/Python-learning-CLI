## Approach

See `answer.md`. In short: the join gives one row per order *line*, so an order total that lives on the order is repeated once per line, and `SUM` adds it that many times.

## Code

```sql
-- fix 1: no join needed, the data is already at the right grain
SELECT customer_id, SUM(total) AS revenue
FROM orders
GROUP BY customer_id;

-- fix 2: compute revenue from the lines (the lines are the many side, nothing is repeated)
SELECT o.customer_id, SUM(oi.qty * oi.unit_price) AS revenue
FROM orders o
JOIN order_items oi ON oi.order_id = o.order_id
GROUP BY o.customer_id;
```

Both return `10 | 90.0` and `20 | 15.0`.

## Complexity

Fix 1 reads only `orders`. Fix 2 reads every order line and joins, more work but needed when the question depends on line data (book, category). The fan-out bug itself is cheap to run and expensive to find: it returns plausible numbers.

## Another way / portable SQL

Pre-aggregate the many side in a subquery or CTE, then join (see the pre-aggregate problem). `COUNT(DISTINCT o.order_id)` rescues counts, but `SUM(DISTINCT o.total)` is **not** a fix: two different orders with the same total would collapse into one. All databases behave the same here.
