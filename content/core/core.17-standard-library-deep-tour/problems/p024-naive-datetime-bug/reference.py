"""Shift log for a hospital that has wards in several cities (fixed version)."""
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

FMT = "%Y-%m-%d %H:%M"
UTC = timezone.utc


def parse_local(text: str, zone: str) -> datetime:
    naive = datetime.strptime(text, FMT)
    tz = ZoneInfo(zone)
    local = naive.replace(tzinfo=tz)              # attach the zone: same wall time, now aware
    back = local.astimezone(UTC).astimezone(tz)    # a skipped time comes back different
    if back.replace(tzinfo=None) != naive:
        raise ValueError(f"{text} does not exist in {zone}: the clocks jumped over it")
    return local


def to_utc_iso(text: str, zone: str) -> str:
    return parse_local(text, zone).astimezone(UTC).isoformat()


def shift_hours(start_text: str, end_text: str, zone: str) -> float:
    start = parse_local(start_text, zone).astimezone(UTC)
    end = parse_local(end_text, zone).astimezone(UTC)
    return (end - start).total_seconds() / 3600


def is_overdue(due_iso: str, now: datetime) -> bool:
    due = datetime.fromisoformat(due_iso)
    if due.tzinfo is None or now.tzinfo is None:
        raise ValueError("both times must be aware (have a UTC offset)")
    return now > due
