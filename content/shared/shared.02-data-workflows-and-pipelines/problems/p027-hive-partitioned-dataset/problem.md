# Write a dataset partitioned by order date

Most questions about orders are about a time range: "yesterday's revenue", "June's cancellations".
If all orders sit in one big file, every question reads all of it. **Partitioning** splits the
data into folders by a column, so a reader can skip whole folders it does not need. The common
layout, called **hive style**, names each folder `column=value`:

```
orders/
    order_date=2024-06-01/
        3f9c...-0.parquet
    order_date=2024-06-02/
        3f9c...-0.parquet
```

The partition value is stored **once**, in the folder name, not in every row of the files.
pyarrow (and Spark, DuckDB, Athena, BigQuery...) turn the folder name back into a column when
they read the whole dataset.

The rows are cleaned Pagebound orders:

```python
{"id": 101, "city": "Pune", "status": "shipped", "amount": Decimal("19.99"),
 "created_at": datetime(2024, 6, 1, 10, 0, tzinfo=timezone.utc)}
```

## Your task

In `solution.py` write:

```python
def write_partitioned(rows: list[dict], root) -> list[str]:
def read_partition(root, day: str) -> list[dict]:
```

`write_partitioned`:

- The order day is the **UTC** calendar date of `created_at`, as `"YYYY-MM-DD"`. `created_at` is
  always aware but may have any offset; an order created at 01:30 on 2 June in India (`+05:30`) is
  20:00 on **1 June** in UTC.
- Write all rows under `root`, partitioned hive style by `order_date`. `pq.write_to_dataset(table,
  root, partition_cols=["order_date"])` does exactly this.
- Use an explicit schema for the table: `id` int64, `city` string, `status` string, `amount`
  decimal128(10, 2), `created_at` timestamp("us", tz="UTC"), plus `order_date` string.
- Return the sorted list of distinct days written. An empty `rows` returns `[]` and creates no
  partition folder.
- `root` is empty or does not exist yet (re-writing a day is the next problem).

`read_partition`:

- Return the rows of **one** day as dicts with the five order columns (`id`, `city`, `status`,
  `amount`, `created_at`; no `order_date`), sorted by `id`.
- Read only that day's files: never open files in other partitions. Either read the folder
  `root / f"order_date={day}"` directly, or read `root` with a filter on `order_date` so pyarrow
  skips the other folders.
- A day with no folder returns `[]`.

## Example

```python
rows = [
    {"id": 101, "city": "Pune", "status": "shipped", "amount": Decimal("19.99"),
     "created_at": datetime(2024, 6, 1, 10, 0, tzinfo=timezone.utc)},
    {"id": 103, "city": "Delhi", "status": "shipped", "amount": Decimal("10.00"),
     "created_at": datetime(2024, 6, 2, 9, 0, tzinfo=timezone.utc)},
    {"id": 104, "city": "Pune", "status": "cancelled", "amount": Decimal("0.00"),
     "created_at": datetime(2024, 6, 2, 1, 30, tzinfo=timezone(timedelta(hours=5, minutes=30)))},
]
write_partitioned(rows, "lake/orders")      # ['2024-06-01', '2024-06-02']
[r["id"] for r in read_partition("lake/orders", "2024-06-01")]   # [101, 104]
read_partition("lake/orders", "2024-07-01")                        # []
```
