## Approach

The schema is the contract of the file, so it is written once, at module level, and used for
every write. `pa.Table.from_pylist(rows, schema=ORDER_SCHEMA)` converts each Python value into the
declared type:

- `Decimal("19.9")` becomes a `decimal128(10, 2)` value `19.90`. A value that would need more
  places (`1.005`) raises `ArrowInvalid`: pyarrow refuses to lose money silently.
- An aware datetime is converted to the UTC instant; the column remembers `tz="UTC"`.
- `None` in `city` is a null in a **string** column, even if the whole batch is `None`.
- `nullable=False` makes `pq.write_table` refuse a null `id`.

The one thing pyarrow does *not* check is a naive datetime: it stores it as if it were UTC. So the
function checks that itself, before writing, so that a bad batch leaves no file behind.

`to_pylist()` turns the columns back into one dict per row with Python types.

## Code

```python
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

ORDER_SCHEMA = pa.schema([
    pa.field("id", pa.int64(), nullable=False),
    pa.field("city", pa.string()),
    pa.field("status", pa.string(), nullable=False),
    pa.field("amount", pa.decimal128(10, 2), nullable=False),
    pa.field("created_at", pa.timestamp("us", tz="UTC"), nullable=False),
])


def write_orders(rows, path):
    for row in rows:
        created = row["created_at"]
        if created is not None and created.tzinfo is None:
            raise ValueError(f"order {row.get('id')}: created_at {created} has no time zone")
    table = pa.Table.from_pylist(rows, schema=ORDER_SCHEMA)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(table, path)
    return table.num_rows


def read_orders(path):
    return pq.read_table(path).to_pylist()
```

## Complexity

O(n) time and memory for n rows: every value is converted once. The file is columnar and
compressed, so it is usually much smaller than the same data as CSV.

## Another way

Build the table column by column: `pa.table({"id": [r["id"] for r in rows], ...}, schema=ORDER_SCHEMA)`.
That is the natural shape when your data is already in columns. You can also pass the schema to
`pq.ParquetWriter(path, ORDER_SCHEMA)` and write several batches into one file; the writer then
rejects any batch whose schema differs, which is a useful guard in a long-running job.
