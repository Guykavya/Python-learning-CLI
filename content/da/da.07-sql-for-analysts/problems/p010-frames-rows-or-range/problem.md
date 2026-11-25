# Frames: rows or range?

Chapter section 4.4. A **frame** says which rows around the current row a window function may see.

- `ROWS BETWEEN 1 PRECEDING AND CURRENT ROW`: the previous **row** and this one (by position).
- `RANGE BETWEEN 1 PRECEDING AND CURRENT ROW`: every row whose `ORDER BY` **value** lies between (value - 1) and the current value, so
  rows with the same value (**peers**) are all included.
- With an `ORDER BY` and no frame clause the default is `RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW`: from the first
  row up to the current row **and all its peers**.

The table has two rows on day 2 (ids 2 and 3) and a gap (no day 4).

```python
import duckdb

con = duckdb.connect()
con.execute("CREATE TABLE t (id INTEGER, day INTEGER, amount INTEGER)")
con.execute("INSERT INTO t VALUES (1, 1, 10), (2, 2, 20), (3, 2, 30), (4, 3, 40), (5, 5, 50)")

rows = con.execute("""
    SELECT id, day, amount,
           sum(amount) OVER (ORDER BY day, id ROWS BETWEEN 1 PRECEDING AND CURRENT ROW)  AS rows_sum,
           sum(amount) OVER (ORDER BY day RANGE BETWEEN 1 PRECEDING AND CURRENT ROW)    AS range_sum,
           sum(amount) OVER (ORDER BY day)                                             AS default_sum
    FROM t
    ORDER BY id
""").fetchall()

for r in rows:
    print(*r)
```

Hand-trace the program, then write **every line it prints**, in order, in `answer.txt`. Each line holds six numbers separated by
single spaces: `id day amount rows_sum range_sum default_sum`.

Do not run the code before you have written your answer.

## Example

For rows `(1, day 1, 10)` and `(2, day 2, 20)` only, the line for id 2 would be `2 2 20 30 30 30`: both windows reach back to day 1.

## After you answer

- Why do ids 2 and 3 have the same `range_sum` and the same `default_sum` but different `rows_sum`?
- Why is the `range_sum` of id 5 just 50, although the previous row (id 4) is only two rows away? What does `ROWS` give for the same row?
- When an analyst computes a "7-day moving sum" with `ROWS BETWEEN 6 PRECEDING`, what must be true of the table for 6 rows to mean 7 days?
