## Hint 1

You met `INSERT ... ON CONFLICT (id) DO UPDATE SET ...` in shared.01. Inside the `DO UPDATE`
part, `excluded.col` is the value you tried to insert and `orders.col` is the value already in
the table. Which condition on those two `updated_at` values says "the incoming row is newer"?
Where in the statement can you put that condition?

## Hint 2

`DO UPDATE` accepts its own `WHERE`. When the `WHERE` is false the row is left alone and is
**not** counted in `cursor.rowcount`. `executemany` with named parameters takes the list of
dicts directly.

```
CREATE TABLE IF NOT EXISTS orders (...)
with conn:                                   # commits at the end
    cur = conn.executemany(
        INSERT INTO orders (...) VALUES (:id, :status, :amount, :updated_at)
        ON CONFLICT (id) DO UPDATE SET status = excluded.status, ... , updated_at = excluded.updated_at
        WHERE excluded.updated_at > orders.updated_at,
        rows)
return cur.rowcount
```
