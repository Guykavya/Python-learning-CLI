## Hint 1

Each statement is built with a function of `sqlalchemy` and executed on a connection. Which context manager gives you a connection that **commits** when the block ends?

## Hint 2

`conn.execute(insert(customers), rows)` with a list of dicts runs the insert for every dict. For `update` and `delete` the `where(...)` clause selects the rows; the result's `.rowcount` says how many changed.

## Hint 3

```text
add_many:  with engine.begin() as conn: return conn.execute(insert(customers), rows).rowcount
by_city:   with engine.connect() as conn: return list(conn.scalars(select(customers.c.name).where(...).order_by(...)))
rename/remove: update(...).where(customers.c.id == id).values(name=...) / delete(...).where(...) -> rowcount
```
