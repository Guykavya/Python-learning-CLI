# Join three tables: a total per line

An order line lives in `order_items` (which order, which book, how many, price when sold). To print a readable
report you need the `orders` row (to see the status) and the `books` row (to get the title). You can chain joins:
`FROM a JOIN b ON ... JOIN c ON ...`.

```sql
CREATE TABLE books (
  book_id   INTEGER PRIMARY KEY,
  title     TEXT NOT NULL,
  author_id INTEGER,
  category  TEXT NOT NULL,
  price     REAL NOT NULL,
  published TEXT NOT NULL,   -- 'YYYY-MM-DD'
  pages     INTEGER          -- NULL when unknown
);
INSERT INTO books VALUES
 (1, 'Quiet Rivers',    1, 'fiction', 12.50, '2019-03-10', 320),
 (2, 'Iron Garden',     1, 'fiction',  9.99, '2021-07-01', 280),
 (3, 'Data Basics',     2, 'tech',    39.00, '2020-01-15', 450),
 (4, 'SQL in Practice', 2, 'tech',    45.50, '2022-05-20', NULL),
 (5, 'Cooking Light',   3, 'cooking', 18.00, '2018-11-30', 200),
 (6, 'Salt and Stone',  3, 'cooking', 18.00, '2023-02-14', 240),
 (7, 'Night Train',     4, 'mystery',  9.99, '2022-09-09', 310),
 (8, 'Paper Moons',     4, 'fiction', 14.25, '2017-06-25', NULL);
CREATE TABLE orders (
  order_id    INTEGER PRIMARY KEY,
  customer_id INTEGER,
  ordered     TEXT NOT NULL,
  status      TEXT NOT NULL      -- 'shipped', 'pending' or 'cancelled'
);
CREATE TABLE order_items (
  order_id   INTEGER NOT NULL,
  book_id    INTEGER NOT NULL,
  qty        INTEGER NOT NULL,
  unit_price REAL NOT NULL,       -- price when sold; may differ from books.price
  PRIMARY KEY (order_id, book_id)
);
INSERT INTO orders VALUES
 (1, 1, '2024-01-05', 'shipped'),
 (2, 1, '2024-02-10', 'shipped'),
 (3, 2, '2024-02-11', 'cancelled'),
 (4, 3, '2024-03-01', 'shipped'),
 (5, 5, '2024-03-15', 'pending');
INSERT INTO order_items VALUES
 (1, 1, 2, 12.50), (1, 3, 1, 39.00), (2, 5, 1, 18.00), (3, 2, 1, 9.99),
 (4, 7, 3, 9.99),  (4, 8, 1, 14.25), (5, 4, 1, 45.50);
```

Return one row per order line of **shipped** orders, with the columns `order_id`, `title`, `line_total`, where
`line_total = ROUND(qty * unit_price, 2)` (use the price stored on the line, not `books.price`). Sort by
`order_id`, then `title` A to Z. The order is checked.

**Example.** For dataset A, order 1 has the lines `Data Basics 39.0` and `Quiet Rivers 25.0` (2 x 12.50).
