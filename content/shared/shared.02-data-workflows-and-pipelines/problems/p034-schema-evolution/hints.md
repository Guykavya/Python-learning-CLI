## Hint 1

Split `evolve_table` into a **plan** and an **act** phase. The plan: which keys are new (compare
with `PRAGMA table_info`, not with a list you remember from last time), and what SQL type each
one gets (skip the `None` values). Only when the whole plan is valid, run the `ALTER TABLE`
statements. Why does that order matter if the third name in the plan is unsafe?

For `load_rows`, you know `INSERT ... ON CONFLICT(id) DO UPDATE SET col = excluded.col` from
shared.01. Which columns should appear after `SET` when a row has only `id` and `status`?

## Hint 2

```
evolve_table(conn, table, rows):
    have = [r[1] for r in conn.execute(f"PRAGMA table_info({table})")]   # table checked with isidentifier
    new  = keys of rows, in first-seen order, not in have
    plan = []
    for name in new:
        if not name.isidentifier(): raise ValueError
        first = first value of rows[i].get(name) that is not None
        type  = INTEGER / REAL / TEXT by type(first), TEXT if none, else TypeError
        plan.append((name, type))
    for name, type in plan: ALTER TABLE {table} ADD COLUMN {name} {type}
    commit; return new

load_rows: evolve_table, then `with conn:` for each row:
    INSERT INTO t (cols) VALUES (?, ...) ON CONFLICT(id) DO UPDATE SET c = excluded.c  (cols except id)

read_parquet_versions(paths):
    if not paths: raise ValueError
    tables = [pq.read_table(p) for p in paths]
    try: pa.unify_schemas([t.schema for t in tables])
    except pa.ArrowTypeError as e: raise ValueError(...) from e     # message names the column
    return pa.concat_tables(tables, promote_options="default")
```
