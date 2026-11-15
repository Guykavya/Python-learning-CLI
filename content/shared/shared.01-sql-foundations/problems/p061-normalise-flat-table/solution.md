## Approach

1. Create the parent tables (`customers`, `books`) first, then `lines`, which has foreign keys to them.
2. Fill the parents with `SELECT DISTINCT`: each customer and each book appears once.
3. Fill `lines` by joining the flat table to the parents on the natural keys (name, title) to fetch the new surrogate ids.

## Code

```python
SCRIPT = """
CREATE TABLE customers (
  customer_id INTEGER PRIMARY KEY,
  name TEXT NOT NULL UNIQUE,
  city TEXT
);
CREATE TABLE books (
  book_id INTEGER PRIMARY KEY,
  title TEXT NOT NULL UNIQUE,
  price REAL NOT NULL
);
CREATE TABLE lines (
  line_id INTEGER PRIMARY KEY,
  order_id INTEGER NOT NULL,
  customer_id INTEGER NOT NULL REFERENCES customers(customer_id),
  book_id INTEGER NOT NULL REFERENCES books(book_id),
  qty INTEGER NOT NULL
);

INSERT INTO customers (name, city)
SELECT DISTINCT customer_name, customer_city FROM orders_flat;

INSERT INTO books (title, price)
SELECT DISTINCT book_title, book_price FROM orders_flat;

INSERT INTO lines (order_id, customer_id, book_id, qty)
SELECT f.order_id, c.customer_id, b.book_id, f.qty
FROM orders_flat f
JOIN customers c ON c.name = f.customer_name
JOIN books b ON b.title = f.book_title;
"""
```

## Complexity

The two `DISTINCT` inserts each scan the flat table once. The `lines` insert does an indexed lookup per row (the `UNIQUE` constraints create the indexes), so it is about O(n log n). Without those unique indexes the joins would be O(n * m).

## Another way / portable SQL

A cleaner design for the order header: an `orders(order_id, customer_id)` table plus `order_items(order_id, book_id, qty)`, since the customer belongs to the *order*, not to each line. The problem keeps three tables so it stays small. In PostgreSQL use `SERIAL`/`GENERATED ... AS IDENTITY` for ids; MySQL uses `AUTO_INCREMENT`. Foreign keys are only checked in SQLite when `PRAGMA foreign_keys = ON`.
