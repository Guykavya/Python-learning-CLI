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
