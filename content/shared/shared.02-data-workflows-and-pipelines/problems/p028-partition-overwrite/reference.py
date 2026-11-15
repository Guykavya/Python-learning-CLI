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

    # 1. Build and write the new data somewhere else first. If this fails, the old day is untouched.
    table = pa.Table.from_pylist(rows, schema=SCHEMA)
    tmp = root / f".tmp-order_date={day}"
    shutil.rmtree(tmp, ignore_errors=True)
    tmp.mkdir(parents=True)
    pq.write_table(table, tmp / "part-0.parquet")

    # 2. Swap: move the old folder away, move the new one in, then delete the old one.
    old = root / f".old-order_date={day}"
    shutil.rmtree(old, ignore_errors=True)
    if folder.exists():
        os.replace(folder, old)
    os.replace(tmp, folder)
    shutil.rmtree(old, ignore_errors=True)
    return table.num_rows
