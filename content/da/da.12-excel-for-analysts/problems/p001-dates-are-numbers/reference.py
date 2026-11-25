from datetime import date, datetime, timedelta

EPOCH = datetime(1899, 12, 30)


def to_serial(d):
    if not isinstance(d, datetime):
        d = datetime(d.year, d.month, d.day)
    return (d - EPOCH).total_seconds() / 86400


def from_serial(n):
    return EPOCH + timedelta(days=float(n))
