## Approach

Writing: the partition key must be a column, so each row gets `order_date`, computed from the
UTC instant (the same order must land in the same folder whichever offset the API used).
`pq.write_to_dataset` groups the rows by that column, creates one `order_date=<value>` folder per
group and writes the other columns into a Parquet file inside it. The column itself is left out
of the files; the folder name *is* the value.

Reading one day: the cheapest read is the one that never touches the other days. The folder of a
day is known, so `pq.read_table(folder)` reads only the files inside it. Because those files do not
contain `order_date`, the rows already have exactly the five order columns.

## Code

```python
from datetime import timezone
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

SCHEMA = pa.schema([
    pa.field("id", pa.int64(), nullable=False),
    pa.field("city", pa.string()),
    pa.field("status", pa.string(), nullable=False),
    pa.field("amount", pa.decimal128(10, 2), nullable=False),
    pa.field("created_at", pa.timestamp("us", tz="UTC"), nullable=False),
    pa.field("order_date", pa.string(), nullable=False),
])


def order_date(created_at):
    return created_at.astimezone(timezone.utc).date().isoformat()


def write_partitioned(rows, root):
    if not rows:
        return []
    with_day = [{**row, "order_date": order_date(row["created_at"])} for row in rows]
    table = pa.Table.from_pylist(with_day, schema=SCHEMA)
    pq.write_to_dataset(table, root, partition_cols=["order_date"])
    return sorted({row["order_date"] for row in with_day})


def read_partition(root, day):
    folder = Path(root) / f"order_date={day}"
    if not folder.is_dir():
        return []
    rows = pq.read_table(folder).to_pylist()
    return sorted(rows, key=lambda row: row["id"])
```

## Complexity

Writing is O(n). Reading one day is O(rows of that day): the other folders are never opened.
That is the whole point of partitioning: the cost of a query depends on the data it needs, not on
the size of the dataset.

## Another way

Read the whole dataset with a filter and let pyarrow **prune** the partitions:

```python
table = pq.read_table(root, filters=[("order_date", "=", day)])
rows = table.drop_columns(["order_date"]).to_pylist()
```

pyarrow sees from the folder names that the other partitions cannot match and never opens their
files. This form scales better when the filter is a range (`("order_date", ">=", "2024-06-01")`)
or when there are several partition columns. You could also write each day yourself with
`pq.write_table(..., root / f"order_date={day}" / "part-0.parquet")`; the result is the same layout
with a predictable file name, which the next problem uses.
