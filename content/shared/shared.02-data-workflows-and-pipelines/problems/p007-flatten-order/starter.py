from datetime import datetime, timezone
from decimal import Decimal


def flatten_order(order):
    """Return a new flat dict with typed, normalised values (see problem.md)."""
    raise NotImplementedError("build a new dict: id, email, city, status, amount, currency, times, item_count, total_qty")
