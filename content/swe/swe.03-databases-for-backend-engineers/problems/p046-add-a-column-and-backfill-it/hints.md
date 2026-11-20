## Hint 1

What would the database say if you added `slug` as `NOT NULL` at once to a table with three rows? So what do you do first, and what last?

## Hint 2

Step 2 needs the rows: `bind = op.get_bind()`, `bind.execute(sa.text("SELECT id, name FROM products"))`, then one `UPDATE ... SET slug = :slug WHERE id = :id` per row (or `executemany`).

## Hint 3

```text
upgrade: with op.batch_alter_table("products") as b: b.add_column(Column("slug", String(200), nullable=True))
         backfill: for id, name in SELECT: UPDATE products SET slug = :s WHERE id = :i  (s = "-".join(name.lower().split()))
         with op.batch_alter_table("products") as b: b.alter_column("slug", existing_type=String(200), nullable=False)
downgrade: batch drop_column("slug")
```
