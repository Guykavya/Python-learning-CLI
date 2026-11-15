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
