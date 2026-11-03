## Hint 1

For `add_books`: which context manager commits on success and rolls back on an error, so that a failing second row also removes the first? Does `executemany` already give you a count?

For `average_by_category`: `with sqlite3.connect(...)` is not enough. Why? Which helper from `contextlib` guarantees `.close()`?

## Hint 2

```
add_books:   with con: con.executemany("INSERT ...", rows); return len(rows)
books_as_dicts: old = con.row_factory; con.row_factory = sqlite3.Row; try: ...; finally: con.row_factory = old
average_by_category: with closing(sqlite3.connect(db_path)) as con: SELECT category, ROUND(AVG(price), 2) ... GROUP BY category
```
