SCHEMA = """
CREATE TABLE customers (
    id    INTEGER PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    name  TEXT NOT NULL
);
CREATE TABLE books (
    id          INTEGER PRIMARY KEY,
    title       TEXT NOT NULL,
    price_paise INTEGER NOT NULL CHECK (price_paise >= 0)
);
CREATE TABLE orders (
    id          INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(id),
    placed_at   TEXT NOT NULL
);
CREATE TABLE order_lines (
    order_id    INTEGER NOT NULL REFERENCES orders(id),
    book_id     INTEGER NOT NULL REFERENCES books(id),
    qty         INTEGER NOT NULL CHECK (qty > 0),
    price_paise INTEGER NOT NULL CHECK (price_paise >= 0),
    PRIMARY KEY (order_id, book_id)
);
"""
