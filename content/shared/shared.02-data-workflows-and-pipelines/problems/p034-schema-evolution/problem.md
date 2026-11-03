# Schema evolution: a new optional field from the API

On 1 July the Pagebound Orders API starts sending a new optional field, `coupon` (a string or
`null`), and a bit later `discount_cents`. Nobody told you in advance; the pipeline must cope. Its
data lives in two places:

- a SQLite table `orders` that was created months ago with the old columns;
- Parquet files: last month's files have the **old** schema, new files have the **new** one.

**Schema evolution** is the art of changing the shape of stored data without breaking what is
already there. The safe kind of change is **adding an optional column**: old rows simply have no
value (NULL) for it. In SQLite that is `ALTER TABLE orders ADD COLUMN coupon TEXT`; in Parquet you
read old and new files together and fill the missing column with nulls.

## Your task

In `solution.py` write three functions.

### `evolve_table(conn, table, rows) -> list[str]`

`conn` is a `sqlite3.Connection`, `table` an existing table name, `rows` a list of dicts.

- Find the keys of `rows` that are not yet columns of `table` (read the current columns with
  `PRAGMA table_info(<table>)`: the second item of each result row is the column name).
- The SQL type of a new column comes from its **first non-`None`** value in `rows`: `int` or `bool`
  -> `INTEGER`, `float` -> `REAL`, `str` -> `TEXT`. A column whose values are all `None` gets `TEXT`.
  Any other Python type (a list, a dict, a `Decimal`...) raises `TypeError` naming the column.
- Column and table names cannot be `?` parameters, so they go into the SQL text. Only names for
  which `str.isidentifier()` is true are allowed; otherwise raise `ValueError`.
- Check **all** names and types first; if anything is wrong, raise before changing the table.
- Add the columns with `ALTER TABLE ... ADD COLUMN`, commit, and return the names added, in the
  order they first appear (row by row, key by key). Calling it again adds nothing and returns `[]`.

### `load_rows(conn, table, rows) -> int`

Call `evolve_table` first, then upsert every row by `id` in one transaction: a new `id` is
inserted; an existing `id` is updated **only in the columns that row contains** (other columns keep
their values). Rows may have different keys. Return `len(rows)`. Loading the same rows twice must
not duplicate anything.

### `read_parquet_versions(paths) -> pa.Table`

Read the Parquet files (old first) into one table:

- the columns are the union of all files' columns, in the order they first appear;
- a column missing from a file is null for that file's rows (new columns in old files, and
  removed columns in new files);
- a column of type `null` (it was written with only missing values) fits any type;
- if two files give the same column **different** types (also `int32` vs `int64`), raise
  `ValueError` with the column name in the message: a type change is a decision for a person, not
  something to cast silently;
- an empty `paths` list raises `ValueError`.

`pa.unify_schemas([...])` computes the union (and raises `pa.ArrowTypeError` on a conflict);
`pa.concat_tables(tables, promote_options="default")` concatenates tables with different columns,
filling the gaps with nulls.

## Example

```python
conn.execute("CREATE TABLE orders (id INTEGER PRIMARY KEY, status TEXT, amount_cents INTEGER)")
conn.execute("INSERT INTO orders VALUES (1, 'pending', 1999)")

rows = [{"id": 3, "status": "shipped", "amount_cents": 700, "coupon": "JUNE10", "discount_cents": 70},
        {"id": 1, "status": "shipped"}]
evolve_table(conn, "orders", rows)     # ['coupon', 'discount_cents']   (TEXT, INTEGER)
load_rows(conn, "orders", rows)        # 2
conn.execute("SELECT * FROM orders ORDER BY id").fetchall()
# [(1, 'shipped', 1999, None, None), (3, 'shipped', 700, 'JUNE10', 70)]

# old.parquet: id, status, legacy_flag      new.parquet: id, status, coupon
read_parquet_versions(["old.parquet", "new.parquet"]).schema.names
# ['id', 'status', 'legacy_flag', 'coupon']
```
