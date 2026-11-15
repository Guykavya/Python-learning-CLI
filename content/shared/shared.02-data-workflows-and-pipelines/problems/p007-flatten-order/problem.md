# Flatten one order into a typed row

The API gives nested JSON with everything as text-ish values. A table (SQLite, CSV, Parquet)
wants **one flat row with real types**. That conversion is the "T" of ETL.

Write

```python
def flatten_order(order):
```

`order` is one order from the Pagebound Orders API:

```python
{"id": 101, "customer": {"email": " Asha@Example.com ", "city": "pune"}, "status": "Shipped",
 "amount": "19.99", "currency": "inr", "created_at": "2024-06-01T15:30:00+05:30",
 "updated_at": "2024-06-01T12:00:00Z", "items": [{"sku": "B1", "qty": 2}, {"sku": "C7", "qty": 1}]}
```

Return a **new** dict with exactly these keys:

| key | value |
|---|---|
| `id` | the id (an `int`, unchanged) |
| `email` | `customer.email`, stripped and lower-cased |
| `city` | `customer.city`, stripped and in title case (`"new delhi"` -> `"New Delhi"`); `None` if it is `null` or blank |
| `status` | stripped and lower-cased |
| `amount` | a `decimal.Decimal` made from the string (never a `float`) |
| `currency` | stripped and upper-cased |
| `created_at`, `updated_at` | timezone-aware `datetime` objects **converted to UTC** |
| `item_count` | how many item lines there are |
| `total_qty` | the sum of `qty` over the items |

- Parse timestamps with `datetime.fromisoformat` (it understands `Z` and offsets such as
  `+05:30`), then convert with `.astimezone(timezone.utc)`.
- A timestamp **without** an offset (`"2024-06-01T10:00:00"`) is ambiguous: is it Indian time or
  UTC? Raise `ValueError` (with the field name in the message) instead of guessing.
- Do not change the input dict.

You may assume every key is present and the values have the right JSON types; checking that
is the next problem's job.

**Example** (for the order above)

```python
{"id": 101, "email": "asha@example.com", "city": "Pune", "status": "shipped",
 "amount": Decimal("19.99"), "currency": "INR",
 "created_at": datetime(2024, 6, 1, 10, 0, tzinfo=timezone.utc),
 "updated_at": datetime(2024, 6, 1, 12, 0, tzinfo=timezone.utc),
 "item_count": 2, "total_qty": 3}
```

`15:30+05:30` is the same moment as `10:00` UTC.
