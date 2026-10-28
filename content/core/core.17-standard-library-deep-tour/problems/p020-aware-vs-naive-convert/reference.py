from datetime import datetime, timezone
from zoneinfo import ZoneInfo


def is_aware(dt: datetime) -> bool:
    return dt.tzinfo is not None and dt.utcoffset() is not None


def to_utc(naive_local: datetime, zone: str) -> datetime:
    if is_aware(naive_local):
        raise ValueError("to_utc expects a naive wall-clock time")
    return naive_local.replace(tzinfo=ZoneInfo(zone)).astimezone(timezone.utc)


def utc_to_local(moment: datetime, zone: str) -> datetime:
    if not is_aware(moment):
        raise ValueError("utc_to_local expects an aware datetime")
    return moment.astimezone(ZoneInfo(zone))


def same_instant(a: datetime, b: datetime) -> bool:
    if not (is_aware(a) and is_aware(b)):
        raise ValueError("cannot compare instants of naive datetimes")
    return a == b
