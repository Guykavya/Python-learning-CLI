# Parquet with an explicit schema

A Parquet file stores a **type** for every column. That is its big advantage over CSV: an
`int` comes back as an `int`, money comes back as an exact `Decimal`, a timestamp comes back as
a timestamp. But the types are only as good as the schema you write. If you let pyarrow
**guess** the schema from the data, it guesses from the values in *this* batch:

- a column whose values are all `None` today becomes type `null` (no real type at all);
- `Decimal("19.9")` becomes `decimal128(3, 1)` today and `decimal128(5, 2)` tomorrow;
- a datetime with a `+05:30` offset becomes `timestamp[us, tz=+05:30]`.

Two files from two days then have different schemas and do not combine cleanly. So a pipeline
writes Parquet with an **explicit** schema that never changes.

The rows are already-cleaned orders from the Pagebound Orders API (the transform step has run):

```python
{"id": 101, "city": "Pune", "status": "shipped",
 "amount": Decimal("19.99"),
 "created_at": datetime(2024, 6, 1, 10, 0, tzinfo=timezone.utc)}
```

## Your task

In `solution.py` write:

```python
def write_orders(rows: list[dict], path) -> int:
def read_orders(path) -> list[dict]:
```

`write_orders` writes `rows` to the Parquet file `path` with **exactly this schema** and returns
the number of rows written:

| column | pyarrow type | nullable |
|---|---|---|
| `id` | `pa.int64()` | no |
| `city` | `pa.string()` | yes |
| `status` | `pa.string()` | no |
| `amount` | `pa.decimal128(10, 2)` | no |
| `created_at` | `pa.timestamp("us", tz="UTC")` | no |

Rules:

- Use the schema even when `rows` is empty (the file then has 0 rows but the right columns).
- Create the parent folders of `path` if they do not exist.
- A **naive** datetime (no `tzinfo`) in `created_at` must raise `ValueError` *before* anything is
  written. (pyarrow would silently treat it as UTC, which is a guess, and a guess about time
  zones is a bug.) Aware datetimes in any offset are fine: pyarrow converts them to UTC.
- Let pyarrow's own errors through. For example a `Decimal("1.005")` cannot fit two decimal
  places, and pyarrow raises `pa.ArrowInvalid` instead of rounding your money. Good.

`read_orders` reads the file and returns a list of plain Python dicts (one per row, in file
order): `int`, `str` or `None`, `Decimal`, and aware `datetime` in UTC.

## Example

```python
from datetime import datetime, timedelta, timezone
from decimal import Decimal

ist = timezone(timedelta(hours=5, minutes=30))
rows = [
    {"id": 101, "city": "Pune", "status": "shipped", "amount": Decimal("19.9"),
     "created_at": datetime(2024, 6, 1, 10, 0, tzinfo=ist)},
    {"id": 102, "city": None, "status": "pending", "amount": Decimal("250"),
     "created_at": datetime(2024, 6, 1, 11, 0, tzinfo=timezone.utc)},
]
write_orders(rows, "out/orders.parquet")     # 2
back = read_orders("out/orders.parquet")
back[0]["amount"]                  # Decimal('19.90')   (two places, from the schema)
back[0]["created_at"].isoformat()  # '2024-06-01T04:30:00+00:00'   (same instant, now in UTC)
back[1]["city"]                    # None
```

`pq.read_schema("out/orders.parquet")` shows the five columns with exactly the types in the table.
