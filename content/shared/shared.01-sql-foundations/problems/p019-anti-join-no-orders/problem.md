# Anti-join: customers with no orders

An **anti-join** finds rows of A that have **no** match in B. The classic recipe: `LEFT JOIN` B and keep the rows where
B's key is NULL (the "no match" marker).

```sql
CREATE TABLE customers (
  customer_id INTEGER PRIMARY KEY,
  name        TEXT NOT NULL,
  city        TEXT
);
CREATE TABLE orders (
  order_id    INTEGER PRIMARY KEY,
  customer_id INTEGER,          -- may be NULL for guest checkout
  ordered     TEXT NOT NULL
);
INSERT INTO customers VALUES
 (1, 'Asha', 'Pune'), (2, 'Ben', NULL), (3, 'Chen', 'Delhi'),
 (4, 'Dia', NULL), (5, 'Eli', 'Pune'), (6, 'Fay', 'Goa');
INSERT INTO orders VALUES
 (10, 1, '2024-01-05'), (11, 1, '2024-02-10'), (12, 2, '2024-02-11'),
 (13, 3, '2024-03-01'), (14, 5, '2024-03-15');
```

Return the `name` of every customer who has **never placed an order**. One column, `name`. Row order does not matter.
Put the SQL in `QUERY`.

Be careful: `orders.customer_id` may be NULL (a guest checkout). Your query must still work when it is.

**Example (a different question).** Authors with no books: `FROM authors a LEFT JOIN books b ON b.author_id = a.author_id WHERE b.book_id IS NULL`.
