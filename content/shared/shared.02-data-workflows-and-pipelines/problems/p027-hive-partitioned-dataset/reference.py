from datetime import timezone
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

COLUMNS = ["id", "city", "status", "amount", "created_at"]

SCHEMA = pa.schema([
    pa.field("id", pa.int64(), nullable=False),
    pa.field("city", pa.string()),
    pa.field("status", pa.string(), nullable=False),
    pa.field("amount", pa.decimal128(10, 2), nullable=False),
    pa.field("created_at", pa.timestamp("us", tz="UTC"), nullable=False),
    pa.field("order_date", pa.string(), nullable=False),
])


def order_date(created_at):
    """The UTC calendar day of an aware datetime, as 'YYYY-MM-DD'."""
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
