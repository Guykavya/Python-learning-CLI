from collections import Counter
from datetime import timedelta
from decimal import Decimal


def quality_report(rows, columns, now, max_age=timedelta(hours=24),
                   amount_range=(Decimal("0"), Decimal("100000"))):
    """Batch checks: null rate per column, duplicate ids, out-of-range amounts, freshness."""
    raise NotImplementedError("one pass for nulls, a Counter for ids, then max(updated_at)")
