## Hint 1

List the moments where the program could fail: while converting the rows, while writing the
file, between removing the old folder and putting the new one in place. After each failure, what
does a reader of `order_date=2024-06-01` see? Order your steps so that every failure leaves either
the old complete day or the new complete day, never nothing and never both.

## Hint 2

`os.replace(src, dst)` renames in one step. For folders, `dst` must not exist (on Windows), so
move the old folder away first.

```
write_day(rows, root, day):
    for each row: if utc date of created_at != day: raise ValueError
    folder = root / f"order_date={day}"
    if no rows: remove folder if it exists; return 0
    table = pa.Table.from_pylist(rows, schema=SCHEMA)        # fails here? old data untouched
    tmp = root / f".tmp-order_date={day}"   (clean it, create it)
    pq.write_table(table, tmp / "part-0.parquet")            # fails here? old data untouched
    old = root / f".old-order_date={day}"
    if folder exists: os.replace(folder, old)
    os.replace(tmp, folder)
    remove old
    return table.num_rows
```
