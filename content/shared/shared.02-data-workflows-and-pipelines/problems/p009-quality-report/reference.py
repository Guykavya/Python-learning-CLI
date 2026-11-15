from collections import Counter
from datetime import timedelta
from decimal import Decimal


def quality_report(rows, columns, now, max_age=timedelta(hours=24),
                   amount_range=(Decimal("0"), Decimal("100000"))):
    """Batch checks: null rate per column, duplicate ids, out-of-range amounts, freshness."""
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
