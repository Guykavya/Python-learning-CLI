## Approach

```python
from alembic import op
import sqlalchemy as sa


def upgrade_0002():
    with op.batch_alter_table("products") as batch:
        batch.add_column(sa.Column("slug", sa.String(200), nullable=True))
    bind = op.get_bind()
    for row_id, name in bind.execute(sa.text("SELECT id, name FROM products")).fetchall():
        slug = "-".join(name.lower().split())
        bind.execute(sa.text("UPDATE products SET slug = :slug WHERE id = :id"), {"slug": slug, "id": row_id})
    with op.batch_alter_table("products") as batch:
        batch.alter_column("slug", existing_type=sa.String(200), nullable=False)


def downgrade_0002():
    with op.batch_alter_table("products") as batch:
        batch.drop_column("slug")
```

The order matters: a column that must be `NOT NULL` is first added as nullable, then filled, and only then tightened. `"-".join(name.lower().split())` lower-cases and collapses any run of white space (and trims) in one expression. **Batch mode** is how Alembic changes SQLite tables: it creates a new table with the new definition, copies the rows, drops the old one and renames the new one (SQLite cannot `ALTER COLUMN`).

Example: rows `Green Tea`, `  Big   Mug `, `Cup` become `green-tea`, `big-mug`, `cup`, and the column becomes `NOT NULL`.

## Complexity

`O(rows)`; for millions of rows backfill in batches (problem 48).

## Another way

In one SQL statement: `UPDATE products SET slug = lower(replace(trim(name), ' ', '-'))` (does not collapse runs of spaces). PostgreSQL could use `ALTER COLUMN ... SET NOT NULL` directly, without batch mode.

## Why it matters

"Add a required column" is the most common schema change, and the naive version fails on any table that is not empty.
