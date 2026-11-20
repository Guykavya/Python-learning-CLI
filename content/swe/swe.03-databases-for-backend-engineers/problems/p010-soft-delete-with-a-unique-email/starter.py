SCHEMA = """
CREATE TABLE customers (
    id         INTEGER PRIMARY KEY,
    email      TEXT NOT NULL UNIQUE,
    name       TEXT NOT NULL,
    deleted_at TEXT
);
-- TODO: replace the plain UNIQUE by a partial unique index; add the view active_customers
"""
