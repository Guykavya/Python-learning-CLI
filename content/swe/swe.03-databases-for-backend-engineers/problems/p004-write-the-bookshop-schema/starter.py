SCHEMA = """
CREATE TABLE customers (id INTEGER PRIMARY KEY, email TEXT, name TEXT);
CREATE TABLE books (id INTEGER PRIMARY KEY, title TEXT, price_paise INTEGER);
CREATE TABLE orders (id INTEGER PRIMARY KEY, customer_id INTEGER, placed_at TEXT);
CREATE TABLE order_lines (order_id INTEGER, book_id INTEGER, qty INTEGER, price_paise INTEGER);
-- TODO: add the constraints (NOT NULL, UNIQUE, CHECK, REFERENCES, PRIMARY KEY (order_id, book_id))
"""
