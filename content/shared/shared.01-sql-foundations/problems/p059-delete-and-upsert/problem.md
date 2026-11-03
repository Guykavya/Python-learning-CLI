# DELETE, then UPSERT

An *upsert* means "insert, or if the key already exists, update instead". In SQLite and PostgreSQL:

```sql
INSERT INTO stock (book_id, qty) VALUES (1, 5)
ON CONFLICT (book_id) DO UPDATE SET qty = qty + excluded.qty;
```

`excluded` is the row you tried to insert; a bare `qty` is the row that is already in the table. `DELETE FROM t WHERE condition` removes matching rows (no `WHERE` removes all of them).

The test runs your `SCRIPT` on a database like this (other data is used too):

```sql
CREATE TABLE stock (book_id INTEGER PRIMARY KEY, qty INTEGER NOT NULL);
CREATE TABLE incoming (book_id INTEGER, qty INTEGER);
INSERT INTO stock VALUES (1,10),(2,0),(3,4);
INSERT INTO incoming VALUES (1,5),(2,3),(4,7),(4,1);
```

Write `SCRIPT` so that:

1. Books that are out of stock (`qty = 0`) are first **deleted** from `stock`.
2. Then all deliveries in `incoming` are added: a book already in `stock` has its quantity increased; a book not in `stock` is inserted. A book may appear several times in `incoming`: add them all up (use `GROUP BY book_id`).

**Example**

Final `stock` for the data above: `(1,15)`, `(2,3)`, `(3,4)`, `(4,8)`.
Book 2 was deleted (qty 0) and then re-inserted with 3; book 4 arrived twice (7 + 1).
