# Add a column and backfill it

Chapter sections 13.5 and 13.6. The table `products(id, name)` already exists and holds rows. You want a new column `slug` (a URL-friendly name) that is **NOT NULL**. You cannot add a `NOT NULL` column to a table with rows without giving the existing rows a value, so a safe migration has **three steps in one revision**:

1. add the column as **nullable**;
2. **backfill**: fill it for every existing row from `name` (a data migration);
3. make it **NOT NULL**.

Write the two functions of revision `0002`:

```python
upgrade_0002()
downgrade_0002()
```

Rules:

- `slug` is `String(200)`.
- The backfill: lower-case the name, trim it, and replace every run of white space by one `-`: `"Green Tea"` becomes `"green-tea"`, `"  Big   Mug "` becomes `"big-mug"`. Use the connection from `op.get_bind()`, read the rows and update them (Python code is fine for the slug, SQL for the update).
- SQLite cannot change a column's nullability with `ALTER`; use **batch mode**: `with op.batch_alter_table("products") as batch: batch.alter_column("slug", existing_type=sa.String(200), nullable=False)`.
- `downgrade_0002` removes the column (batch mode again) and keeps all other data.

The tests create revision `0001` themselves (the table with 3 rows), run `upgrade 0001`, then your `0002`.
