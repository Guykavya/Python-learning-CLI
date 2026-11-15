# Trace: CSV round trip vs Parquet round trip

A CSV file is text. It has no idea what a number, a missing value, a boolean or a decimal is:
everything you write becomes characters, and everything `csv.DictReader` gives back is a `str`.
A Parquet file stores a type for every column, so values come back as the types they went in as.

The program below writes **one** order row both ways and reads it back. Work out, line by line,
exactly what it prints. Write one line per `print` call, with the same spacing and quotes that
`print` would give. The program needs no input and no network.

Two reminders:

- `csv.DictWriter` writes `None` as an empty field and every other value as `str(value)`.
- `str()` of an aware `datetime` uses a space between date and time; `.isoformat()` uses a `T`.

```python
import csv
import io
import tempfile
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

row = {
    "id": 7,
    "zip": "007",
    "city": None,
    "amount": Decimal("19.90"),
    "paid": False,
    "created_at": datetime(2024, 6, 1, 10, 0, tzinfo=timezone.utc),
}

buffer = io.StringIO()
writer = csv.DictWriter(buffer, fieldnames=list(row))
writer.writeheader()
writer.writerow(row)
print(buffer.getvalue().splitlines()[1])

buffer.seek(0)
back = next(csv.DictReader(buffer))
for name in ("id", "city", "amount", "paid"):
    print(name, repr(back[name]), type(back[name]).__name__)
print("paid?", "yes" if back["paid"] else "no")
print(back["id"] + back["zip"])

schema = pa.schema([
    ("id", pa.int64()), ("zip", pa.string()), ("city", pa.string()),
    ("amount", pa.decimal128(8, 2)), ("paid", pa.bool_()),
    ("created_at", pa.timestamp("us", tz="UTC")),
])
with tempfile.TemporaryDirectory() as tmp:
    path = Path(tmp) / "row.parquet"
    pq.write_table(pa.Table.from_pylist([row], schema=schema), path)
    table = pq.read_table(path)
    got = table.to_pylist()[0]
print(table.num_columns, table.num_rows)
for name in ("id", "zip", "city", "amount", "paid"):
    print(name, repr(got[name]), type(got[name]).__name__)
print("paid?", "yes" if got["paid"] else "no")
print(got["id"] + 1, got["amount"] * 2)
print(got["created_at"].isoformat(), got["created_at"] == row["created_at"])
print(table.schema.field("amount").type, table.schema.field("created_at").type)
```

Write your answer in `answer.txt`, one output line per `print`.

**Example (a different program)**

```python
import csv, io

buffer = io.StringIO()
csv.writer(buffer).writerow([3, None, 2.5])
buffer.seek(0)
print(next(csv.reader(buffer)))
```

prints

```
['3', '', '2.5']
```
