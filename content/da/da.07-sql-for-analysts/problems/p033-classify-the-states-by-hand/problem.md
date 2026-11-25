# Classify the states by hand

Chapter section 8.1. The table `act` holds the months (1 to 4) in which each of four users was active. The rules of the chapter,
for a month `m`:

| State in month `m` | Definition |
|---|---|
| **new** | active in `m`, and `m` is the first month the user was ever active |
| **retained** | active in `m` and also active in `m - 1` |
| **resurrected** | active in `m`, not active in `m - 1`, but active before that |
| **churned** | active in `m - 1` and **not** active in `m` |

```python
import duckdb

con = duckdb.connect()
con.execute("CREATE TABLE act (user_id INTEGER, m INTEGER)")       # one row per user and active month (months 1 to 4)
con.execute("""INSERT INTO act VALUES (1, 1), (1, 2), (1, 3), (1, 4), (2, 1), (2, 3), (3, 2), (3, 4), (4, 3)""")

rows = con.execute("""
    WITH x AS (SELECT user_id, m, lag(m) OVER (PARTITION BY user_id ORDER BY m) AS prev FROM act),
    s AS (SELECT m, CASE WHEN prev IS NULL THEN 'new' WHEN prev = m - 1 THEN 'retained' ELSE 'resurrected' END AS state FROM x),
    c AS (SELECT m + 1 AS m, 'churned' AS state FROM act a
          WHERE m + 1 <= 4 AND NOT EXISTS (SELECT 1 FROM act b WHERE b.user_id = a.user_id AND b.m = a.m + 1))
    SELECT m,
           count(*) FILTER (WHERE state = 'new'),
           count(*) FILTER (WHERE state = 'retained'),
           count(*) FILTER (WHERE state = 'resurrected'),
           count(*) FILTER (WHERE state = 'churned')
    FROM (SELECT * FROM s UNION ALL SELECT * FROM c)
    GROUP BY m ORDER BY m
""").fetchall()

for r in rows:
    print(*r)
print([a + b + c for _, a, b, c, _ in rows])
```

Hand-trace the program, then write **every line it prints**, in order, in `answer.txt`. The first four lines hold five numbers
each: `m new retained resurrected churned`. The last line is a list.

Do not run the code before you have written your answer.

## Example

For a single user active in months 1 and 3 only, month 1 would count one `new`, month 2 one `churned`, and month 3 one
`resurrected`; the last line would be the list of `new + retained + resurrected` per month.

## After you answer

- The last line is MAU per month. Check on paper that `MAU(m-1) = retained(m) + churned(m)` for months 2, 3 and 4.
- Why is user 2 `churned` in month 2 and `resurrected` in month 3, not `retained`?
- Why is `m + 1 <= 4` in the churn part, and what would it add for month 5?
