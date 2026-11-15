# HAVING: prolific authors

`WHERE` filters **rows** before grouping. `HAVING` filters **groups** after the aggregates are computed. A condition on
`COUNT(*)` or `SUM(...)` can only go in `HAVING`.

```sql
CREATE TABLE books (book_id INTEGER PRIMARY KEY, title TEXT, author_id INTEGER, price REAL);
INSERT INTO books VALUES (1,'Dune',1,10.0),(2,'Emma',2,6.0),(3,'SQL Basics',3,30.0),(4,'Python Deep',3,40.0),(5,'Cooking',4,15.0),(6,'Poems',2,7.0),(7,'Notes',3,12.0);
```

Return the authors (by `author_id`) who wrote **at least 2** books, with how many they wrote:

| column | meaning |
|---|---|
| `author_id` | the author |
| `n_books` | number of books |

Most books first; break ties by `author_id` ascending.

**Example.** For the data above: author 3 has 3 books, author 2 has 2, author 1 and 4 have 1 each, so the result is
`(3, 3)` then `(2, 2)`.
