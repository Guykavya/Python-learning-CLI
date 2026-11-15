## Hint 1

Which table is the parent, and which is the child? Which table is created first? What word introduces the table and column a foreign key points at, and where does the delete rule go?

## Hint 2

```
CREATE TABLE customers (...);
CREATE TABLE orders (
  order_id INTEGER PRIMARY KEY,
  customer_id INTEGER NOT NULL REFERENCES customers(customer_id) <delete rule>,
  ordered TEXT NOT NULL
);
```
