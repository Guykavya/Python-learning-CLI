# Foreign keys and ON DELETE CASCADE

A **foreign key** says: "this column must hold an id that exists in another table". It stops orders for customers
that do not exist. `ON DELETE CASCADE` says: when the parent row is deleted, delete its child rows too.

SQLite checks foreign keys only if you run `PRAGMA foreign_keys = ON;` on the connection. The tests turn it on
before running your script, so do **not** put the PRAGMA in your script.

Write a `SCRIPT` that creates two tables (in this order):

- `customers(customer_id INTEGER PRIMARY KEY, name TEXT NOT NULL)`
- `orders(order_id INTEGER PRIMARY KEY, customer_id INTEGER NOT NULL, ordered TEXT NOT NULL)`
  where `orders.customer_id` is a foreign key to `customers(customer_id)` with `ON DELETE CASCADE`.

**Example (a different pair).** `CREATE TABLE pets (pet_id INTEGER PRIMARY KEY, owner_id INTEGER REFERENCES owners(owner_id));`
