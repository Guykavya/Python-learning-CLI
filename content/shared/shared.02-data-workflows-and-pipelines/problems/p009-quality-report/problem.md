# A data-quality report for one batch

A schema check looks at **one** record. Many problems only show up when you look at the
**whole batch**: 40 % of the cities are empty today (yesterday it was 2 %), the same order id
appears twice, an amount is negative, or the newest order is three days old because the
source stopped updating. A data-quality report measures these things so a pipeline (or a
person) can decide whether to load the batch.

Write

```python
def quality_report(rows, columns, now, max_age=timedelta(hours=24),
                   amount_range=(Decimal("0"), Decimal("100000"))):
```

`rows` is a list of flat order rows (dicts) like the ones `flatten_order` builds:
`{"id": 1, "amount": Decimal("10.00"), "updated_at": datetime(..., tzinfo=timezone.utc), "city": "Pune", ...}`.
Any value can be `None`, and a key can be missing (count a missing key as `None`).
`now` is a timezone-aware `datetime` passed in by the caller; never call `datetime.now()`
yourself (the tests must be able to choose "now").

Return a dict with exactly these keys:

| key | value |
|---|---|
| `"rows"` | number of rows |
| `"null_rate"` | `{column: rate}` for every name in `columns`: the fraction of rows where that column is `None` or missing, rounded with `round(x, 3)`. With no rows, every rate is `0.0`. |
| `"duplicate_ids"` | sorted list of the ids that appear **more than once** (each id listed once; `None` ids are ignored here, they are counted by the null rate) |
| `"out_of_range"` | the `id` of every row whose `amount` is not `None` and is outside `amount_range` (both ends allowed), in row order |
| `"newest"` | the largest `updated_at` that is not `None`, or `None` if there is none |
| `"fresh"` | `True` if `newest` is not `None` and `now - newest <= max_age`, else `False` |

**Example**

```python
rows = [
    {"id": 1, "amount": Decimal("10.00"),   "updated_at": datetime(2024, 6, 1, 8, tzinfo=UTC),  "city": "Pune"},
    {"id": 2, "amount": None,               "updated_at": datetime(2024, 6, 1, 9, tzinfo=UTC),  "city": None},
    {"id": 2, "amount": Decimal("-5.00"),   "updated_at": None,                                 "city": "Goa"},
    {"id": 4, "amount": Decimal("250000"),  "updated_at": datetime(2024, 6, 1, 11, tzinfo=UTC)},
    {"id": 1, "amount": Decimal("0"),       "updated_at": datetime(2024, 5, 31, 23, tzinfo=UTC), "city": "Pune"},
]
quality_report(rows, ["id", "amount", "updated_at", "city"], now=datetime(2024, 6, 2, 10, tzinfo=UTC))
# {"rows": 5,
#  "null_rate": {"id": 0.0, "amount": 0.2, "updated_at": 0.2, "city": 0.4},
#  "duplicate_ids": [1, 2],
#  "out_of_range": [2, 4],
#  "newest": datetime(2024, 6, 1, 11, 0, tzinfo=UTC),
#  "fresh": True}            # 23 hours old, max_age is 24 hours
```

Row 4 has no `city` key, so it counts as a null city. `Decimal("0")` is inside the range
because both ends are allowed.
