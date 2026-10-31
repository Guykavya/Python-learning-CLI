from datetime import datetime, timezone
from zoneinfo import ZoneInfo


def is_aware(dt: datetime) -> bool:
    return False


def to_utc(naive_local: datetime, zone: str) -> datetime:
    return naive_local


def utc_to_local(moment: datetime, zone: str) -> datetime:
    return moment


def same_instant(a: datetime, b: datetime) -> bool:
    return False
