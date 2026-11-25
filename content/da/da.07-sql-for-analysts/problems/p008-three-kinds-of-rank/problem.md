# Three kinds of rank

Chapter section 4.2. The three ranking functions differ only in what they do with **ties**: `row_number` never repeats (it needs a
tie-break to be reproducible), `rank` repeats and then **skips** numbers, `dense_rank` repeats and does **not** skip.
`ntile(n)` cuts the ordered rows into `n` groups of (nearly) equal size.

```python
import duckdb

con = duckdb.connect()
con.execute("CREATE TABLE o (order_id INTEGER, amount INTEGER)")
con.execute("INSERT INTO o VALUES (1, 300), (2, 500), (3, 500), (4, 200), (5, 100), (6, 400)")

rows = con.execute("""
    SELECT order_id, amount,
           row_number() OVER (ORDER BY amount DESC, order_id) AS rn,
           rank()       OVER (ORDER BY amount DESC)           AS rk,
           dense_rank() OVER (ORDER BY amount DESC)           AS dr,
           ntile(2)     OVER (ORDER BY amount DESC, order_id) AS half
    FROM o
    ORDER BY amount DESC, order_id
""").fetchall()

for r in rows:
    print(*r)
print(max(r[3] for r in rows), max(r[4] for r in rows))
```

Hand-trace the program, then write **every line it prints**, in order, in `answer.txt`. Each row prints its six values separated
by single spaces.

Do not run the code before you have written your answer.

## Example

For three orders with amounts 90, 90 and 50 (ids 1, 2, 3) in the same windows, the printed rows would be
`1 90 1 1 1 1`, `2 90 2 1 1 1` and `3 50 3 3 2 2` (with `ntile(2)` putting 2 rows in the first half and 1 in the second).

## After you answer

- Which two orders tie, and what do `rn`, `rk`, `dr` say about them? What number does `rk` jump to after the tie, and why?
- Why does `row_number` need `order_id` in its `ORDER BY` while `rank` does not?
- `ntile(2)` of 6 rows: how many rows per half? What would 7 rows give?
