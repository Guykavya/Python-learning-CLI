## Approach

```python
from sqlalchemy import Column, Integer, MetaData, String, Table, delete, insert, select, update

metadata = MetaData()
customers = Table(
    "customers", metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(100), nullable=False),
    Column("city", String(50)),
)


def add_many(engine, rows):
    if not rows:
        return 0
    with engine.begin() as conn:
        return conn.execute(insert(customers), rows).rowcount


def by_city(engine, city):
    with engine.connect() as conn:
        return list(conn.scalars(select(customers.c.name).where(customers.c.city == city).order_by(customers.c.name)))


def rename(engine, customer_id, new_name):
    with engine.begin() as conn:
        return conn.execute(update(customers).where(customers.c.id == customer_id).values(name=new_name)).rowcount


def remove(engine, customer_id):
    with engine.begin() as conn:
        return conn.execute(delete(customers).where(customers.c.id == customer_id)).rowcount
```

`engine.begin()` opens a transaction and commits when the `with` block ends normally (or rolls back on an exception): the statements of `add_many` succeed or fail together. A plain `engine.connect()` is enough for reads. `conn.scalars(...)` returns the first column of every row, so `by_city` gives a list of names.

Example: `rename(engine, 99, "X")` matches no row, so `rowcount` is 0 and nothing changes.

## Complexity

One statement per call (`add_many` sends one `executemany`).

## Another way

`session.add_all(...)` in the ORM (section 9) does the same with objects. Core is the right level for bulk inserts and simple statements.

## Why it matters

Statements built from objects are safe from injection (problem 32) and portable between databases; `engine.begin()` makes "commit or roll back" automatic.
