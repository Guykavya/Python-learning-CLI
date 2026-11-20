SCHEMA = """
CREATE TABLE customers (
    id         INTEGER PRIMARY KEY,
    email      TEXT NOT NULL,
    name       TEXT NOT NULL,
    deleted_at TEXT
);
CREATE UNIQUE INDEX customers_live_email ON customers(email) WHERE deleted_at IS NULL;
CREATE VIEW active_customers AS
    SELECT id, email, name FROM customers WHERE deleted_at IS NULL;
"""
