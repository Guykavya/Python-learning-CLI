## Approach

All three use placeholders. `lastrowid` of the cursor gives the new id. `fetchone()` returns `None` when no row matches, exactly what `find_customer` needs. For the optional category, `(:category IS NULL OR category = :category)` turns the filter off when the value is `None`.

## Code

```python
def add_customer(con, name, city):
    cur = con.execute("INSERT INTO customers (name, city) VALUES (?, ?)", (name, city))
    con.commit()
    return cur.lastrowid


def find_customer(con, name):
    return con.execute(
        "SELECT customer_id, name, city FROM customers WHERE name = :name ORDER BY customer_id LIMIT 1",
        {"name": name},
    ).fetchone()


def books_between(con, low, high, category=None):
    rows = con.execute(
        """SELECT title FROM books
           WHERE price BETWEEN :low AND :high
             AND (:category IS NULL OR category = :category)
           ORDER BY price, title""",
        {"low": low, "high": high, "category": category},
    ).fetchall()
    return [title for (title,) in rows]
```

## Complexity

Insert and lookup by name: O(log n) with an index, otherwise a scan O(n). SQLite also caches the compiled statement for the same SQL text, so repeated calls with different values are cheap.

## Another way / portable SQL

PostgreSQL's `psycopg` uses `%s` / `%(name)s` placeholders, MySQL connectors `%s`; SQLite also accepts `?1` numbered and `@name` / `$name`. The idea is identical in every driver. Values can be parameters; **table and column names cannot** (see p067).
