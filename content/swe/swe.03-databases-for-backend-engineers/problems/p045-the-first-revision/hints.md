## Hint 1

`alembic.op` has an operation for each schema change: one creates a table, one drops it. Which ones? Alembic also needs the column types from `sqlalchemy`.

## Hint 2

`op.create_table("name", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("name", sa.String(100), nullable=False), ...)`. The downgrade is the mirror image: `op.drop_table("name")`.

## Hint 3

```text
upgrade_0001: op.create_table("products", Column id Integer PK, Column name String(100) NOT NULL, Column price_paise Integer NOT NULL)
downgrade_0001: op.drop_table("products")
```
