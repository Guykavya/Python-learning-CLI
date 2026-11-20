## Approach

```python
from alembic import op
import sqlalchemy as sa


def upgrade_0001():
    op.create_table(
        "products",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("price_paise", sa.Integer(), nullable=False),
    )


def downgrade_0001():
    op.drop_table("products")
```

`op` works inside the migration context that Alembic sets up when it runs the revision: it knows the connection and the database dialect. `downgrade` is the exact inverse of `upgrade`, so you can go back one step at any time. Alembic records the current revision in the table `alembic_version`, which is why that table remains after `downgrade base` (it is empty).

Example: `alembic upgrade head` runs `upgrade()` of revision `0001`; `alembic downgrade base` runs its `downgrade()`.

## Complexity

Not applicable.

## Another way

`op.execute("CREATE TABLE ...")` also works, but then the migration is tied to one database's SQL; `op.create_table` is portable (and batch mode, problem 46, relies on it).

## Why it matters

A migration is code that changes production data: it must be versioned, reviewable, repeatable on every environment and reversible. This is the first brick.
