# EXISTS and NOT EXISTS

`EXISTS (subquery)` is true when the subquery returns **at least one row**. What the subquery selects does not matter (people write
`SELECT 1`). Because the subquery can look at the outer row, you can ask "does this customer have a matching row?" directly.

```sql
CREATE TABLE customers (customer_id INTEGER PRIMARY KEY, name TEXT NOT NULL, city TEXT);
INSERT INTO customers VALUES (1,'Asha','Pune'),(2,'Bala','Delhi'),(3,'Chitra',NULL),(4,'Dev','Pune');
CREATE TABLE books (book_id INTEGER PRIMARY KEY, title TEXT NOT NULL, category TEXT, price REAL NOT NULL);
INSERT INTO books VALUES
 (1,'Dune','fiction',10.0),(2,'Emma','fiction',6.0),(3,'SQL Basics','tech',30.0),
 (4,'Python Deep','tech',40.0),(5,'Cooking','food',15.0),(6,'Algorithms','tech',50.0);
INSERT INTO books VALUES (7,'Poetry','fiction',8.0);
CREATE TABLE orders (order_id INTEGER PRIMARY KEY, customer_id INTEGER, ordered TEXT, status TEXT);
INSERT INTO orders VALUES
 (101,1,'2024-01-05','shipped'),(102,1,'2024-02-10','shipped'),(103,4,'2024-02-11','cancelled'),
 (104,2,'2024-03-01','shipped'),(105,3,'2024-03-15','shipped');
CREATE TABLE order_items (order_id INTEGER, book_id INTEGER, qty INTEGER, unit_price REAL, PRIMARY KEY (order_id, book_id));
INSERT INTO order_items VALUES
 (101,1,2,10.0),(101,3,1,30.0),(102,4,1,40.0),(103,5,1,15.0),
 (104,2,3,6.0),(104,3,1,30.0),(105,6,1,50.0),(105,3,1,28.0);
```

Write two queries, both ordered as stated:

- `QUERY_A`: customers (`name`) who have **at least one order with status `'shipped'`**, ordered by `name`. Use `EXISTS`.
- `QUERY_B`: books (`title`) that **were never ordered** (no row in `order_items`), ordered by `title`. Use `NOT EXISTS`.

**Example.** In the data above Dev only has a cancelled order, so `QUERY_A` gives Asha, Bala, Chitra. Book 7 `Poetry`
appears in no order line, so `QUERY_B` gives just `Poetry`.
