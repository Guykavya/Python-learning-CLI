## Hint 1

`pq.write_to_dataset` needs the partition value as a **column** of the table, so first give each
row an `order_date`. How do you get the UTC date of an aware datetime? (`astimezone(timezone.utc)`
first, then `.date().isoformat()`.) Why is `created_at.date()` alone wrong for order 104?

## Hint 2

For reading, think about where one day's data lives on disk. You know the folder name exactly,
so you can hand that folder to `pq.read_table`. Its files do not contain `order_date`, which is
exactly the five columns you must return.

```
write_partitioned(rows, root):
    if no rows: return []
    rows2 = [row plus order_date = utc day of created_at, for each row]
    table = pa.Table.from_pylist(rows2, schema=SCHEMA_WITH_ORDER_DATE)
    pq.write_to_dataset(table, root, partition_cols=["order_date"])
    return sorted(set of the days)

read_partition(root, day):
    folder = Path(root) / f"order_date={day}"
    if folder is not a directory: return []
    return sorted(pq.read_table(folder).to_pylist(), by id)
```
