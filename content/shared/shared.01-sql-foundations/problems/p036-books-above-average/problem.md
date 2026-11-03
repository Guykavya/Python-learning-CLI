# Books above the average price

A **scalar subquery** is a `SELECT` in parentheses that returns exactly one value. You can use it where a value is
expected, for example on the right of `>`.

```sql
CREATE TABLE books (book_id INTEGER PRIMARY KEY, title TEXT NOT NULL, price REAL NOT NULL);
INSERT INTO books VALUES (1,'Dune',10.0),(2,'Emma',6.0),(3,'SQL Basics',30.0),(4,'Python Deep',40.0),(5,'Cooking',15.0),(6,'Algorithms',50.0);
```

Return the books whose price is **strictly greater** than the average price of all books:

| column | meaning |
|---|---|
| `title` | book title |
| `price` | its price |

Order: price descending (no ties in the examples, but add `title` as a second key).

**Example.** The average of the data above is 151 / 6 = 25.17, so the result is Algorithms 50.0, Python Deep 40.0, SQL Basics 30.0.
Do not hard-code 25.17: the test uses other data.
