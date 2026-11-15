## Approach

Follow the evaluation order.

1. `FROM books`: 7 rows.
2. `WHERE price > 10`: removes B (8.0) and E (9.0). Left: A 12.0, C 15.0 (fiction); D 30.0 (tech); F 11.0, G 14.0 (food).
3. `GROUP BY category`: fiction has 2 rows (max 15.0), tech has 1 row (max 30.0), food has 2 rows (max 14.0).
4. `HAVING COUNT(*) >= 2`: tech has only 1 row left, so the tech group disappears.
5. `ORDER BY category`: fiction, food.

## Code

```
fiction|2|15.0
food|2|14.0
```

## Complexity

Not applicable to a trace, but note the cost lesson: filtering with `WHERE` first means fewer rows to group. Without the `WHERE`, fiction would have 3 rows and tech 2, so tech would survive `HAVING`.

## Another way / portable SQL

Run it with `sqlite3` or Python's `sqlite3` module to confirm. The evaluation order is the same in MySQL and PostgreSQL.
