## Hint 1

Where does the column type come from when you call `pa.Table.from_pylist(rows)` with no other
argument? What will it guess for `city` if every row has `city=None`? Which argument of
`from_pylist` lets you hand over the types yourself? A `pa.field(name, type, nullable=False)` is
how you say "this column may never be null".

## Hint 2

pyarrow does not complain about a naive datetime, so you must check first, in plain Python,
before anything touches the disk.

```
SCHEMA = pa.schema([pa.field("id", pa.int64(), nullable=False), ... five fields ...])

write_orders(rows, path):
    for each row:
        if row["created_at"].tzinfo is None: raise ValueError(...)
    table = pa.Table.from_pylist(rows, schema=SCHEMA)
    make the parent folder of path
    pq.write_table(table, path)
    return table.num_rows

read_orders(path):
    return pq.read_table(path).to_pylist()
```
