# A first CTE: units sold per book

A **CTE** (common table expression) gives a name to a subquery so the main query can use it like a table:
`WITH name AS (SELECT ...) SELECT ... FROM name`. It reads top to bottom: first the helper, then the answer.

```sql
CREATE TABLE books (book_id INTEGER PRIMARY KEY, title TEXT NOT NULL, category TEXT, price REAL NOT NULL);
INSERT INTO books VALUES
 (1,'Dune','fiction',10.0),(2,'Emma','fiction',6.0),(3,'SQL Basics','tech',30.0),
 (4,'Python Deep','tech',40.0),(5,'Cooking','food',15.0),(6,'Algorithms','tech',50.0);
CREATE TABLE order_items (order_id INTEGER, book_id INTEGER, qty INTEGER, unit_price REAL, PRIMARY KEY (order_id, book_id));
INSERT INTO order_items VALUES
 (101,1,2,10.0),(101,3,1,30.0),(102,4,1,40.0),(103,5,1,15.0),
 (104,2,3,6.0),(104,3,1,30.0),(105,6,1,50.0),(105,3,1,28.0);
```

Define a CTE `book_sales` with one row per ordered book: `book_id` and `units` (sum of `qty`). Then join it to `books` and return
the books that sold **at least 2 units**:

| column | meaning |
|---|---|
| `title` | book title |
| `units` | units sold |

Order: `units` descending, then `title` ascending. Books never ordered have no row in `book_sales` and do not appear.

**Example.** For the data above: Emma 3 units (one line), SQL Basics 3 units (three lines of 1), Dune 2. Result: Emma 3,
SQL Basics 3, Dune 2.
