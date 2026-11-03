## Approach

The day's folder is the unit of work. The run for that day replaces it as a whole, so the
result never depends on what was there before: running once or ten times gives the same folder.

The order of steps is what makes it safe:

1. **Check** every row belongs to the day (a row of 2 June in the 1 June folder would be counted
   on the wrong day forever).
2. **Build and write** the new data into a temporary folder. If the conversion or the write fails,
   nothing visible has changed yet.
3. **Swap**: move the current folder away, move the new folder in, delete the old one. The only
   window where the day is missing is between two renames, a few microseconds, instead of the
   whole time it takes to write the file.

Other days are never opened, so they cannot be damaged.

## Code

```python
import os
import shutil
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
])


def utc_day(created_at):
    return created_at.astimezone(timezone.utc).date().isoformat()


def write_day(rows, root, day):
    for row in rows:
        if utc_day(row["created_at"]) != day:
            raise ValueError(f"order {row['id']} belongs to {utc_day(row['created_at'])}, not {day}")

    root = Path(root)
    folder = root / f"order_date={day}"
    if not rows:
        shutil.rmtree(folder, ignore_errors=True)
        return 0

    table = pa.Table.from_pylist(rows, schema=SCHEMA)
    tmp = root / f".tmp-order_date={day}"
    shutil.rmtree(tmp, ignore_errors=True)
    tmp.mkdir(parents=True)
    pq.write_table(table, tmp / "part-0.parquet")

    old = root / f".old-order_date={day}"
    shutil.rmtree(old, ignore_errors=True)
    if folder.exists():
        os.replace(folder, old)
    os.replace(tmp, folder)
    shutil.rmtree(old, ignore_errors=True)
    return table.num_rows
```

## Complexity

O(rows of the day) to convert and write. The swap is two renames, O(1), whatever the size of
the data. The cost never depends on the size of the other partitions.

## Another way

pyarrow can do the replace itself:

```python
table = pa.Table.from_pylist([{**r, "order_date": day} for r in rows], schema=SCHEMA_WITH_DAY)
pq.write_to_dataset(table, root, partition_cols=["order_date"],
                    existing_data_behavior="delete_matching")
```

`delete_matching` deletes the files of each partition the table writes to, then writes the new
ones; partitions not in the table are left alone. It is shorter, but the old files are deleted
*before* the new file is complete, so a crash in the middle leaves the day empty. The rename
version keeps the last good data until the new data is ready. In SQL the same idea is
"`DELETE` the day, `INSERT` the day, inside one transaction".
