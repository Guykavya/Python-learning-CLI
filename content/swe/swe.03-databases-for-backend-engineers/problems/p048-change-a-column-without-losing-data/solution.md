## Approach

```python
from alembic import op
import sqlalchemy as sa

BATCH = 500


def upgrade_0002():
    """EXPAND: add the new column; old code keeps working."""
    with op.batch_alter_table("products") as batch:
        batch.add_column(sa.Column("price_paise", sa.Integer(), nullable=True))


def downgrade_0002():
    with op.batch_alter_table("products") as batch:
        batch.drop_column("price_paise")


def upgrade_0003():
    """BACKFILL in batches: each UPDATE touches at most BATCH rows."""
    bind = op.get_bind()
    while True:
        result = bind.execute(sa.text(
            "UPDATE products SET price_paise = CAST(ROUND(price * 100) AS INTEGER) "
            "WHERE id IN (SELECT id FROM products WHERE price_paise IS NULL AND price IS NOT NULL LIMIT :n)"),
            {"n": BATCH})
        if result.rowcount == 0:
            break


def downgrade_0003():
    op.execute("UPDATE products SET price_paise = NULL")


def upgrade_0004():
    """CONTRACT: the new column becomes required, the old one disappears."""
    with op.batch_alter_table("products") as batch:
        batch.alter_column("price_paise", existing_type=sa.Integer(), nullable=False)
        batch.drop_column("price")


def downgrade_0004():
    with op.batch_alter_table("products") as batch:
        batch.add_column(sa.Column("price", sa.Float(), nullable=True))
        batch.alter_column("price_paise", existing_type=sa.Integer(), nullable=True)
    op.execute("UPDATE products SET price = price_paise / 100.0")
```

Each revision is safe on its own **and** reversible:

- **0002 (expand)** only adds; every old query still works.
- **0003 (backfill)** copies the data in **batches**: a single `UPDATE` of ten million rows would hold a lock for a long time and bloat the log; 500 rows at a time keep each statement short. The loop ends when no row is left to update (`rowcount == 0`). Between the revisions the application can be redeployed to write **both** columns.
- **0004 (contract)** is the only destructive step; it runs after every writer uses the new column.

`ROUND(price * 100)` fixes the floating-point noise (`99.99 * 100` is `9999.000000000002`), and `CAST(... AS INTEGER)` stores an integer. The downgrade of 0004 rebuilds the rupee column by dividing by `100.0`: `1230 / 100.0` is exactly the double `12.3` again, so the original values return.

Example: the row `("Green Tea", 12.30)` becomes `price_paise = 1230` at 0003, loses `price` at 0004, and gets `price = 12.3` back on the way down.

## Complexity

`O(rows)` in `ceil(rows / 500)` statements.

## Another way

A single revision with `ALTER TABLE ... ALTER COLUMN price TYPE integer USING round(price * 100)` works on PostgreSQL, but locks the table while it rewrites it, and cannot be mixed with old code. Expand-contract trades more steps for no downtime.

## Why it matters

Changing the shape of data in a live system is where outages happen. Splitting the change so that **every intermediate state works with both the old and the new code** is the habit that avoids them.
