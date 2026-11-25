# Top N per group

Chapter section 4.7. `QUALIFY` filters on a window function, the way `HAVING` filters on an aggregate: first the windows are
computed, then rows that fail the condition are dropped. `row_number() <= 2` keeps **exactly** two rows per group; `rank() <= 2`
keeps every row whose rank is 1 or 2, so **ties can make the group larger**.

```python
import duckdb

con = duckdb.connect()
con.execute("CREATE TABLE o (order_id INTEGER, country VARCHAR, amount INTEGER)")
con.execute("""INSERT INTO o VALUES (1, 'IN', 300), (2, 'IN', 500), (3, 'US', 200), (4, 'IN', 500), (5, 'UK', 100),
                                    (6, 'US', 250), (7, 'US', 250), (8, 'UK', 400), (9, 'IN', 100), (10, 'IN', 500)""")

top2 = con.execute("""
    SELECT order_id, country, amount FROM o
    QUALIFY row_number() OVER (PARTITION BY country ORDER BY amount DESC, order_id) <= 2
    ORDER BY country, amount DESC, order_id
""").fetchall()
for r in top2:
    print(*r)

ranked = con.execute("""
    SELECT order_id FROM o
    QUALIFY rank() OVER (PARTITION BY country ORDER BY amount DESC) <= 2
    ORDER BY order_id
""").fetchall()
print([r[0] for r in ranked])
print(len(top2), len(ranked))
```

Hand-trace the program, then write **every line it prints**, in order, in `answer.txt`. A list prints as Python prints it
(`[1, 2]`).

Do not run the code before you have written your answer.

## Example

If the table held only `(1, 'IN', 90)`, `(2, 'IN', 90)` and `(3, 'IN', 50)`, the first query would keep orders 1 and 2 (tie broken by
`order_id`) and the second would keep 1 and 2 too (both have rank 1); the third row has rank 3 and is dropped.

## After you answer

- Which `IN` orders are kept by `row_number`, and which by `rank`? Why does `rank` keep one more?
- Which of the two queries do you use for "the top 2 orders per country, always exactly two"? Which one for "everyone who is in the top two by amount"?
- Why does the first query need `order_id` in its window `ORDER BY`?
