# Trace: the default window frame with ties

When a window has `ORDER BY` but no frame clause, the frame is `RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW`.
`RANGE` treats all rows with the same `ORDER BY` value (the *peers*) as "the current row" together. `ROWS` counts physical rows one by one.
Without `ORDER BY`, the frame is the whole partition.

Predict the exact output of this script on SQLite. Rows are shown ordered by `id`.

```sql
CREATE TABLE sales (id INTEGER PRIMARY KEY, amount INTEGER);
INSERT INTO sales VALUES (1,10),(2,20),(3,20),(4,30),(5,30),(6,40);

SELECT id, amount,
       SUM(amount) OVER (ORDER BY amount)                                    AS dflt,
       SUM(amount) OVER (ORDER BY amount, id ROWS UNBOUNDED PRECEDING)       AS by_rows,
       COUNT(*)    OVER (ORDER BY amount)                                    AS cnt,
       SUM(amount) OVER ()                                                   AS total
FROM sales
ORDER BY id;
```

Columns of the result: `id|amount|dflt|by_rows|cnt|total`.

Write your answer in `answer.txt`: one line per result row, column values joined with `|` (no spaces), `NULL` for a NULL,
no header line, strings without quotes. If the query returns no rows, write the single line `(no rows)`.

**Example (a different query)**

```sql
CREATE TABLE t (x INTEGER);
INSERT INTO t VALUES (1),(1),(5);
SELECT x, SUM(x) OVER (ORDER BY x) FROM t ORDER BY x, 2;
```

The two `1` rows are peers, so each sees both of them: the answer lines are `1|2`, `1|2`, `5|7`.
