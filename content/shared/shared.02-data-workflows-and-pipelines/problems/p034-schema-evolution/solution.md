## Approach

**SQLite.** Adding an optional column is the one schema change that cannot break existing
readers: `SELECT id, status FROM orders` still works, and old rows read NULL in the new column.
`evolve_table` asks the database what it has *now* (`PRAGMA table_info`), so it is idempotent: a
re-run, or a second batch with the same new field, finds the column already there.

Identifiers (table and column names) cannot be bound with `?`, so the only safe way to put a
name from the data into SQL is to allow nothing but plain identifiers. All checks run before the
first `ALTER TABLE`, so a bad batch leaves the table exactly as it was.

`load_rows` upserts with only the columns each row has. `INSERT OR REPLACE` would be wrong: it
deletes the old row and inserts a new one, so every column the row did not mention becomes NULL.

**Parquet.** Old files cannot be changed cheaply (and should not be: they are a record of what
was written). Instead the *reader* evolves: `pa.unify_schemas` computes the union of the columns
(null-typed columns take the other file's type) and refuses incompatible types;
`pa.concat_tables(..., promote_options="default")` fills the missing columns with nulls.
Turning pyarrow's `ArrowTypeError` into a `ValueError` with the column name gives the operator
a clear message.

## Code

```python
import pyarrow as pa
import pyarrow.parquet as pq

SQL_TYPES = {bool: "INTEGER", int: "INTEGER", float: "REAL", str: "TEXT"}


def check_name(name):
    if not isinstance(name, str) or not name.isidentifier():
        raise ValueError(f"not a safe column or table name: {name!r}")


def existing_columns(conn, table):
    check_name(table)
    return [row[1] for row in conn.execute(f"PRAGMA table_info({table})")]


def sql_type(values, name):
    for value in values:
        if value is not None:
            if type(value) not in SQL_TYPES:
                raise TypeError(f"column {name}: cannot store {type(value).__name__}")
            return SQL_TYPES[type(value)]
    return "TEXT"


def evolve_table(conn, table, rows):
    have = existing_columns(conn, table)
    new = []
    for row in rows:
        for name in row:
            if name not in have and name not in new:
                new.append(name)
    plan = []
    for name in new:
        check_name(name)
        plan.append((name, sql_type([row.get(name) for row in rows], name)))
    for name, kind in plan:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {name} {kind}")
    conn.commit()
    return new


def load_rows(conn, table, rows):
    evolve_table(conn, table, rows)
    with conn:
        for row in rows:
            names = list(row)
            placeholders = ", ".join("?" for _ in names)
            updates = ", ".join(f"{n} = excluded.{n}" for n in names if n != "id")
            sql = f"INSERT INTO {table} ({', '.join(names)}) VALUES ({placeholders})"
            sql += f" ON CONFLICT(id) DO UPDATE SET {updates}" if updates else " ON CONFLICT(id) DO NOTHING"
            conn.execute(sql, [row[n] for n in names])
    return len(rows)


def read_parquet_versions(paths):
    if not paths:
        raise ValueError("no files to read")
    tables = [pq.read_table(path) for path in paths]
    try:
        pa.unify_schemas([t.schema for t in tables])
    except (pa.ArrowTypeError, pa.ArrowInvalid) as error:
        raise ValueError(f"files disagree on a column type: {error}") from error
    return pa.concat_tables(tables, promote_options="default")
```

## Complexity

`evolve_table`: O(rows x keys) to find the new columns; each `ALTER TABLE ADD COLUMN` in SQLite
only changes the schema, it does not rewrite the rows, so it is fast even on a big table.
`load_rows`: O(rows) statements. `read_parquet_versions`: O(total rows) to read and concatenate.

## Another way

Build the unified schema yourself: walk the fields of every file, remember the first real type of
each name, raise on a different non-null type; then for each table build the columns in the
unified order with `pa.nulls(num_rows, type)` for the missing ones and `column.cast(type)` for
null-typed ones, and `pa.concat_tables` the results. With `pyarrow.dataset` you can also pass the
unified schema directly: `ds.dataset(paths, schema=unified).to_table()` reads every file as if it
had that schema. Renaming a column is a harder change: you add the new name, copy the values
(`UPDATE orders SET new = old`), switch the readers, and only then drop the old name.
