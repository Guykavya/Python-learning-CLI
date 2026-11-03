## Approach

Each question maps to one pattern from the chapter: filter (Q1, Q2), group and count (Q3), anti-join (Q4), outer join with the filter in `ON` (Q5), join + group (Q6, Q7), `HAVING COUNT(DISTINCT)` (Q8), pre-aggregate then average (Q9), top-1 per group (Q10), running total (Q11), ranking (Q12). Build and check each one alone before moving on.

## Code

```python
QUERY_1 = """
SELECT title, price
FROM books
WHERE price > 25
ORDER BY price DESC, title
"""

QUERY_2 = """
SELECT name
FROM customers
WHERE city IS NULL
ORDER BY name
"""

QUERY_3 = """
SELECT category, COUNT(*) AS books
FROM books
GROUP BY category
ORDER BY books DESC, category
"""

QUERY_4 = """
SELECT a.name
FROM authors a
LEFT JOIN books b ON b.author_id = a.author_id
WHERE b.book_id IS NULL
"""

QUERY_5 = """
SELECT c.name,
       ROUND(COALESCE(SUM(oi.qty * oi.unit_price), 0), 2) AS revenue
FROM customers c
LEFT JOIN orders o       ON o.customer_id = c.customer_id AND o.status <> 'cancelled'
LEFT JOIN order_items oi ON oi.order_id = o.order_id
GROUP BY c.customer_id
ORDER BY revenue DESC, c.name
"""

QUERY_6 = """
SELECT strftime('%Y-%m', o.ordered) AS month,
       ROUND(SUM(oi.qty * oi.unit_price), 2) AS revenue
FROM orders o
JOIN order_items oi ON oi.order_id = o.order_id
WHERE o.status <> 'cancelled'
GROUP BY month
ORDER BY month
"""

QUERY_7 = """
SELECT b.title, SUM(oi.qty) AS units
FROM order_items oi
JOIN orders o ON o.order_id = oi.order_id
JOIN books b  ON b.book_id = oi.book_id
WHERE o.status <> 'cancelled'
GROUP BY b.book_id
ORDER BY units DESC, b.title
LIMIT 3
"""

QUERY_8 = """
SELECT c.name, COUNT(DISTINCT strftime('%Y-%m', o.ordered)) AS months
FROM customers c
JOIN orders o ON o.customer_id = c.customer_id
WHERE o.status <> 'cancelled'
GROUP BY c.customer_id
HAVING months >= 2
ORDER BY months DESC, c.name
"""

QUERY_9 = """
WITH totals AS (
  SELECT o.order_id, o.customer_id, SUM(oi.qty * oi.unit_price) AS total
  FROM orders o
  JOIN order_items oi ON oi.order_id = o.order_id
  WHERE o.status <> 'cancelled'
  GROUP BY o.order_id
)
SELECT COALESCE(c.city, 'Unknown') AS city,
       ROUND(AVG(t.total), 2) AS avg_order
FROM totals t
JOIN customers c ON c.customer_id = t.customer_id
GROUP BY COALESCE(c.city, 'Unknown')
ORDER BY city
"""

QUERY_10 = """
SELECT category, title, price
FROM (
  SELECT category, title, price,
         ROW_NUMBER() OVER (PARTITION BY category ORDER BY price DESC, title) AS rn
  FROM books
)
WHERE rn = 1
ORDER BY category
"""

QUERY_11 = """
WITH m AS (
  SELECT strftime('%Y-%m', o.ordered) AS month,
         SUM(oi.qty * oi.unit_price) AS revenue
  FROM orders o
  JOIN order_items oi ON oi.order_id = o.order_id
  WHERE o.status <> 'cancelled'
  GROUP BY month
)
SELECT month,
       ROUND(revenue, 2) AS revenue,
       ROUND(SUM(revenue) OVER (ORDER BY month), 2) AS cumulative
FROM m
ORDER BY month
"""

QUERY_12 = """
WITH r AS (
  SELECT a.name AS author, SUM(oi.qty * oi.unit_price) AS revenue
  FROM order_items oi
  JOIN orders o  ON o.order_id = oi.order_id
  JOIN books b   ON b.book_id = oi.book_id
  JOIN authors a ON a.author_id = b.author_id
  WHERE o.status <> 'cancelled'
  GROUP BY a.author_id
)
SELECT author, ROUND(revenue, 2) AS revenue,
       RANK() OVER (ORDER BY revenue DESC) AS rank
FROM r
ORDER BY rank, author
"""
```

## Complexity

On about 100 rows everything is instant. On real data the costs would be: scans of `order_items` (the biggest table) for Q5-Q9, Q11, Q12 (one pass each plus a hash/sort group); indexes on `order_items(order_id)`, `orders(customer_id)` and `books(author_id)` would turn the joins into lookups.

## Another way / portable SQL

Q4 can use `NOT EXISTS`; Q10 a correlated subquery `price = (SELECT MAX(price) ...)`; Q7 can use a window `RANK()`; Q12's `rank` alias is fine in SQLite, in PostgreSQL write `RANK()` with an alias that is not a keyword (`rnk`). In PostgreSQL `strftime` becomes `to_char(ordered::date, 'YYYY-MM')` and `HAVING months >= 2` must repeat the expression (`HAVING COUNT(DISTINCT ...) >= 2`).
