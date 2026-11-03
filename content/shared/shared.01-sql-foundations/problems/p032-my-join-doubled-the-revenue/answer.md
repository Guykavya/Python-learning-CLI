**1. Why 140.0.** Order 1 has two lines, so the join returns it twice. Its `total` (50.0) is repeated in both rows:

| order_id | total | book_id |
|---|---|---|
| 1 | 50.0 | 1 |
| 1 | 50.0 | 3 |
| 2 | 40.0 | 4 |
| 3 | 15.0 | 5 |

For customer 10, `SUM(o.total)` adds 50.0 (line 1) + 50.0 (line 3) + 40.0 (order 2) = **140.0**. The correct 90.0 needs each order once. The query changed the *grain*: `orders` has one row per order, but `orders JOIN order_items` has one row per **order line**. Any value that belongs to the order is repeated once per line, and `SUM` cannot know that.

**2. The check.** Compare `SELECT COUNT(*)` with `SELECT COUNT(DISTINCT o.order_id)` over the joined rows (here 4 versus 3), or just compare the number of rows of `orders` with the number of rows after the join. If they differ, an order total will be repeated. Do this after every join in a report.

**3. Two fixes.**
- Do not join at all: `SELECT customer_id, SUM(total) FROM orders GROUP BY customer_id` gives `10 | 90.0`, `20 | 15.0`. Choose it when the question needs only order-level data.
- Compute from the lines: `SUM(oi.qty * oi.unit_price)` over the join. The lines are the "many" side, so nothing is repeated and the result is also 90.0. Choose it when you also need line data, such as book or category.
(Bonus: summarise the lines per order first in a subquery, then join that to `orders`.)

**4. Counts.** `COUNT(*)` over the join is also wrong: it counts lines (3 for customer 10), not orders. `COUNT(DISTINCT o.order_id)` is safe because the repeats share the same id. `SUM(DISTINCT o.total)` is **not** safe: two different orders with the same total collapse into one.

**Takeaway.** Before aggregating, ask: "what does one row of my FROM clause mean?" If a join makes it finer than the thing you are measuring, aggregate before joining or measure on the finer side.
