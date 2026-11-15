# Relational division: customers who bought every tech book

"For **all**" questions are the hardest in SQL, because SQL has no `FOR ALL`. The trick: *customers for whom there is **no**
tech book that they have **not** bought*. Or: customers whose number of *different* tech books bought equals the number of tech books.

```sql
CREATE TABLE customers (customer_id INTEGER PRIMARY KEY, name TEXT NOT NULL, city TEXT);
INSERT INTO customers VALUES (1,'Asha','Pune'),(2,'Bala','Delhi'),(3,'Chitra',NULL),(4,'Dev','Pune');
CREATE TABLE books (book_id INTEGER PRIMARY KEY, title TEXT NOT NULL, category TEXT, price REAL NOT NULL);
INSERT INTO books VALUES
 (1,'Dune','fiction',10.0),(2,'Emma','fiction',6.0),(3,'SQL Basics','tech',30.0),
 (4,'Python Deep','tech',40.0),(5,'Cooking','food',15.0),(6,'Algorithms','tech',50.0);
CREATE TABLE orders (order_id INTEGER PRIMARY KEY, customer_id INTEGER, ordered TEXT, status TEXT);
INSERT INTO orders VALUES (101,1,'2024-01-05','shipped'),(102,1,'2024-02-10','shipped'),(103,4,'2024-02-11','shipped'),(104,2,'2024-03-01','shipped'),(105,3,'2024-03-15','shipped'),(106,1,'2024-04-01','shipped');
CREATE TABLE order_items (order_id INTEGER, book_id INTEGER, qty INTEGER, unit_price REAL, PRIMARY KEY (order_id, book_id));
INSERT INTO order_items VALUES (101,1,2,10.0),(101,3,1,30.0),(102,4,1,40.0),(103,5,1,15.0),(104,3,1,30.0),(105,6,1,50.0),(105,3,1,28.0),(106,6,1,50.0);
```

Return the names of customers who have bought **every** book of category `'tech'` (they may have bought the books in different
orders, and any order status counts). Column `name`, ordered by `name`.

**Example.** Tech books are 3, 4 and 6. Asha bought 3 (order 101), 4 (order 102) and 6 (order 106): all three, but in three
different orders. Chitra bought 3 and 6 but not 4. Bala only 3. Dev no tech book. Result: `Asha`.
Customers with no tech purchases at all must not appear.
