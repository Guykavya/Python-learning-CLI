# What does this DELETE remove?

Chapter section 4.5. A SQLite database with foreign keys **on** has this schema:

```sql
CREATE TABLE customers   (id INTEGER PRIMARY KEY);
CREATE TABLE orders      (id INTEGER PRIMARY KEY,
                          customer_id INTEGER NOT NULL REFERENCES customers(id) ON DELETE CASCADE);
CREATE TABLE order_lines (id INTEGER PRIMARY KEY,
                          order_id INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE);
CREATE TABLE tickets     (id INTEGER PRIMARY KEY,
                          customer_id INTEGER REFERENCES customers(id) ON DELETE SET NULL);
CREATE TABLE invoices    (id INTEGER PRIMARY KEY,
                          order_id INTEGER NOT NULL REFERENCES orders(id) ON DELETE RESTRICT);
```

and this data (`table: id (parent)`):

```text
customers:    1, 2
orders:       10 (customer 1), 11 (customer 1), 12 (customer 2)
order_lines:  1 (order 10), 2 (order 10), 3 (order 11), 4 (order 12)
tickets:      1 (customer 1), 2 (customer 2), 3 (customer 1)
invoices:     1 (order 12)
```

Four statements run **one after the other** (a refused statement changes nothing):

```text
1. DELETE FROM customers WHERE id = 1;
2. DELETE FROM orders WHERE id = 12;
3. DELETE FROM invoices WHERE id = 1;
4. DELETE FROM orders WHERE id = 12;
```

After each statement write the **number of rows in each table**, in this form:

```text
1: customers=<n> orders=<n> lines=<n> tickets=<n> invoices=<n>
```

If the statement fails, write `2: error` (use the statement's number). Do not run it.

## After you answer

1. After statement 1, which tickets still exist, and what is in their `customer_id`?
2. Why does statement 2 fail, and why does statement 4 work?
3. Which delete rule would you choose for `invoices`: why not `CASCADE`?
