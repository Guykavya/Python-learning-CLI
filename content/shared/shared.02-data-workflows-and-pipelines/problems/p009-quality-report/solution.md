## Approach

Every part of the report is one small aggregate over the batch:

- **Null rate.** `row.get(column) is None` is true both for a `None` value and a missing key,
  which is exactly what we want to count. Divide by the row count, but guard the empty batch.
  `is None` (not truthiness) keeps `0` and `""` as real values.
- **Uniqueness.** `Counter` counts each id; the duplicates are the ids with a count above 1.
  `None` ids are left out, otherwise every row without an id would look like "duplicate id None".
- **Range.** A chained comparison `low <= amount <= high` includes both ends. A `None` amount is
  a null problem, not a range problem, so it is skipped here (and already shows in the null rate).
- **Freshness.** The age of the batch is the age of its **newest** row. `now` comes from the
  caller, so the tests (and a re-run of last Tuesday's job) can choose the moment. Both `now` and
  the timestamps are aware, so the subtraction is correct across time zones.

The report does not decide anything. A later step compares it with thresholds ("abort if the
city null rate is above 10 %") or with yesterday's report. Keeping measuring and deciding
apart makes both easy to test.

## Code

```python
from collections import Counter
from datetime import timedelta
from decimal import Decimal


def quality_report(rows, columns, now, max_age=timedelta(hours=24),
                   amount_range=(Decimal("0"), Decimal("100000"))):
    n = len(rows)
    null_rate = {}
    for column in columns:
        nulls = sum(1 for row in rows if row.get(column) is None)
        null_rate[column] = round(nulls / n, 3) if n else 0.0

    id_counts = Counter(row.get("id") for row in rows if row.get("id") is not None)
    duplicate_ids = sorted(i for i, count in id_counts.items() if count > 1)

    low, high = amount_range
    out_of_range = [row.get("id") for row in rows
                    if row.get("amount") is not None and not low <= row["amount"] <= high]

    times = [row["updated_at"] for row in rows if row.get("updated_at") is not None]
    newest = max(times) if times else None
    fresh = newest is not None and now - newest <= max_age

    return {"rows": n, "null_rate": null_rate, "duplicate_ids": duplicate_ids,
            "out_of_range": out_of_range, "newest": newest, "fresh": fresh}
```

## Complexity

O(n * c) for `n` rows and `c` columns (one pass per column for the null rates), O(n) for the
rest. A single pass that updates all counters at once is also O(n * c), just with one loop.

## Another way

The same report in SQL, once the batch is in a staging table:

```sql
SELECT COUNT(*)                                     AS rows,
       ROUND(AVG(city IS NULL), 3)                  AS city_null_rate,
       SUM(amount < 0 OR amount > 100000)           AS out_of_range,
       MAX(updated_at)                              AS newest
FROM stg_orders;
SELECT id FROM stg_orders WHERE id IS NOT NULL GROUP BY id HAVING COUNT(*) > 1 ORDER BY id;
```

`AVG(city IS NULL)` works because a comparison in SQLite is `0` or `1`. Tools like Great
Expectations or dbt tests run exactly these queries and compare the results with thresholds.
