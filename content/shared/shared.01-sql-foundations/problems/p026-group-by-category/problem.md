# Books per category

`GROUP BY` splits the rows into groups (one per value) and runs the aggregates once **per group**.

```sql
CREATE TABLE books (book_id INTEGER PRIMARY KEY, title TEXT, category TEXT, price REAL);
INSERT INTO books VALUES (1,'Dune','fiction',10.0),(2,'Emma','fiction',6.5),(3,'SQL Basics','tech',30.0),(4,'Python Deep','tech',40.0),(5,'Cooking','food',15.0);
```

Return one row per category with these columns:

| column | meaning |
|---|---|
| `category` | the category |
| `n_books` | number of books in it |
| `avg_price` | average price, rounded to 2 decimals (`ROUND(x, 2)`) |

Sort the rows by `category`, A to Z.

**Example.** For the data above the result is

| category | n_books | avg_price |
|---|---|---|
| fiction | 2 | 8.25 |
| food | 1 | 15.0 |
| tech | 2 | 35.0 |
