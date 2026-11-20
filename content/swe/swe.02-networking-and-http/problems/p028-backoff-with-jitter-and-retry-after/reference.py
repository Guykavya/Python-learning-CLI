import math
from datetime import timezone
from email.utils import parsedate_to_datetime


def delays(attempts, base, cap, rng):
    return [rng.uniform(0, min(cap, base * 2 ** i)) for i in range(attempts)]


def retry_after(header, now, cap=None):
    if header is None:
        return None
    value = header.strip()
    if value.isascii() and value.isdigit():
        seconds = int(value)
    else:
        try:
            when = parsedate_to_datetime(value)
        except (TypeError, ValueError):
            return None
        if when.tzinfo is None:
            when = when.replace(tzinfo=timezone.utc)
        seconds = max(0, (when - now).total_seconds())
    return min(seconds, cap) if cap is not None else seconds
