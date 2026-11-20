## Approach

```python
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
```

Every rule is a **constraint** the database checks on every write, whichever program writes: the application cannot forget one. `NOT NULL` and `UNIQUE` protect the customer, `CHECK` protects the money and quantities, `REFERENCES` makes orphan rows impossible (when foreign keys are switched on, problem 8), and the composite primary key means a book appears once per order (a second purchase of the same book changes `qty`).

Example: `INSERT INTO order_lines VALUES (1, 1, 0, 100)` fails with `CHECK constraint failed`.

## Complexity

Not applicable.

## Another way

Name the constraints (`CONSTRAINT qty_positive CHECK (...)`) to get readable error names in PostgreSQL. SQLite keeps the expression in the message.

## Why it matters

Bugs in application code are certain; the database is the last line of defence. A constraint turns "someone inserted garbage six months ago" into an error today.
