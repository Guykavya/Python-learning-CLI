## Approach

The child table carries the foreign key. Put `REFERENCES customers(customer_id) ON DELETE CASCADE` on the child column.

## Code

```python
SCRIPT = """
CREATE TABLE customers (
  customer_id INTEGER PRIMARY KEY,
  name TEXT NOT NULL
);
CREATE TABLE orders (
  order_id INTEGER PRIMARY KEY,
  customer_id INTEGER NOT NULL REFERENCES customers(customer_id) ON DELETE CASCADE,
  ordered TEXT NOT NULL
);
"""
```

## Complexity

Each insert into `orders` does a lookup in the parent's primary key (cheap). A cascade delete must find the child rows: without an index on `orders.customer_id` this scans the child table, so index foreign key columns in big tables.

## Another way / portable SQL

Table-level form: `FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE`. PostgreSQL and MySQL (InnoDB) check foreign keys always; SQLite needs the PRAGMA per connection. Other delete rules: `RESTRICT`, `SET NULL`, `NO ACTION`.
