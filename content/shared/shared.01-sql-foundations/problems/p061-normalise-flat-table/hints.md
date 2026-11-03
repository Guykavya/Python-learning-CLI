## Hint 1

Which columns of the flat table describe a customer? Which describe a book? Which describe a single purchase? What identifies each of those things so that a line can point to it?

## Hint 2

```
CREATE TABLE customers (customer_id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE, city TEXT);
CREATE TABLE books (...);
CREATE TABLE lines (line_id INTEGER PRIMARY KEY, order_id ..., customer_id ... REFERENCES customers(customer_id), book_id ... REFERENCES books(book_id), qty ...);
INSERT INTO customers (name, city) SELECT DISTINCT ... FROM orders_flat;
INSERT INTO books (title, price) SELECT DISTINCT ... FROM orders_flat;
INSERT INTO lines (...) SELECT ... FROM orders_flat f JOIN customers c ON ... JOIN books b ON ...;
```
