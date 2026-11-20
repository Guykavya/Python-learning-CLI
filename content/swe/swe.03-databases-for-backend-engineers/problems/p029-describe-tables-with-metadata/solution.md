## Approach

```python
from sqlalchemy import Column, ForeignKey, Integer, String, Table


def make_tables(metadata):
    customers = Table(
        "customers", metadata,
        Column("id", Integer, primary_key=True),
        Column("name", String(100), nullable=False),
        Column("city", String(50)),
        Column("email", String(200), nullable=False, unique=True),
    )
    orders = Table(
        "orders", metadata,
        Column("id", Integer, primary_key=True),
        Column("customer_id", Integer, ForeignKey("customers.id"), nullable=False),
        Column("total_paise", Integer, nullable=False),
        Column("status", String(20), nullable=False, server_default="open"),
    )
    return customers, orders
```

A `Table` is a **description**: nothing is created in the database until `metadata.create_all(engine)`, which emits `CREATE TABLE` (parents before children, because the foreign key tells the order). `server_default` puts the default **in the database** (`DEFAULT 'open'`), so it works for inserts from any program, unlike `default=` which is applied by SQLAlchemy only.

Example: `orders.insert().values(customer_id=1, total_paise=500)` leaves out `status`; the database fills in `'open'`.

## Complexity

Not applicable.

## Another way

The ORM (section 9) describes the same tables with classes and `Mapped[...]` annotations. Core tables are the base layer that the ORM builds on.

## Why it matters

One Python description feeds `create_all`, queries and migrations. Types, nullability and uniqueness written here become the constraints of problem 4, in the database.
