# Distinct users do not add up

Chapter section 5.2. A count of **distinct** users per day cannot be added over days: a user active on two days is counted twice
by the sum and once by the distinct count over the two days. The table `a` has one row per (user, day) sighting, and some rows
repeat.

```python
import duckdb

con = duckdb.connect()
con.execute("CREATE TABLE a (user_id INTEGER, day INTEGER)")
con.execute("INSERT INTO a VALUES (1, 1), (2, 1), (3, 1), (2, 2), (2, 2), (3, 2), (4, 2), (1, 3), (3, 3), (3, 3)")

per_day = con.execute("SELECT day, count(DISTINCT user_id) FROM a GROUP BY day ORDER BY day").fetchall()
print([n for _, n in per_day])
print(sum(n for _, n in per_day))
print(con.execute("SELECT count(DISTINCT user_id) FROM a").fetchall()[0][0])
print(con.execute("SELECT count(*) FROM a").fetchall()[0][0])
two_days = con.execute("SELECT count(DISTINCT user_id) FROM a WHERE day >= 2").fetchall()[0][0]
print(sum(n for d, n in per_day if d >= 2), two_days)
```

Hand-trace the program, then write **every line it prints**, in order, in `answer.txt`. A list prints as Python prints it
(`[1, 2]`).

Do not run the code before you have written your answer.

## Example

If `a` held only `(1, 1), (1, 2), (2, 2)`, the per-day distinct counts would be `[1, 2]`, their sum 3, but the distinct users over
both days only 2 (users 1 and 2).

## After you answer

- Which users are counted on more than one day, and what does each of them add to the *sum* of the daily counts?
- Why is `count(*)` (line 4) larger than the sum of the daily distinct counts?
- A dashboard shows "weekly active users" as the sum of seven DAU numbers. Is it too high or too low, and by how much does it differ here?
