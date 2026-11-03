# UPDATE with WHERE and a subquery

`UPDATE t SET col = expr WHERE condition` changes the rows that match. Without `WHERE` it changes **every** row. A condition may contain a subquery.

The test runs your `SCRIPT` on a database like this (other data is used too):

```sql
CREATE TABLE books (book_id INTEGER PRIMARY KEY, title TEXT, category TEXT, price REAL);
CREATE TABLE customers (customer_id INTEGER PRIMARY KEY, name TEXT, tier TEXT NOT NULL DEFAULT 'basic');
CREATE TABLE orders (order_id INTEGER PRIMARY KEY, customer_id INTEGER, ordered TEXT, status TEXT);
INSERT INTO books VALUES (1,'Rust Basics','Tech',30),(2,'Tales','Fiction',10),(3,'Go Tour','Tech',20);
INSERT INTO customers (customer_id, name) VALUES (1,'Ada'),(2,'Bo'),(3,'Cy');
INSERT INTO orders VALUES (1,1,'2024-01-01','shipped'),(2,1,'2024-02-01','shipped'),(3,2,'2024-02-05','shipped');
```

Write `SCRIPT` with two `UPDATE` statements:

1. Raise the price of every book in category `'Tech'` by 10 percent, rounded to 2 decimals (`ROUND(price * 1.10, 2)`).
2. Set `tier = 'gold'` for every customer who has **two or more orders** (use a subquery with `GROUP BY ... HAVING`). Everyone else must stay `'basic'`.

**Example**

After the script on the data above: Rust Basics 33.0, Go Tour 22.0, Tales 10.0; Ada is `gold`, Bo and Cy `basic`.
